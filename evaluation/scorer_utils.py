from collections import Counter, defaultdict
import math
from datatype_utils import hmt_process_answer, to_pred_value_list

def hitab_score(prediction, answer):
    prediction = hmt_process_answer(prediction)
    answer = hmt_process_answer(answer)

    def hmt_equal(prediction, answer):
        if type(prediction) != type(answer):
            return False
        if isinstance(prediction, str):
            return prediction == answer
        if isinstance(prediction, int) or isinstance(prediction, float):
            return math.fabs(prediction - answer) < 1e-5
        if isinstance(prediction, list):
            if len(prediction) != len(answer):
                return False
            return all([hmt_equal(prediction[i], answer[i]) for i in range(len(prediction))])

    return hmt_equal(prediction, answer)


def wtq_score(target_values, predicted_values):
    if len(target_values) != len(predicted_values):
        return False
    for target in target_values:
        if not any(target.match(pred) for pred in predicted_values):
            return False
    return True

def scorer(key, predict, target_values):
    if key == 'tabfact':
        correct = str(predict).lower() == target_values.lower()
    elif key == 'finqa':
        if type(target_values) == str:
            correct  = str(predict).lower() == target_values.lower()
        elif type(target_values) in [float, int]:
            try:
                predict = float(predict)
                correct = abs(predict - target_values) < 1e-5 or abs(predict / 100 - target_values) < 1e-5
            except:
                correct = False
        else:
            print('unkown type: ', predict)
            print('unkown type: ', type(predict), 'gold: ', type(target_values))
            correct = False
    elif key == 'hitab':
        if type(predict) == str:
            predict = predict.split('|')
        else:
            predict = [predict]
        correct = hitab_score(predict, target_values)
    else:
        predicted_values = to_pred_value_list(predict, target_values)
        correct = wtq_score(target_values, predicted_values)
    return correct

# 结果合并

def not_force_answer(f_predict):
    return 'Formula Exectution Error' not in str(f_predict) and f_predict is not None and f_predict != -2146826238 and str(f_predict) != '0.0'
    # return 'Formula Exectution Error' not in str(f_predict) and f_predict is not None


def cal_correct_by_ppl_single(obj_f, obj_o):
    if not not_force_answer(obj_f['predict']):
        return obj_o['correct']
    lp_f = sum(obj_f['logprobs']) / len(obj_f['logprobs'])
    lp_o = sum(obj_o['logprobs']) / len(obj_o['logprobs'])
    return obj_f['correct'] if lp_f > lp_o else obj_o['correct']

def cal_correct_by_ppl(corrects):
    except_corrects = [[a, b, c] for a, b, c in corrects if not_force_answer(b)]
    if not except_corrects:
        return corrects[0][0]
    b_weight_sum = defaultdict(int)
    b_to_a = {}
    for a, b, c in except_corrects:
        b_weight_sum[b] = max(math.exp(c), b_weight_sum.get(b, 0))
        b_to_a[b] = a 
    max_b = max(b_weight_sum, key=b_weight_sum.get)
    correct = b_to_a[max_b]
    assert correct in [True, False]
    return correct


def cal_correct_by_pa(corrects):
    except_corrects = [[a, b, c] for a, b, c in corrects if not_force_answer(b)]
    if not except_corrects:
        return corrects[0][0]
    b_weight_sum = defaultdict(int)
    b_to_a = {}
    for a, b, c in except_corrects:
        b_weight_sum[b] += math.exp(c)
        b_to_a[b] = a  
    max_b = max(b_weight_sum, key=b_weight_sum.get)
    correct = b_to_a[max_b]
    assert correct in [True, False]
    return correct


def cal_correct_by_vote(corrects):
    except_corrects = [[a, b, c] for a, b, c in corrects if not_force_answer(b)]
    if except_corrects:
        b_count = Counter(b for a, b, c in except_corrects)
        most_common_b = b_count.most_common(1)[0][0]
        correct = next(a for a, b, c in corrects if b == most_common_b)
    else:
        correct = corrects[0][0]
    return correct