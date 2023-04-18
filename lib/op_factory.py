from lib.operations import *


class OperationFactory:
    """
    Factory for creating operations.
    By given operation name, it returns the operation class.
    """
    def __init__(self):
        self.operations: Dict[str, Operation] = {
            "MOVE": Move,
            "CREATEFRAME": Createframe,
            "PUSHFRAME": Pushframe,
            "POPFRAME": Popframe,
            "DEFVAR": Defvar,
            "CALL": Call,
            "RETURN": Return,
            "PUSHS": Pushs,
            "POPS": Pops,
            "ADD": Add,
            "SUB": Sub,
            "MUL": Mul,
            "IDIV": IDiv,
            "LT": Lt,
            "GT": Gt,
            "EQ": Eq,
            "AND": And,
            "OR": Or,
            "NOT": Not,
            "INT2CHAR": Int2char,
            "STRI2INT": Stri2char,
            "READ": Read,
            "WRITE": Write,
            "CONCAT": Concat,
            "STRLEN": Strlen,
            "GETCHAR": Getchar,
            "SETCHAR": Setchar,
            "TYPE": Type,
            "LABEL": Label,
            "JUMP": Jump,
            "JUMPIFEQ": Jumpifeq,
            "JUMPIFNEQ": Jumpifneq,
            "EXIT": Exit,
            "DPRINT": Dprint,
            "BREAK": Break
        }

    def create_operation(self, operation: str) -> Operation:
        operation: Operation = self.operations.get(operation.upper())
        if operation is None:
            exit_with_code(32, "Error: Unknown operation.")
        return operation
