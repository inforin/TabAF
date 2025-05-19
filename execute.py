import json
import xlwings as xw
from tqdm import tqdm
import os
import json
from codecs import open
from myutils.execute_utils import run_execution


dataset_keys = ['hitab', 'wtq', 'squall', 'tabfact', 'aitqa', 'finqa']

paths = []
def add_path(paths, base_dir, vote=False):
    if vote:
        base_dir += '_vote'
    for d in os.listdir(base_dir):
        if d.startswith('inference_'):
            key, ident = d[len('inference_'):].split('_', 1)
            if key not in dataset_keys:
                print('Unknown datasets: ' + key)
                continue
            if 'format' in ident:
                if 'generated_predictions.jsonl' not in os.listdir(base_dir + '/' + d):
                    print('predictions file not found')
                    continue
                path = base_dir + '/' + d + '/' +'generated_predictions.jsonl'
                paths.append(path)
                print(path)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '--base_model',
    type=str,
    required=True,
    choices=['qwen2.5-coder-7b', 'qwen2.5-coder-14b', 'qwen2.5-coder-32b', 'llama3.1-8b', 'llama3.1-70b'],
)
args = parser.parse_args()

base_path = f'saves/tabaf/{args.base_model}'
add_path(paths, base_path, False)
add_path(paths, base_path, True)

app = xw.App(visible=True, add_book=False)
wb = app.books.add()
sheet = wb.sheets.active

for pred_file in paths:
    if 'inference_hitab' in pred_file:
        test_file = './data/hitab/test_format.json'
    elif 'inference_tabfact' in pred_file:
        test_file = './data/tabfact/test_format.json'
    elif 'inference_wtq' in pred_file:
        test_file = './data/wtq/test_format.json'
    elif 'inference_aitqa' in pred_file:
        test_file = './data/aitqa/test_format.json'
    elif 'inference_finqa' in pred_file:
        test_file = './data/finqa/test_formatx.json'
    else:
        raise ValueError('Unkown pred_file:', pred_file)
    
    output_file = pred_file.replace('.jsonl', '_executed2.jsonl')
    assert pred_file != output_file
    print('[Pred File]', pred_file)
    print('[Test File]', test_file)
 
    test_objs = json.load(open(test_file, encoding='utf-8'))
    pred_objs = [json.loads(line) for line in open(pred_file)]
    id2test_obj = {i['id']: i for i in test_objs}

    q2testid = {}
    for test_obj in test_objs:
        question = test_obj['question']
        if question in q2testid:
            print(question)
        q2testid.setdefault(question, []).append(test_obj['id'])
    
    with open(output_file, 'w', encoding='utf-8') as fout:
        for pred_obj in tqdm(pred_objs, total=len(pred_objs), ncols=80):
            question = pred_obj['prompt'].split(']\n')[-1].split('\n\n')[0]
            if 'id' not in pred_obj:
                test_obj = id2test_obj[q2testid[question].pop(0)]
                pred_obj['id'] = test_obj['id']
            else:
                test_obj = id2test_obj[pred_obj['id']]
            table = test_obj['table'] if 'table' in test_obj else test_obj['Table']
            
            if 'vote' in pred_file:
                formulas = pred_obj['predict']
                answers, processed_formulas = run_execution(formulas, table, sheet, force_str='aitqa' in pred_file, replace_dollor='finqa' in pred_file)
            else:
                formulas = [pred_obj['predict']]
                answers, processed_formulas = run_execution(formulas, table, sheet, force_str='aitqa' in pred_file, replace_dollor='finqa' in pred_file)
                answers = answers[0]
            pred_obj['predict_formula'] = pred_obj['predict']
            pred_obj['predict'] = answers
            try:
                fout.write(json.dumps(pred_obj, ensure_ascii=False) + '\n')
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(pred_obj)
                raise e
    
app.quit()