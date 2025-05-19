import json
import csv

input_file = './data/pristine-unseen-tables.tsv'
output_format_file = 'test_format.json'
output_origin_file = 'test_origin.json'

format_samples = []
origin_samples = []
for i, line in enumerate(open(input_file, 'r')):
    if i == 0:
        continue
    id, qst, table_file, answer = line.strip().split('\t')
    new_sample = {}
    new_sample['id'] = id
    new_sample['question'] = qst
    new_sample['gold'] = answer
    new_sample['table_file'] = table_file
    old_sample = new_sample.copy()
    old_sample['instruction'] = 'This is table question answering task, based on the given table, answer the given question. Only output the answer. '
    new_sample['instruction'] = 'You are an Excel Expert. Based on the Excel table, generate excel formula to answer the user question.'
    
    new_table_file = table_file.replace('.csv', '_process.csv')
    assert new_table_file != table_file
    with open(new_table_file, 'w') as fout:
        for line in open(table_file):
            if table_file != 'csv/203-csv/128.csv':
                line = line.replace('\\"', '""')
            fout.write(line)
    fout.close()    
    table = [row for row in csv.reader(open(new_table_file))]
    new_sample['Table'] = table
    old_sample['Table'] = table
    table_str = ""
    for row in table:
        table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
    old_sample['input'] = f'[Table]\n{table_str}\n\n[Question]\n{qst}\n\n[Answer]'
    column_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    assert len(table[0]) <= len(column_names)
    table = [column_names[:len(table[0])]] + table
    table = [[str(j)] + row for j, row in enumerate(table)]
    
    table_str = ""
    for row in table:
        table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
    
    new_sample['input'] = f'[Table]\n{table_str}\n\n[Question]\n{qst}\n\n[Formula]'
    format_samples.append(new_sample)
    origin_samples.append(old_sample)
json.dump(format_samples, open(output_format_file, 'w'), indent=4, ensure_ascii=False)
json.dump(origin_samples, open(output_origin_file, 'w'), indent=4, ensure_ascii=False)