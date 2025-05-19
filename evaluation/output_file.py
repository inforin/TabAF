import json


def output_upperbound(res_f, res_o):
    id2res_o = {i['id']: i for i in res_o}
    output_objs = []
    for obj_f in res_f:
        obj_o = id2res_o[obj_f['id']]
        if not obj_f['correct'] and not obj_o['correct']:
            obj = {
                'id': obj_f['id'],
                'formula_sub_answer_logprobs': sum(obj_f['logprobs']) / len(obj_f['logprobs']) - sum(obj_o['logprobs']) / len(obj_o['logprobs']),
                'formula': obj_f['predict_formula'],
                'formula_ans': obj_f['predict'],
                'direct_ans': obj_o['predict'],
                'gold_ans': obj_f['label'],
            }
            table, question = obj_f['prompt'].split('system\nYou are an Excel Expert. Based on the Excel table, generate excel formula to answer the user question.\nuser\n')[1].split('\n\n\n[Question]\n')
            obj['question'] = question.split('\n\n[Formula]')[0]
            title, table = table.split('\n[Table]\n')
            obj['title'] = title
            for i, row in enumerate(table.split('|\n|')):
                obj[f'row_{i}'] = row
            output_objs.append(obj)
    json.dump(output_objs, open('beyond_upperbound.json', 'w'), ensure_ascii=False, indent=2)
    import random
    output_objs = random.sample(output_objs, k=100)
    json.dump(output_objs, open('beyond_upperbound_100.json', 'w'), ensure_ascii=False, indent=2)


def io_output_corrects(path, pred_objs):
    output_file = path.replace('.json', '_res.json')
    assert output_file != path

    with open(output_file, 'w', encoding='utf-8') as out:
        for obj in pred_objs:
            out_obj = obj.copy()
            del out_obj['logprobs']
            out_obj['logprobs'] = [i[2] for i in out_obj['corrects']]
            out_obj['corrects'] = [i[0] for i in out_obj['corrects']]
            out.write(json.dumps(out_obj, ensure_ascii=False) + '\n')


def io_output_wrong(path, pred_objs):
    output_file = path.replace('.json', '_wrong_sample.json')
    assert output_file != path

    with open(output_file, 'w', encoding='utf-8') as out:
        for obj in pred_objs:
            out_obj = obj.copy()
            del out_obj['logprobs']
            out_obj['logprobs'] = [i[2] for i in out_obj['corrects']]
            out_obj['corrects'] = [i[0] for i in out_obj['corrects']]
            del out_obj['prompt']
            if out_obj['corrects'].count(True) > 2:
                continue
            out.write(json.dumps(out_obj, ensure_ascii=False) + '\n')