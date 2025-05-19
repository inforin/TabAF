import os
import concurrent.futures
from tqdm import tqdm
import openai
import json

base_url = 'http://{your_url}:{your_port}/v1/'
api_key = 'your key'


def process_obj(obj, dataset_info, vote=False):
    openai_client = openai.OpenAI(base_url=base_url, api_key=api_key)
    messages = [
        {'role': 'system', 'content': obj[dataset_info['columns']['prompt']]},
        {'role': 'user', 'content': obj[dataset_info['columns']['query']]},
    ]

    if vote:
        n = 5
        temperature = 0.8
    else:
        n = 1
        temperature = 0

    try:
        response = openai_client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=384,
            temperature=temperature,
            n=n,
            logprobs=True,
            top_logprobs=5,
        )
    except:
        import traceback
        traceback.print_exc()
        return None
    try:
        if vote:
            answer = [choice.message.content for choice in response.choices]
            logprob_list = [[k.logprob for k in (choice.logprobs.content if choice.logprobs else [])] for choice in response.choices]
        else:
            answer = response.choices[0].message.content
            logprob_list = [k.logprob for k in (response.choices[0].logprobs.content if response.choices[0].logprobs else [])]

        o_obj = {
            'id': obj['id'],
            'prompt': f"system\n{obj[dataset_info['columns']['prompt']]}\nuser\n{obj[dataset_info['columns']['query']]}",
            'predict': answer,
            'label': obj[dataset_info['columns']['response']],
            'logprobs': logprob_list,
        }
        return o_obj
    except Exception:
        import traceback
        traceback.print_exc()
        return None
    
def main(base_model):
    base_path = f'saves/tabaf/{base_model}'
    base_path2 = base_path + '_vote'
    

    k2v = [
        ('hitab_test_format', f'{base_path}/inference_hitab_format'),
        ('hitab_test_origin', f'{base_path}/inference_hitab_origin'),
        ('tabfact_test_format', f'{base_path}/inference_tabfact_format'),
        ('tabfact_test_origin', f'{base_path}/inference_tabfact_origin'),
        ('aitqa_test_origin', f'{base_path}/inference_aitqa_origin'),
        ('aitqa_test_format', f'{base_path}/inference_aitqa_format'),
        ('finqa_test_origin', f'{base_path}/inference_finqa_origin'),
        ('finqa_test_format', f'{base_path}/inference_finqa_format'),
        ('wtq_test_format', f'{base_path}/inference_wtq_format'),
        ('wtq_test_origin', f'{base_path}/inference_wtq_origin'),
        
        ('hitab_test_format', f'{base_path2}/inference_hitab_format'),
        ('hitab_test_origin', f'{base_path2}/inference_hitab_origin'),
        ('tabfact_test_format', f'{base_path2}/inference_tabfact_format'),
        ('tabfact_test_origin', f'{base_path2}/inference_tabfact_origin'),
        ('wtq_test_format', f'{base_path2}/inference_wtq_format'),
        ('wtq_test_origin', f'{base_path2}/inference_wtq_origin'),
        ('aitqa_test_origin', f'{base_path2}/inference_aitqa_origin'),
        ('aitqa_test_format', f'{base_path2}/inference_aitqa_format'),
        ('finqa_test_origin', f'{base_path2}/inference_finqa_origin'),
        ('finqa_test_format', f'{base_path2}/inference_finqa_format'),
    ]
    
    for eval_dataset, output_dir in k2v:
        print(f"Working on {eval_dataset}")

        dataset_info = json.load(open('data/dataset_info.json'))[eval_dataset]
        l_datast_file = f'data/{dataset_info["file_name"]}'
        dataset_objs = json.load(open(l_datast_file, encoding='utf-8'))
        l_out_file = f'{output_dir}/generated_predictions.jsonl'
        os.makedirs(output_dir, exist_ok=True)
        
        if os.path.exists(l_out_file):
            sample_ids = [json.loads(line)['id'] for line in open(l_out_file, 'r', encoding='utf-8')]
            out = open(l_out_file, 'a', encoding='utf-8')
        else:
            sample_ids = []
            out = open(l_out_file, 'w', encoding='utf-8')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = [
                executor.submit(process_obj, obj, dataset_info, vote='vote' in output_dir) 
                for i, obj in enumerate(dataset_objs)
                if obj['id'] not in sample_ids
            ]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), ncols=50):
                o_obj = future.result()
                if o_obj:
                    out.write(json.dumps(o_obj) + '\n')
                    out.flush()
                else:
                    print(o_obj)
        out.close()

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
    main(args.base_model)
