import itertools
import sys, os

from evaluation.process import process_res, merge_res

dataset_keys = ['hitab', 'wtq', 'squall', 'tabfact', 'aitqa', 'finqa']

def main(base_path):
    for root, dirs, _ in os.walk(base_path):
        if not any(d.startswith('inference_') for d in dirs):
            continue
        
        print('=' * 100, file=sys.stderr)
        print(f'In {root}', file=sys.stderr)
        print('=' * 100, file=sys.stderr)
        key2path = {}
        for d in dirs:
            if not any(i in d for i in dataset_keys):
                continue
            
            if d.startswith('inference_'):
                key, ident = d[len('inference_'):].split('_', 1)
                
                if key not in dataset_keys:
                    raise ValueError('Unknown datasets: ' + key)
                if 'format' in ident:
                    path = os.path.join(root, d, 'generated_predictions_executed2.jsonl')
                    key2path.setdefault(key, [[], []])[0].append([ident, path, 'vote' in path])
                elif 'origin' in ident:
                    path = os.path.join(root, d, 'generated_predictions.jsonl')
                    key2path.setdefault(key, [[], []])[1].append([ident, path, 'vote' in path])
                else:
                    raise ValueError('Unknown format: ' + ident)
        
        for key, (formats, origins) in key2path.items():
            print(f'>>> For Dataset {key}', file=sys.stderr)
            for instance in origins + formats:
                ident, path, vote = instance
                res = process_res(key, ident, path, vote)
                instance.append(res)
            
            if formats and origins:
                for (ident_f, path_f, vote_f, res_f), (ident_o, path_o, vote_o, res_o) in itertools.product(formats, origins):
                    if vote_f != vote_o:
                        continue
                    merge_res(key, vote_f, ident_f, ident_o, res_f, res_o)
            print(file=sys.stderr)

if __name__ == '__main__':
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
    main(base_path)
    base_path = f'saves/tabaf/{args.base_model}_vote'
    main(base_path)
