import librosa, soundfile as sf
y, sr = librosa.load('harv-test.wav', sr=16000)
y_stretched = librosa.effects.time_stretch(y, rate=1.2)
sf.write('harv-test_stretched.wav', y_stretched, sr)
print('original duration:', len(y)/sr)
print('stretched duration:', len(y_stretched)/sr)