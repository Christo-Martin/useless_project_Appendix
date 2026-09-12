import whisperx
import torch
import gc

def align_audio(audio_path: str, device: str = 'cuda', model_size: str = 'small'):
    audio = whisperx.load_audio(audio_path)
    model = whisperx.load_model(model_size, device, compute_type='float16')
    result = model.transcribe(audio, batch_size=8)

    language = result['language']

    align_model, metadata = whisperx.load_align_model(
        language_code=language, device=device
    )
    result = whisperx.align(
        result['segments'], align_model, metadata, audio, device
    )

    # explicitly free GPU memory used by whisper + align models
    del model
    del align_model
    torch.cuda.empty_cache()
    gc.collect()

    return result['segments'], language

if __name__ == '__main__':
    segments, lang = align_audio('../test_audios/harv-test.wav')
    print(f"Language: {lang}")
    for seg in segments:
        print(f"[{seg['start']:.2f}-{seg['end']:.2f}] {seg['text']}")