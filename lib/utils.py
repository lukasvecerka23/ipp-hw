import sys
import re


def get_symb_value(symb, context):
    if symb['type'] == 'var':
        var = symb['value'].split('@')
        var_data = get_var_value(var, context)
        # if var_data['value'] is None:
        #     exit_with_code(56, "Error: Variable not initialized.")
        return var_data['value'], var_data['type']
    elif symb['type'] == 'int':
        try:
            val = int(symb['value'])
        except ValueError:
            exit_with_code(32, "Error: Wrong type of value.")
        return val, 'int'
    elif symb['type'] == 'bool':
        if symb['value'] == 'true':
            return True, 'bool'
        elif symb['value'] == 'false':
            return False, 'bool'
    elif symb['type'] == 'string':
        if symb['value'] is None:
            return '', 'string'
        string = remove_escape_seq(symb['value'])
        return string, 'string'
    elif symb['type'] == 'nil':
        return 'nil', 'nil'


def store_val_to_var(var, val, val_type, context):
    err = True
    if var[0] == 'GF':
        if var[1] in context.global_frame.keys():
            context.global_frame[var[1]] = {'type': val_type, 'value': val}
            return
    elif var[0] == 'LF':
        if len(context.local_frame) == 0:
            exit_with_code(55, "Error: No local frame.")
        if var[1] in context.local_frame[-1].keys():
            context.local_frame[-1][var[1]] = {'type': val_type, 'value': val}
            return
    elif var[0] == 'TF':
        if context.tmp_frame is None:
            exit_with_code(55, "Error: No temporary frame.")
        if var[1] in context.tmp_frame.keys():
            context.tmp_frame[var[1]] = {'type': val_type, 'value': val}
            return
    else:
        exit_with_code(55, "Error: Wrong variable type.")

    if err:
        exit_with_code(54, "Error: Variable doesn't exist.")


def get_var_value(var, context):
    val = None
    if var[0] == 'GF':
        val = context.global_frame.get(var[1])
    elif var[0] == 'LF':
        if len(context.local_frame) == 0:
            exit_with_code(55, "Error: No local frame.")
        val = context.local_frame[-1].get(var[1])
    elif var[0] == 'TF':
        if context.tmp_frame is None:
            exit_with_code(55, "Error: No temporary frame.")
        val = context.tmp_frame.get(var[1])
    if val is None:
        exit_with_code(54, "Error: Variable doesn't exist.")
    return val


def exit_with_code(code, text):
    print(text, file=sys.stderr)
    sys.exit(code)


def remove_escape_seq(string):
    if len(string) != 0:
        string = re.sub(r'\\(\d{3})', lambda match: chr(int(match.group(1))), string)
    return string

