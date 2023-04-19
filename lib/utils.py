import sys
import re
from typing import Dict, Union, List


def get_symb_value(symb: Dict[str, str], context) -> (Union[str, int, bool], str):
    """
    Get value and type of symbol.
    :param symb: XML argument
    :param context:  Interpret class
    :return: Tuple of value and type
    """
    if symb['type'] == 'var':
        var: List[str] = symb['value'].strip().split('@')
        var_data: Dict[str, str] = get_var_value(var, context)
        return var_data['value'], var_data['type']
    elif symb['type'] == 'int':
        val: int = 0
        try:
            val: int = int(symb['value'])
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
        string: str = symb['value'].strip().replace('\n', '')
        string: str = remove_escape_seq(string)
        return string, 'string'
    elif symb['type'] == 'nil':
        return 'nil', 'nil'


def store_val_to_var(var: List[str], val: Union[int, str, bool], val_type: str, context) -> None:
    """
    Store value to variable.
    :param var: Variable frame and name where to store the value
    :param val: Value to store
    :param val_type: Type of value
    :param context: Interpret class
    :return: None
    """
    err: bool = True
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
        exit_with_code(52, "Error: Wrong variable type.")

    if err:
        exit_with_code(54, "Error: Variable doesn't exist.")


def get_var_value(var: List[str], context) -> Dict[str, str]:
    """
    Get value of variable.
    :param var: Variable frame and name
    :param context: Interpret class
    :return: Value of variable
    """
    val: None = None
    if var[0] == 'GF':
        val: Dict[str, str] = context.global_frame.get(var[1])
    elif var[0] == 'LF':
        if len(context.local_frame) == 0:
            exit_with_code(55, "Error: No local frame.")
        val: Dict[str, str] = context.local_frame[-1].get(var[1])
    elif var[0] == 'TF':
        if context.tmp_frame is None:
            exit_with_code(55, "Error: No temporary frame.")
        val: Dict[str, str] = context.tmp_frame.get(var[1])
    else:
        exit_with_code(52, "Error: Wrong variable type.")

    if val is None:
        exit_with_code(54, "Error: Variable doesn't exist.")
    return val


def exit_with_code(code: int, text: str) -> None:
    """
    Exit with error code and print error message.
    :param code: Int value of error code
    :param text: Error message
    :return: None
    """
    print(text, file=sys.stderr)
    sys.exit(code)


def remove_escape_seq(string: str) -> str:
    """
    Replace escape sequences with characters.
    :param string:  String with escape sequences
    :return: String with replaced escape sequences
    """
    if len(string) != 0:
        string: str = re.sub(r'\\(\d{3})', lambda match: chr(int(match.group(1))), string)
    return string


def check_arguments(args: Dict[str, Dict[str, str]], num_of_args: int) -> None:
    """
    Check if operation has correct number of arguments.
    :param args: List of arguments
    :param num_of_args: Number of operation arguments
    :return: None
    """
    if len(args)-1 != num_of_args:
        exit_with_code(32, "Error: Wrong number of arguments.")
    arg_cnt: int = 1
    for arg in range(1, num_of_args+1):
        if f"arg{arg_cnt}" not in args.keys():
            exit_with_code(32, "Error: Wrong argument name.")
        arg_cnt += 1
