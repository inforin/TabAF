import json


sample_file = './data/test_samples.jsonl'

def fill_table_data(obj):
    all_data = obj['texts']
    merged_regions = obj['merged_regions']
    for merged_region in merged_regions:
        cell_data = all_data[merged_region['first_row']][merged_region['first_column']]
        for i in range(merged_region['first_row'], min(merged_region['last_row'] + 1, len(all_data))):
            for j in range(merged_region['first_column'], min(merged_region['last_column'] + 1, len(all_data[0]))):
                all_data[i][j] = cell_data
    return obj

samples = [json.loads(line) for line in open(sample_file, 'r')]
origin_samples = []
for sample in samples:
    new_sample = {
        'id': sample['id'],
        'table_id': sample['table_id'],
        'question': sample['question'],
        'gold': '|'.join([str(i) for i in sample['answer']]),
    }
    table_obj = json.load(open(f'./data/tables/raw/{sample["table_id"]}.json'))
    fill_table_data(table_obj)
    new_sample['title'] = table_obj['title']
    new_sample['table'] = table_obj['texts']
    old_sample = new_sample.copy()
    old_sample['instruction'] = 'This is table question answering task, based on the given table, answer the given question. Only output the answer. '

    table = table_obj['texts']
    table_str = ""
    for row in table:
        table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
    old_sample['input'] = f'[Table Title]{table_obj["title"]}\n[Table]\n{table_str}\n\n[Question]\n{sample["question"]}\n\n[Answer]'
    origin_samples.append(old_sample)
json.dump(origin_samples, open(sample_file.replace('_samples.jsonl', '_origin_wtq_output.json'), 'w'), indent=4, ensure_ascii=False)