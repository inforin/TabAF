

import sys


def cal_score(corrects: list):
    num_correct = corrects.count(True)
    num_examples = len(corrects)
    return round((num_correct + 1e-9) / (num_examples + 1e-9) * 100, 2)


def print_single(key, ident, stat):
    all_acc = cal_score(stat['all'])
    cal_acc = cal_score(stat.get('cal', []))
    if stat.get('cal', []):
        print(f'[{key}][{ident}] All||Cal: {all_acc}\t{cal_acc}', file=sys.stderr)
    else:
        print(f'[{key}][{ident}] Accuracy: {all_acc}', file=sys.stderr)


def print_merge(ident_f, ident_o, stats: dict):
    for strategy, stat in stats.items():
        all_acc = cal_score(stat['all'])
        cal_acc = cal_score(stat.get('cal', []))
        if stat.get('cal', []):
            print(f'[Merge {ident_f} & {ident_o}] ({strategy}) All||Cal: {all_acc}\t{cal_acc}', file=sys.stderr)
        else:
           print(f'[Merge {ident_f} & {ident_o}] ({strategy}) Accuracy: {all_acc}', file=sys.stderr)
