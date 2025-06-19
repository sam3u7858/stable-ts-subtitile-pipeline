import pickle
import stable_whisper


result1 = None


# open result1 use pickle
try:
    with open('result1.pickle', 'rb') as handle:
        result1 = pickle.load(handle)
except FileNotFoundError:
    print("File not found")


initial_prompt = '''
魔物獵人,



'''

if (result1 is None):
    model = stable_whisper.load_model('large-v2')
    result1 = model.transcribe(
        '20250604_edited.wav',  regroup=False, vad=False, initial_prompt=initial_prompt)
    (
        result1

        .split_by_punctuation([('.', ' '), '。', '?', '？', ',', '，', (',', ' '), '、'])



        .split_by_gap(.3)

        .split_by_punctuation([('.', ' '), '。', '?', '？'])
    )
    # save result1 use pickle

else:
    result1.reset()
    result1 = (
        result1

        # .split_by_punctuation([('.', ' '), ' ', '。', '?', '？', ',', '，', (',', ' '), '、'])
        .split_by_gap(.3)



        .split_by_punctuation([('.', ' '), '。', '?', '？'])
    )
    print(result1, "is result1 after reset and split_by_punctuation and split_by_gap and merge_by_gap and split_by_punctuation")


result1.to_srt_vtt('fullvoicev23.srt',  segment_level=True, word_level=False)

with open('result1.pickle', 'wb') as handle:
    pickle.dump(result1, handle, protocol=pickle.HIGHEST_PROTOCOL)
