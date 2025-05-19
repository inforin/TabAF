from dataload_utils import load_gold_objs, load_pred_objs
from scorer_utils import cal_correct_by_pa, cal_correct_by_ppl, cal_correct_by_ppl_single, cal_correct_by_vote, scorer
from ouput_console import print_merge, print_single
from output_file import io_output_corrects, io_output_wrong

def add2stat(stat, is_cal, correct):
    stat['all'].append(correct)
    if is_cal:
        stat['cal'].append(correct)

def process_res_greedy(key, ident, path):
    id2golds, test_objs = load_gold_objs(key)
    pred_objs = load_pred_objs(key, path, test_objs)
    tokens = []
    stats = {'all': [], 'cal': []}
    for obj in pred_objs:
        tokens.append(len(obj['logprobs']))
        obj['correct'] = scorer(key, obj['predict'], id2golds[obj['id']])
        add2stat(stats, obj.get('is_cal'), obj['correct'])
    print_single(key, ident, stats)
    return pred_objs

def process_res_vote(key, ident, path):
    id2golds, test_objs = load_gold_objs(key)
    pred_objs = load_pred_objs(key, path, test_objs)
    for obj in pred_objs:
        corrects = []
        assert obj['logprobs']
        for predict, log_prob in zip(obj['predict'], obj['logprobs']):
            correct = scorer(key, predict, id2golds[obj['id']])
            if log_prob is not None:
                lp = sum(log_prob) / len(log_prob)
            corrects.append([correct, predict, lp])
        obj['corrects'] = corrects
    io_output_corrects(path, pred_objs)
    io_output_wrong(path, pred_objs)
    return pred_objs


def process_res(key, ident, path, vote):
    if vote:
        return process_res_vote(key, ident, path)
    else:
        return process_res_greedy(key, ident, path)
    

def merge_res_greedy(ident_f, ident_o, res_f, res_o):
    stats = {
        'ppl': {'all': [], 'cal': []},
        'upper': {'all': [], 'cal': []},
    }
    id2res_o = {i['id']: i for i in res_o}
    for obj_f in res_f:
        obj_o = id2res_o[obj_f['id']]
        is_cal = obj_f.get('is_cal')
        add2stat(stats['upper'], is_cal, obj_f['correct'] or obj_o['correct'])
        add2stat(stats['ppl'], is_cal, cal_correct_by_ppl_single(obj_f, obj_o))
    print_merge(ident_f, ident_o, stats)


def merge_res_vote(ident_f, ident_o, res_f, res_o):
    stats = {
        'vote': {'all': [], 'cal': []},
        'ppl': {'all': [], 'cal': []},
        'pa': {'all': [], 'cal': []},
        'upper': {'all': [], 'cal': []},
    }
    id2res_o = {i['id']: i for i in res_o}
    for obj_f in res_f:
        obj_o = id2res_o[obj_f['id']]
        corrects = obj_f['corrects'] + obj_o['corrects']
        is_cal = obj_f.get('is_cal')
        add2stat(stats['upper'], is_cal, any(ins[0] for ins in corrects))
        add2stat(stats['vote'], is_cal, cal_correct_by_vote(corrects))
        add2stat(stats['ppl'], is_cal, cal_correct_by_ppl(corrects))
        add2stat(stats['pa'], is_cal, cal_correct_by_pa(corrects))
    print_merge(ident_f, ident_o, stats)


def merge_res(key, vote, ident_f, ident_o, res_f, res_o):
    if vote:
        merge_res_vote(ident_f, ident_o, res_f, res_o)
    else:
        merge_res_greedy(ident_f, ident_o, res_f, res_o)

def merge_res_greedy(ident_f, ident_o, res_f, res_o):
    stats = {
        'ppl': {'all': [], 'cal': []},
        'upper': {'all': [], 'cal': []},
    }
    id2res_o = {i['id']: i for i in res_o}
    for obj_f in res_f:
        obj_o = id2res_o[obj_f['id']]
        is_cal = obj_f.get('is_cal')
        add2stat(stats['upper'], is_cal, obj_f['correct'] or obj_o['correct'])
        add2stat(stats['ppl'], is_cal, cal_correct_by_ppl_single(obj_f, obj_o))
    print_merge(ident_f, ident_o, stats)
    
