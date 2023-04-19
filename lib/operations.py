from abc import ABC, abstractmethod
from lib.utils import *
import sys
from typing import Dict


class Operation(ABC):
    @abstractmethod
    def execute(self, context) -> None:
        pass

    @abstractmethod
    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        pass


class Move(Operation):
    def execute(self, context) -> None:
        data: Dict[str, Dict[str, str]] = context.operation_list[context.op_cnt]
        arg1: List[str] = data['arg1']['value'].strip().split('@')
        arg2: Dict[str, str] = data['arg2']
        val, val_type = get_symb_value(arg2, context)
        if val_type is None:
            exit_with_code(56, "Error: Variable not initialized.")
        store_val_to_var(arg1, val, val_type, context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 2)


class Createframe(Operation):
    def execute(self, context) -> None:
        context.tmp_frame = {}
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 0)


class Pushframe(Operation):
    def execute(self, context) -> None:
        if context.tmp_frame is None:
            exit_with_code(55, "Error: No frame to push.")
        context.local_frame.append(context.tmp_frame)
        context.tmp_frame = None
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 0)


class Popframe(Operation):
    def execute(self, context) -> None:
        if len(context.local_frame) == 0:
            exit_with_code(55, "Error: No frame to pop.")
        context.tmp_frame = context.local_frame.pop()
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 0)


class Defvar(Operation):
    def execute(self, context) -> None:
        data: Dict[str, Dict[str, str]] = context.operation_list[context.op_cnt]
        var: Dict[str, None] = {'type': None, 'value': None}
        arg: List[str] = data['arg1']['value'].strip().split('@')
        if arg[0] == 'GF':
            if arg[1] in context.global_frame.keys():
                exit_with_code(52, "Error: Variable already defined.")
            context.global_frame[arg[1]] = var
        elif arg[0] == 'LF':
            if len(context.local_frame) == 0:
                exit_with_code(55, "Error: No local frame.")
            if arg[1] in context.local_frame[-1].keys():
                exit_with_code(52, "Error: Variable already defined.")
            context.local_frame[-1][arg[1]] = var
        elif arg[0] == 'TF':
            if context.tmp_frame is None:
                exit_with_code(55, "Error: No temporary frame.")
            if arg[1] in context.tmp_frame.keys():
                exit_with_code(52, "Error: Variable already defined.")
            context.tmp_frame[arg[1]] = var
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Call(Operation):
    def execute(self, context) -> None:
        context.call_stack.append(context.op_cnt)
        label_name: str = context.operation_list[context.op_cnt]['arg1']['value']
        if label_name not in context.label_dict.keys():
            exit_with_code(52, "Error: Label does not exist.")
        context.op_cnt = context.label_dict[label_name]

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Return(Operation):
    def execute(self, context) -> None:
        if len(context.call_stack) == 0:
            exit_with_code(56, "Error: No function to return.")
        context.op_cnt = context.call_stack.pop() + 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 0)


class Pushs(Operation):
    def execute(self, context) -> None:
        symb_val, symb_type = get_symb_value(context.operation_list[context.op_cnt]['arg1'], context)
        if symb_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        context.stack.append({'type': symb_type, 'value': symb_val})
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Pops(Operation):
    def execute(self, context) -> None:
        if len(context.stack) == 0:
            exit_with_code(56, "Error: No data to pop.")
        data: Dict[str, Union[str, int, bool]] = context.stack.pop()
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].split('@')
        store_val_to_var(var, data['value'], data['type'], context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Add(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'int' or symb2_type != 'int':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val + symb2_val, 'int', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Sub(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'int' or symb2_type != 'int':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val - symb2_val, 'int', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Mul(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'int' or symb2_type != 'int':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val * symb2_val, 'int', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class IDiv(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'int' or symb2_type != 'int':
            exit_with_code(53, "Error: Wrong types.")
        if symb2_val == 0:
            exit_with_code(57, "Error: Division by zero.")
        store_val_to_var(var, symb1_val // symb2_val, 'int', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Lt(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != symb2_type or symb1_type == 'nil':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val < symb2_val, 'bool', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Gt(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != symb2_type or symb1_type == 'nil':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val > symb2_val, 'bool', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Eq(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != symb2_type and symb1_type != 'nil' and symb2_type != 'nil':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val == symb2_val, 'bool', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class And(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'bool' or symb2_type != 'bool':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val and symb2_val, 'bool', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Or(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'bool' or symb2_type != 'bool':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val or symb2_val, 'bool', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Not(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        if symb1_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'bool':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, not symb1_val, 'bool', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 2)


class Int2char(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        if symb1_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'int':
            exit_with_code(53, "Error: Wrong types.")
        try:
            store_val_to_var(var, chr(symb1_val), 'string', context)
        except ValueError:
            exit_with_code(58, "Error: Wrong value.")
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 2)


class Stri2char(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'string' or symb2_type != 'int':
            exit_with_code(53, "Error: Wrong types.")
        if symb2_val < 0 or symb2_val >= len(symb1_val):
            exit_with_code(58, "Error: Wrong value.")
        try:
            store_val_to_var(var, ord(symb1_val[symb2_val]), 'int', context)
        except IndexError:
            exit_with_code(58, "Error: Wrong value.")
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Read(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        val_type: str = context.operation_list[context.op_cnt]['arg2']['value']
        input_val: None = None
        if val_type not in ['int', 'bool', 'string', 'nil']:
            exit_with_code(32, "Error: Wrong type of second operand.")
        if context.input_path is None:
            try:
                input_val: str = input()
            except EOFError:
                input_val: str = 'nil'
                val_type: str = 'nil'
        else:
            if context.input_line < len(context.input_lines):
                input_val: str = context.input_lines[context.input_line]
                input_val: str = input_val.replace('\n', '')
                context.input_line += 1
            else:
                input_val: str = 'nil'
                val_type: str = 'nil'

        if val_type == 'int' and input_val is not None:
            try:
                input_val: int = int(input_val)
            except ValueError:
                val_type: str = 'nil'
                input_val: str = 'nil'
        elif val_type == 'bool' and input_val is not None:
            if input_val.lower() == 'true':
                input_val: bool = True
            else:
                input_val: bool = False
        elif val_type == 'string':
            input_val: str = str(input_val)
        store_val_to_var(var, input_val, val_type, context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 2)


class Write(Operation):
    def execute(self, context) -> None:
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg1']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        if symb1_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type == 'bool':
            if symb1_val:
                string_to_print: str = 'true'
            else:
                string_to_print: str = 'false'
        elif symb1_type == 'nil':
            string_to_print: str = ''
        else:
            string_to_print: str = symb1_val
        print(string_to_print, end='')
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Concat(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'string' or symb2_type != 'string':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, symb1_val + symb2_val, 'string', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Strlen(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        if symb1_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'string':
            exit_with_code(53, "Error: Wrong types.")
        store_val_to_var(var, len(symb1_val), 'int', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 2)


class Getchar(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != 'string' or symb2_type != 'int':
            exit_with_code(53, "Error: Wrong types.")
        if symb2_val < 0 or symb2_val >= len(symb1_val):
            exit_with_code(58, "Error: Wrong value.")
        try:
            store_val_to_var(var, symb1_val[symb2_val], 'string', context)
        except IndexError:
            exit_with_code(58, "Error: Wrong value.")
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Setchar(Operation):
    def execute(self, context) -> None:
        var: Dict[str, str] = context.operation_list[context.op_cnt]['arg1']
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        var_val, var_type = get_symb_value(var, context)
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if var_type is None or symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if var_type != 'string' or symb1_type != 'int' or symb2_type != 'string':
            exit_with_code(53, "Error: Wrong types.")
        if symb1_val < 0 or symb1_val > len(var_val)-1 or len(symb2_val) == 0:
            exit_with_code(58, "Error: Wrong value.")
        try:
            store_val_to_var(var['value'].split('@'), f'{var_val[:symb1_val]}{symb2_val[:len(var_val)-symb1_val]}{var_val[symb1_val+len(symb2_val)::]}', 'string', context)
        except IndexError:
            exit_with_code(58, "Error: Wrong value.")
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Type(Operation):
    def execute(self, context) -> None:
        var: List[str] = context.operation_list[context.op_cnt]['arg1']['value'].strip().split('@')
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        if symb1_type is None:
            store_val_to_var(var, '', 'string', context)
        else:
            store_val_to_var(var, symb1_type, 'string', context)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 2)


class Label(Operation):
    def execute(self, context) -> None:
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Jump(Operation):
    def execute(self, context) -> None:
        label: str = context.operation_list[context.op_cnt]['arg1']['value']
        if context.label_dict.get(label) is None:
            exit_with_code(52, "Error: Label does not exist.")
        context.op_cnt = context.label_dict[label]

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Jumpifeq(Operation):
    def execute(self, context) -> None:
        label = context.operation_list[context.op_cnt]['arg1']['value']
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != symb2_type and symb1_type != 'nil' and symb2_type != 'nil':
            exit_with_code(53, "Error: Wrong types.")
        if context.label_dict.get(label) is None:
            exit_with_code(52, "Error: Label does not exist.")
        if symb1_val == symb2_val:
            context.op_cnt = context.label_dict[label]
        else:
            context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)



class Jumpifneq(Operation):
    def execute(self, context) -> None:
        label = context.operation_list[context.op_cnt]['arg1']['value']
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg2']
        symb2: Dict[str, str] = context.operation_list[context.op_cnt]['arg3']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        symb2_val, symb2_type = get_symb_value(symb2, context)
        if symb1_type is None or symb2_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if symb1_type != symb2_type and symb1_type != 'nil' and symb2_type != 'nil':
            exit_with_code(53, "Error: Wrong types.")
        if context.label_dict.get(label) is None:
            exit_with_code(52, "Error: Label does not exist.")
        if symb1_val != symb2_val:
            context.op_cnt = context.label_dict[label]
        else:
            context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 3)


class Exit(Operation):
    def execute(self, context) -> None:
        exit_code: Dict[str, str] = context.operation_list[context.op_cnt]['arg1']
        val, val_type = get_symb_value(exit_code, context)
        if val_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        if val_type != 'int':
            exit_with_code(53, "Error: Invalid exit code type.")
        if val < 0 or val > 49:
            exit_with_code(57, "Error: Invalid exit code.")
        sys.exit(val)

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Dprint(Operation):
    def execute(self, context) -> None:
        symb1: Dict[str, str] = context.operation_list[context.op_cnt]['arg1']
        symb1_val, symb1_type = get_symb_value(symb1, context)
        if symb1_type is None:
            exit_with_code(56, "Error: Variable uninitialized.")
        print(symb1_val, file=sys.stderr)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 1)


class Break(Operation):
    def execute(self, context) -> None:
        print("Instruction counter:", context.op_cnt)
        print("Data stack:", context.data_stack)
        print("Call stack:", context.call_stack)
        print("Actual Local frames:", context.local_frames[-1])
        print("Global frame:", context.global_frame)
        print("Temporary frame:", context.temp_frame)
        context.op_cnt += 1

    def check_args(self, data: Dict[str, Dict[str, str]]) -> None:
        check_arguments(data, 0)
