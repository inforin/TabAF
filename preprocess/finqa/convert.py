import json


input_file = './dataset/test.json'
output_format_file = 'test_format.json'
output_origin_file = 'test_origin.json'

format_samples = []
origin_samples = []
for obj in json.load(open(input_file, 'r')):
    pre_text = '\n'.join(obj['pre_text'])
    post_text = '\n'.join(obj['post_text'])
    
    new_sample = {}
    new_sample['id'] = obj['id']
    new_sample['question'] = qst = obj['qa']['question']
    new_sample['gold'] = obj['qa']['exe_ans']
    old_sample = new_sample.copy()
    old_sample['instruction'] = 'This is table-text question answering task, based on the given table and the text on both sides of the table, answer the given question. Only output the answer. '
    new_sample['instruction'] = 'You are an Excel Expert. Based on the Excel table with text before and after the table, generate excel formula to answer the user question. If some values come from the text before or after the table, use those values directly in the formula, such as (E8 + 2306.5) / A9, A2*(2.1+3.5)/5. '
    table = obj['table_ori']
    if len(set(len(i) for i in table)) != 1:
        print('扩展')
        max_len = max([len(i) for i in table])
        processed_data = table = [i + [''] * (max_len - len(i)) for i in table]
        assert len(set(len(i) for i in table)) == 1
    
    new_sample['Table'] = table
    old_sample['Table'] = table
    table_str = ""
    for row in table:
        table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
    old_sample['input'] = f'[Text before the table]\n{pre_text}\n\n[Table]\n{table_str}\n[Text after the table]\n{post_text}\n\n[Question]\n{qst}\n\n[Answer]'
    column_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    assert len(table[0]) <= len(column_names)
    table = [column_names[:len(table[0])]] + table
    table = [[str(j)] + row for j, row in enumerate(table)]
    
    table_str = ""
    for row in table:
        table_str += '|' + '|'.join([str(i) for i in row]) + '|\n'
    
    new_sample['input'] = f'[Text before the table]\n{pre_text}\n[Table]\n{table_str}\n[Text after the table]\n{post_text}\n\n[Question]\n{qst}\n\n[Formula]'
    format_samples.append(new_sample)
    origin_samples.append(old_sample)
json.dump(format_samples, open(output_format_file, 'w'), indent=4, ensure_ascii=False)
json.dump(origin_samples, open(output_origin_file, 'w'), indent=4, ensure_ascii=False)