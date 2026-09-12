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


def main():
    os.makedirs(TEMP_DIR, exist_ok=True)

    with open(INPUT_JSON, 'r') as f:
        data = json.load(f)
    segments = data['segments']
    language = data['language']

    print("Loading XTTS...")
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(DEVICE)

    orig_audio, sr = librosa.load(SOURCE_AUDIO, sr=None)
    total_samples = len(orig_audio)
    final_track = np.zeros(total_samples, dtype=np.float32)

    for i, seg in enumerate(segments):
        original_text = seg['text']
        start_time = seg['start']
        end_time = seg['end']
        target_duration = end_time - start_time

        if target_duration <= 0.05:
            continue

        gibberish_text = gibberish_for_segment(original_text)
        print(f"\nSegment {i}: [{start_time:.2f}-{end_time:.2f}] "
              f"({target_duration:.2f}s)")
        print(f"  Original:  {original_text}")
        print(f"  Gibberish: {gibberish_text}")

        raw_path = os.path.join(TEMP_DIR, f'seg_{i}_raw.wav')
        tts.tts_to_file(
            text=gibberish_text,
            speaker_wav=SOURCE_AUDIO,
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

    sf.write(OUTPUT_AUDIO, final_track, sr)
    print(f"\nDone. Output written to {OUTPUT_AUDIO}")


if __name__ == '__main__':
    main()