from abc import ABCMeta, abstractmethod
import math
import re
import unicodedata
from math import isnan, isinf

def normalize(x):
    x = ''.join(c for c in unicodedata.normalize('NFKD', x)
                if unicodedata.category(c) != 'Mn')
    # Normalize quotes and dashes
    x = re.sub(r"[‘’´`]", "'", x)
    x = re.sub(r"[“”]", "\"", x)
    x = re.sub(r"[‐‑‒–—−]", "-", x)
    while True:
        old_x = x
        # Remove citations
        x = re.sub(r"((?<!^)\[[^\]]*\]|\[\d+\]|[•♦†‡*#+])*$", "", x.strip())
        # Remove details in parenthesis
        x = re.sub(r"(?<!^)( \([^)]*\))*$", "", x.strip())
        # Remove outermost quotation mark
        x = re.sub(r'^"([^"]*)"$', r'\1', x.strip())
        if x == old_x:
            break
    # Remove final '.'
    if x and x[-1] == '.':
        x = x[:-1]
    # Collapse whitespaces and convert to lower case
    x = re.sub(r'\s+', ' ', x, flags=re.U).lower().strip()
    return x

class Value(object):
    __metaclass__ = ABCMeta

    # Should be populated with the normalized string
    _normalized = None

    @abstractmethod
    def match(self, other):
        """Return True if the value matches the other value.

        Args:
            other (Value)
        Returns:
            a boolean
        """
        pass

    @property
    def normalized(self):
        return self._normalized

class StringValue(Value):

    def __init__(self, content):
        assert isinstance(content, str)
        self._normalized = normalize(content)
        self._hash = hash(self._normalized)

    def __eq__(self, other):
        return isinstance(other, StringValue) and self.normalized == other.normalized

    def __hash__(self):
        return self._hash

    def __str__(self):
        return 'S' +  str([self.normalized])
    __repr__ = __str__

    def match(self, other):
        assert isinstance(other, Value)
        return self.normalized == other.normalized

class NumberValue(Value):

    def __init__(self, amount, original_string=None):
        assert isinstance(amount, (int, float))
        if abs(amount - round(amount)) < 1e-6:
            self._amount = int(amount)
        else:
            self._amount = float(amount)
        if not original_string:
            self._normalized = unicode(self._amount)
        else:
            self._normalized = normalize(original_string)
        self._hash = hash(self._amount)

    @property
    def amount(self):
        return self._amount

    def __eq__(self, other):
        return isinstance(other, NumberValue) and self.amount == other.amount

    def __hash__(self):
        return self._hash

    def __str__(self):
        return ('N(%f)' % self.amount) + str([self.normalized])
    __repr__ = __str__

    def match(self, other):
        assert isinstance(other, Value)
        if self.normalized == other.normalized:
            return True
        if isinstance(other, NumberValue):
            return abs(self.amount - other.amount) < 1e-6
        return False

    @staticmethod
    def parse(text):
        """Try to parse into a number.

        Return:
            the number (int or float) if successful; otherwise None.
        """
        try:
            return int(text)
        except:
            try:
                amount = float(text)
                assert not isnan(amount) and not isinf(amount)
                return amount
            except:
                return None

class DateValue(Value):

    def __init__(self, year, month, day, original_string=None):
        """Create a new DateValue. Placeholders are marked as -1."""
        assert isinstance(year, int)
        assert isinstance(month, int) and (month == -1 or 1 <= month <= 12)
        assert isinstance(day, int) and (day == -1 or 1 <= day <= 31)
        assert not (year == month == day == -1)
        self._year = year
        self._month = month
        self._day = day
        if not original_string:
            self._normalized = '{}-{}-{}'.format(
                year if year != -1 else 'xx',
                month if month != -1 else 'xx',
                day if day != '-1' else 'xx')
        else:
            self._normalized = normalize(original_string)
        self._hash = hash((self._year, self._month, self._day))

    @property
    def ymd(self):
        return (self._year, self._month, self._day)

    def __eq__(self, other):
        return isinstance(other, DateValue) and self.ymd == other.ymd

    def __hash__(self):
        return self._hash

    def __str__(self):
        return (('D(%d,%d,%d)' % (self._year, self._month, self._day))
                + str([self._normalized]))
    __repr__ = __str__

    def match(self, other):
        assert isinstance(other, Value)
        if self.normalized == other.normalized:
            return True
        if isinstance(other, DateValue):
            return self.ymd == other.ymd
        return False

    @staticmethod
    def parse(text):
        """Try to parse into a date.

        Return:
            tuple (year, month, date) if successful; otherwise None.
        """
        try:
            ymd = text.lower().split('-')
            assert len(ymd) == 3
            year = -1 if ymd[0] in ('xx', 'xxxx') else int(ymd[0])
            month = -1 if ymd[1] == 'xx' else int(ymd[1])
            day = -1 if ymd[2] == 'xx' else int(ymd[2])
            assert not (year == month == day == -1)
            assert month == -1 or 1 <= month <= 12
            assert day == -1 or 1 <= day <= 31
            return (year, month, day)
        except:
            return None


def naive_str_to_float(string):
    """ A naive way to convert str to float, if convertable."""
    sanitized = string
    try:
        if sanitized[0] == '(':
            sanitized = sanitized[1:]
        if (sanitized[-1] == '%') or (sanitized[-1] == ')'):
            sanitized = sanitized[: -1]
        sanitized = sanitized.replace(',', '')
        new = float(sanitized)
        return new
    except:
        return normalize(string)

def hmt_process_answer(answer):
    """ 4 types of answer: 1)region; 2)num_list(aggr); 3)header_list(argmax); 4)num(count/div)"""
    if isinstance(answer, int) or isinstance(answer, float):
        return float(answer)
    if isinstance(answer, str):
        return naive_str_to_float(answer.strip().lower())
    if isinstance(answer, list):
        if isinstance(answer[0], list):  # pred region
            if len(answer) == 1 and len(answer[0]) == 1:  # pred region with one cell, flatten
                return hmt_process_answer(answer[0][0])
            elif len(answer) == 1:  # pred region with one line
                return hmt_process_answer(answer[0])
            elif len(answer[0]) == 1:  # pred region with one line
                return hmt_process_answer([row[0] for row in answer])
            else:  # pred region is a matrix
                return [hmt_process_answer(a) for a in answer]
        else:  # list or processed single-line region
            if len(answer) == 1:  # answer with one cell or pred list
                return [hmt_process_answer(answer[0])]
            else:
                return [hmt_process_answer(a) for a in answer]

def to_value(original_string, corenlp_value=None):
    if isinstance(original_string, Value):
        # Already a Value
        return original_string
    if not corenlp_value:
        corenlp_value = original_string
    # Number?
    amount = NumberValue.parse(corenlp_value)
    if amount is not None:
        return NumberValue(amount, original_string)
    # Date?
    ymd = DateValue.parse(corenlp_value)
    if ymd is not None:
        if ymd[1] == ymd[2] == -1:
            return NumberValue(ymd[0], original_string)
        else:
            return DateValue(ymd[0], ymd[1], ymd[2], original_string)
    # String.
    return StringValue(original_string)

def to_pred_value_list(pred_str, gold_values):
    """Convert a list of strings to a list of Values

    Args:
        original_strings (list[basestring])
        corenlp_values (list[basestring or None])
    Returns:
        list[Value]
    """
    if type(pred_str) in [str, float, int, bool] or pred_str == None:
        pred_str = str(pred_str)
        if pred_str.startswith('<') and pred_str.endswith('>'):
            pred_str = pred_str[1:-1].split('>,<')
        elif '|' in pred_str:
            pred_str = pred_str.split('|')
        elif len(gold_values) == 1:
            pred_str = [pred_str]
        else:
            preds = []
            golds = [str(i) for i in gold_values]
            golds = sorted(golds, key=lambda x: len(x), reverse=True)
            for gold in golds:
                if gold in pred_str:
                    preds.append(gold)
                    pred_str = pred_str.replace(gold, '', 1)
            if pred_str.replace(', ', '').replace(',', '') != '':
                preds.append(pred_str.replace(', ', '').replace(',', ''))
            pred_str = preds
    assert isinstance(pred_str, (list, tuple, set)), type(pred_str)
    return list(set(to_value(x) for x in pred_str))

