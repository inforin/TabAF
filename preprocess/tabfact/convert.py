import json
import pandas as pd

test1_file = './collected_data/r1_training_all.json'
test2_file = './collected_data/r2_training_all.json'

tid2samples = json.load(open(test1_file , encoding='utf-8'))
tid2samples.update(json.load(open(test2_file, encoding='utf-8')))

samples = []
for tid in json.load(open('./data/small_test_id.json')):
    questions, labels, title = tid2samples[tid]
    df = pd.read_csv(f'./data/all_csv/{tid}', sep='#')
    table = [df.columns.tolist()] + df.values.tolist()
    for i, (question, label) in enumerate(zip(questions, labels)):
        sample = {
            'id': f'{tid}-q{i}',
            'table_file': tid,
            'question': question,
            'gold': str(label == 1),
            'Table': table.copy(),
            # 'instruction': 'You are an Excel Expert. Based on the Excel table, generate excel formula to check whether the sentence is correct.',
            'instruction': 'This is table fact verification task, based on the given table, judge whether the sentence is correct. Only output the True or False.',
        }
        table_str = ""
        for row in table:
            table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
        sample['input'] = f'[Table]\n{table_str}\n\n[Sentence]\n{question}\n\n[Formula]'
        samples.append(sample)
# json.dump(samples, open('test_format.json', 'w'), indent=4, ensure_ascii=False)
json.dump(samples, open('test_origin.json', 'w'), indent=4, ensure_ascii=False)
