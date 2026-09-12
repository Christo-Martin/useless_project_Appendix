import json
from align import align_audio


SOURCE_AUDIO = '../test_audios/harv-test.wav'
OUTPUT_JSON = '../aligned_segments.json'

segments, language = align_audio(SOURCE_AUDIO, device='cuda')

# convert numpy floats to plain floats for JSO  N serialization
clean_segments = []
for seg in segments:
    clean_segments.append({
        'text': seg['text'],
        'start': float(seg['start']),
        'end': float(seg['end']),
    })

with open(OUTPUT_JSON, 'w') as f:
    json.dump({'language': language, 'segments': clean_segments}, f, indent=2)

print(f"Saved {len(clean_segments)} segments to {OUTPUT_JSON}")