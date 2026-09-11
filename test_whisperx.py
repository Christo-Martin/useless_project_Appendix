import whisperx

device = 'cuda'
audio = whisperx.load_audio('harv-test.wav')
model = whisperx.load_model('small', device, compute_type='float16')
result = model.transcribe(audio, batch_size=8)
print('detected language:', result['language'])
print('segments:', result['segments'])

align_model, metadata = whisperx.load_align_model(language_code=result['language'], device=device)
result = whisperx.align(result['segments'], align_model, metadata, audio, device)

print('word-level output:')
for w in result['segments'][0]['words']:
    print(w)