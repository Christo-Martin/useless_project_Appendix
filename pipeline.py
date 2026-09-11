import os
import numpy as np
import soundfile as sf
import librosa
from TTS.api import TTS

from align import align_audio
from gibberish import gibberish_for_segment

SOURCE_AUDIO = 'test.wav'
OUTPUT_AUDIO = 'dubbed_output.wav'
DEVICE = 'cuda'
TEMP_DIR = 'temp_segments'


def main():
    os.makedirs(TEMP_DIR, exist_ok=True)

    print("Step 1: Aligning original audio...")
    segments, language = align_audio(SOURCE_AUDIO, device=DEVICE)

    print("Step 2: Loading XTTS...")
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(DEVICE)

    # total duration of the original file, to size our output buffer
    orig_audio, sr = librosa.load(SOURCE_AUDIO, sr=None)
    total_samples = len(orig_audio)
    final_track = np.zeros(total_samples, dtype=np.float32)

    for i, seg in enumerate(segments):
        original_text = seg['text']
        start_time = float(seg['start'])
        end_time = float(seg['end'])
        target_duration = end_time - start_time

        if target_duration <= 0.05:
            continue  # skip near-empty segments

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

        # load synthesized clip, stretch to match target duration
        synth_audio, synth_sr = librosa.load(raw_path, sr=sr)
        synth_duration = len(synth_audio) / synth_sr

        if synth_duration <= 0:
            continue

        rate = synth_duration / target_duration  # >1 = need to speed up
        rate = max(0.5, min(rate, 2.5))  # clamp to sane stretch bounds

        stretched = librosa.effects.time_stretch(synth_audio, rate=rate)

        # place into final track at the right position, trim/pad as needed
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