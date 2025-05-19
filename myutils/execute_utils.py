from datetime import datetime
from decimal import Decimal
import re
import xlwings as xw

def save_table(sheet, table, force_str=False):
    # processed_data = [row[1:] for row in table[1:]]
    len_rows = set(len(row) for row in table)
    if len(len_rows) != 1:
        new_table = []
        max_len = max(len_rows)
        for row in table:
            new_table.append(row + ['' for _ in range(100)][len(row):max_len])
        table = new_table

    processed_data = table
    table_data= [[element.lower() if type(element) == str else str(element) if type(element) == list else element for element in row] for row in processed_data]
    sheet.clear()
    num_rows = len(table_data)
    num_columns = len(table_data[0])

    fill_range = sheet.range((1, 1), (num_rows+10, num_columns+5))
    if force_str:
        fill_range.number_format = '@'
    # fill_range.number_format = '@'
    fill_range.value = table_data 

    for i in range(num_rows):
        for j in range(num_columns):
            read = fill_range.value[i][j]
            if read and type(read) not in [float, int, str, Decimal, bool]:
                if type(read) in [datetime]:
                    original = table_data[i][j]
                    sheet.range((i+1, j+1)).number_format = '@'
                    sheet.range((i+1, j+1)).value = f"{original}"
                else:
                    raise ValueError('Unknown: ', type(read))

def remove_sheet_references(formula):
    formula = re.sub(r"\$([A-Z]+)\$(\d+)", r"\1\2", formula)
    formula = re.sub(r"([A-Z]+)\$(\d+)", r"\1\2", formula)
    formula =  re.sub(r"(?:'[^']+'|[\w\d]+)!(?=[A-Z]+)", "", formula)
    return formula

def run_execution(preds, table, sheet: xw.Sheet, force_str=False, replace_dollor=False):
    row_len = len(table)
    save_table(sheet, table, force_str)
    f_cell = f'A{row_len+4}'
    answers = []
    processed_formulas = []
    if sheet.range(f_cell).value is None:
        for formula in preds:
            sheet.range(f_cell).clear()

            formula = formula.split('```excel\n')[-1].split('\n```')[0]
            if formula.count('```\n') == 1:
                formula = formula.split('```\n')[0]
            elif formula.count('```\n') == 2:
                formula = formula.split('```\n')[1]
            formula = formula.strip()
            formula = formula.replace('TEXTJOIN(", "', 'TEXTJOIN("| "')
            if '\\"' in formula:
                formula = formula.replace('\\"', '""')
            formula = remove_sheet_references(formula)

            try:
                if formula[0] == '=':
                    formula = formula[1:]
                if replace_dollor:
                    formula = formula.replace('$', '')
                if ';=' not in formula:
                    sheet.range(f_cell).formula2 = f"={formula}"
                    result = sheet.range(f_cell).value
                    if type(result) == datetime:
                        result = result.strftime('%Y-%m-%d')
                    elif type(result) == Decimal:
                        result = float(result)
                else:
                    results = []
                    for p in formula.split(';='):
                        sheet.range(f_cell).formula2 = f"={p}"
                        result = sheet.range(f_cell).value
                        if type(result) == datetime:
                            result = result.strftime('%Y-%m-%d')
                        results.append(result)
                    result = '|'.join([str(r) for r in results])
            except:
                result = '[Formula Exectution Error]'
            answers.append(result)
            processed_formulas.append(formula)
    else:
        raise ValueError("Cell not Empty!")
    return answers, processed_formulas