import os
import json
import numpy as np
import soundfile as sf
import librosa
from TTS.api import TTS

from gibberish import gibberish_for_segment

SOURCE_AUDIO = '../test_audios/harv-test.wav'
INPUT_JSON = '../aligned_segments.json'
OUTPUT_AUDIO = '../output_audios/dubbed_output.wav'
DEVICE = 'cuda'
TEMP_DIR = 'temp_segments'


def synthesize(
    source_audio_path: str = SOURCE_AUDIO,
    aligned_json_path: str = INPUT_JSON,
    output_path: str = OUTPUT_AUDIO,
    device: str = DEVICE,
    temp_dir: str = TEMP_DIR,
    level: int = 3,
) -> str:
    """Callable entry-point used by server.py.

    Args:
        source_audio_path: WAV used as XTTS speaker reference.
        aligned_json_path: JSON produced by run_align.py.
        output_path:       Destination WAV.
        device:            'cuda' or 'cpu'.
        temp_dir:          Scratch dir for per-segment WAVs.
        level:             Meaning-destruction level 1-5 (slider value).

    Returns:
        Absolute path of the written output file.
    """
    main(
        source_audio=source_audio_path,
        input_json=aligned_json_path,
        output_audio=output_path,
        device=device,
        temp_dir=temp_dir,
        level=level,
    )
    return os.path.abspath(output_path)


def main(
    source_audio: str = SOURCE_AUDIO,
    input_json: str = INPUT_JSON,
    output_audio: str = OUTPUT_AUDIO,
    device: str = DEVICE,
    temp_dir: str = TEMP_DIR,
    level: int = 3,
):
    os.makedirs(temp_dir, exist_ok=True)

    with open(input_json, 'r') as f:
        data = json.load(f)
    segments = data['segments']
    language = data['language']

    print(f"Loading XTTS... (level={level})")
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)

    orig_audio, sr = librosa.load(source_audio, sr=None)
    total_samples = len(orig_audio)
    final_track = np.zeros(total_samples, dtype=np.float32)

    for i, seg in enumerate(segments):
        original_text = seg['text']
        start_time = seg['start']
        end_time = seg['end']
        target_duration = end_time - start_time

        if target_duration <= 0.05:
            continue

        # Pass the slider level to the gibberish generator
        gibberish_text = gibberish_for_segment(original_text, level=level)
        print(f"\nSegment {i}: [{start_time:.2f}-{end_time:.2f}] "
              f"({target_duration:.2f}s) [level {level}]")
        print(f"  Original:  {original_text}")
        print(f"  Gibberish: {gibberish_text}")

        raw_path = os.path.join(temp_dir, f'seg_{i}_raw.wav')
        tts.tts_to_file(
            text=gibberish_text,
            speaker_wav=source_audio,
            language=language,
            file_path=raw_path
        )

        synth_audio, synth_sr = librosa.load(raw_path, sr=sr)
        synth_duration = len(synth_audio) / synth_sr

        if synth_duration <= 0:
            continue

        rate = synth_duration / target_duration
        rate = max(0.5, min(rate, 2.5))

        stretched = librosa.effects.time_stretch(synth_audio, rate=rate)

        start_sample = int(start_time * sr)
        end_sample = start_sample + len(stretched)

        if end_sample > total_samples:
            stretched = stretched[: total_samples - start_sample]
            end_sample = total_samples

        final_track[start_sample:end_sample] = stretched

    sf.write(output_audio, final_track, sr)
    print(f"\nDone. Output written to {output_audio}")


if __name__ == '__main__':
    main()