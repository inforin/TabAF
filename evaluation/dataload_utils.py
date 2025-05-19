import json
import os
from datatype_utils import to_value

def tsv_unescape(x):
    return x.replace(r'\n', '\n').replace(r'\p', '|').replace('\\\\', '\\')

def tsv_unescape_list(x):
    return [tsv_unescape(y) for y in x.split('|')]

def load_wtq_gold():
    def to_wtq_gold_value_list(original_strings, corenlp_values=None):
        assert isinstance(original_strings, (list, tuple, set))
        if corenlp_values is not None:
            assert isinstance(corenlp_values, (list, tuple, set))
            assert len(original_strings) == len(corenlp_values)
            return list(set(to_value(x, y) for (x, y)
                    in zip(original_strings, corenlp_values)))
        else:
            return list(set(to_value(x) for x in original_strings))

    tagged_dataset_path = '../data/wtq/tagged/data'
    target_values_map = {}
    for filename in os.listdir(tagged_dataset_path):
        filename = os.path.join(tagged_dataset_path, filename)
        with open(filename, 'r', encoding='utf8') as fin:
            header = fin.readline().rstrip('\n').split('\t')
            for line in fin:
                stuff = dict(zip(header, line.rstrip('\n').split('\t')))
                ex_id = stuff['id']
                original_strings = tsv_unescape_list(stuff['targetValue'])
                canon_strings = tsv_unescape_list(stuff['targetCanon'])
                target_values_map[ex_id] = to_wtq_gold_value_list(
                        original_strings, canon_strings)
                        # original_strings, None)
    test_file = '../data/wtq/test_origin.json'
    test_objs = json.load(open(test_file, encoding='utf-8'))
    return target_values_map, test_objs

def load_squall_gold():
    test_file = '../data/squall/test_origin_and_sql.json'
    test_objs = json.load(open(test_file, encoding='utf-8'))
    return test_objs

def load_hitab_gold():
    test_file = '../data/hitab/test_origin.json'
    test_objs = json.load(open(test_file, encoding='utf-8'))
    
    id2golds = {i['id']: i['gold'].split('|') for i in test_objs}
    return id2golds, test_objs

def load_aitqa_gold():
    def to_aitqa_gold_value_list(gold_str: str):
        preds = gold_str
        assert isinstance(preds, (list, tuple, set)), type(preds)
        return list(set(to_value(x) for x in preds))
    test_file = '../data/aitqa/test_origin.json'
    test_objs = json.load(open(test_file, encoding='utf-8'))
    id2golds = {i['id']: to_aitqa_gold_value_list(i['gold']) for i in test_objs}
    return id2golds, test_objs
    
def load_tabfact_gold():
    test_file = '../data/tabfact/test_origin.json'
    test_objs = json.load(open(test_file, encoding='utf-8'))
    
    id2golds = {i['id']: i['gold'] for i in test_objs}
    return id2golds, test_objs

def load_finqa_gold():
    def to_finqa_gold_value_list(gold_str: str):
        preds = gold_str
        assert isinstance(preds, (float, str, int)), type(preds)
        return preds
    test_file = '../data/finqa/test_origin.json'
    test_objs = json.load(open(test_file, encoding='utf-8'))
    id2golds = {i['id']: to_finqa_gold_value_list(i['gold']) for i in test_objs}
    return id2golds, test_objs


def load_gold_objs(dataset):
    if dataset == 'wtq':
        id2golds, test_objs = load_wtq_gold()
        id2is_cal = json.load(open('test_is_cal.json', encoding='utf-8'))
        for test_obj in test_objs:
            test_obj['is_cal'] = id2is_cal[test_obj['id']]
    elif dataset == 'hitab':
        id2golds, test_objs = load_hitab_gold()
    elif dataset == 'tabfact':
        id2golds, test_objs = load_tabfact_gold()
    elif dataset == 'squall':
        id2golds, test_objs = load_wtq_gold()
        test_objs_squall = load_squall_gold()
        id2test_objs_squall = {i['id']: i for i in test_objs_squall}
        for test_obj in test_objs:
            test_obj['question'] = id2test_objs_squall[test_obj['id']]['question']
    elif dataset == 'aitqa':
        id2golds, test_objs = load_aitqa_gold()
    elif dataset == 'finqa':
        id2golds, test_objs = load_finqa_gold()
    else:
        raise ValueError('Unknown dataset')
    return id2golds, test_objs


def load_pred_objs(dataset, path, test_objs):
    pred_objs = [json.loads(line) for line in open(path, encoding='utf-8')]
    assert len(test_objs) == len(pred_objs)
    id2test_obj = {i['id']: i for i in test_objs}
    if 'id' not in pred_objs[0]:
        sample_ids = set()
        q2testid = {}
        for test_obj in test_objs:
            question = test_obj['question']
            q2testid.setdefault(question, []).append(test_obj['id'])
        for pred_obj in pred_objs:
            question = pred_obj['prompt'].split(']\n')[-1].split('\n\n')[0]
            test_obj = id2test_obj[q2testid[question].pop(0)]
            pred_obj['id'] = test_obj['id']
            sample_ids.add(test_obj['id'])
        assert len(sample_ids) == len(pred_objs), 'ids并没有都出现'

    if dataset == 'hitab':
        for pred_obj in pred_objs:
            pred_obj['is_cal'] = id2test_obj[pred_obj['id']]['formula'].lower().strip('=0123456789abcdefghijklmnopqrstuvwxyz;') != ''
    elif dataset == 'wtq':
        for pred_obj in pred_objs:
            pred_obj['is_cal'] = id2test_obj[pred_obj['id']]['is_cal'].count(True) >= 3
    
    for pred_obj in pred_objs:
        test_obj = id2test_obj[pred_obj['id']]
        if 'table_file' in test_obj:
            pred_obj['table_id'] = test_obj['table_file']
        elif 'table_id' in test_obj:
            pred_obj['table_id'] = test_obj['table_id']

        pred_obj['question'] = test_obj['question']
    return pred_objs
