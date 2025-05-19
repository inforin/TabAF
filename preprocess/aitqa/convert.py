import json


question_file = './aitqa_questions.jsonl'
table_file = './aitqa_tables.jsonl'

aitqa_objs = [json.loads(line) for line in open(question_file)]
tables = [json.loads(line) for line in open(table_file)]

for tobj in tables:
    row_header = tobj["row_header"]
    column_header = tobj["column_header"]
    data = tobj['data']
    if len(set(len(i) for i in column_header)) != 1:
        print('column header err', tobj['id'], '; ', [len(i) for i in column_header])
    
    column_header_len = max([len(i) for i in column_header])
    for i in column_header:
        while len(i) != column_header_len:
            i.append('')
    
    column_header = list(zip(*column_header))
    if row_header == []:
        column_header = [list(ch) for ch in column_header]
        table = column_header + data
    else:
        row_header_len = max([len(i) for i in row_header])
        for i in row_header:
            while len(i) != row_header_len:
                i.append('')
        column_header = [['header'] * len(row_header[0]) + list(ch) for ch in column_header]
        table = column_header
        for rh, row in zip(row_header, data):
            table.append(rh + row)
    tobj['table'] = table

id2tables = {i['id']: i for i in tables}


output_format_file = 'test_format.json'
output_origin_file = 'test_origin.json'  
        
format_samples = []
origin_samples = []
for obj in aitqa_objs:
    new_sample = {}
    new_sample['id'] = obj['id']
    new_sample['question'] = qst = obj['question']
    new_sample['gold'] = obj['answers']
    new_sample['table_id'] = obj['table_id']
    old_sample = new_sample.copy()
    old_sample['instruction'] = 'This is table question answering task, based on the given table, answer the given question. Only output the answer. '
    new_sample['instruction'] = 'You are an Excel Expert. Based on the Excel table, generate excel formula to answer the user question.'
    
    tobj = id2tables[obj['table_id']]
    table = tobj['table']
    new_sample['Table'] = table
    old_sample['Table'] = table
    table_str = ""
    for row in table:
        table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
    old_sample['input'] = f'[Table]\n{table_str}\n\n[Question]\n{qst}\n\n[Answer]'
    column_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    assert len(table[0]) <= len(column_names)
    table = [column_names[:len(table[0])]] + table
    print(table)
    table = [[str(j)] + row for j, row in enumerate(table)]
    
    table_str = ""
    for row in table:
        table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
    
    new_sample['input'] = f'[Table]\n{table_str}\n\n[Question]\n{qst}\n\n[Formula]'
    format_samples.append(new_sample)
    origin_samples.append(old_sample)
json.dump(format_samples, open(output_format_file, 'w'), indent=4, ensure_ascii=False)
json.dump(origin_samples, open(output_origin_file, 'w'), indent=4, ensure_ascii=False)