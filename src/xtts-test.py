from TTS.api import TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cuda')

tts.tts_to_file(
    text=' The stale smell of old beer lingers. It takes heat to bring out the odor. A cold dip restores health and zest. A salt pickle tastes fine with ham. Tacos al pastor are my favorite. A zestful food is the hot cross bun.',
    speaker_wav='harv-test.wav',
    language='en',
    file_path='xtts_harv-test_output.wav'
)
print('synthesis complete')