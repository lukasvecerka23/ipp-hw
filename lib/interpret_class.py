from argparse import ArgumentParser
import sys
from typing import Dict, List, Union, AnyStr
from xml.etree.ElementTree import Element
from xml.etree import ElementTree
from lib.op_factory import OperationFactory
from lib.operations import Operation
from lib.utils import exit_with_code
import re


class Interpret:
    def __init__(self):
        self.__op_factory: OperationFactory = OperationFactory()
        self.__xml_parser: XMLParser = XMLParser()
        self.__arg_parser: ArgumentParser = ArgumentParser()

        self.source_path: None = None
        self.input_path: None = None
        self.input_lines: None = None
        self.input_line: int = 0
        self.op_cnt: int = 0
        self.global_frame: Dict[str, Dict[str, str]] = {}
        self.local_frame: List[Dict[str, Dict[str, str]]] = []
        self.tmp_frame: None = None
        self.label_dict: Dict[str, int] = {}
        self.stack: List[Dict[str, Union[str, int, bool]]] = []
        self.call_stack: List[int] = []
        self.operation_list: List[Dict[str, Union[Dict[str, str], str]]] = []

    def interpret(self):
        self.__parse_args()
        self.operation_list: List[Dict[str, Union[Dict[str, str], str]]] = self.__xml_parser.parse_xml(self.source_path)
        if self.input_path is not None:
            self.__parse_input()
        self.__register_labels()
        self.__execute_operations()

    def __parse_args(self) -> None:
        if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
            if len(sys.argv) > 2:
                exit_with_code(10, "Error: Wrong number of arguments.")
        self.__arg_parser.description = "Python script for interpreting XML file which is generated from IPPcode23."
        self.__arg_parser.add_argument('--source', type=str, metavar='<file>', help="Specify the source file.")
        self.__arg_parser.add_argument('--input', type=str, metavar='<file>', help="Specify the input file.")

        args = self.__arg_parser.parse_args()

        if not args.source and not args.input:
            print("Error: At least one of --source or --input must be specified.")
            self.__arg_parser.print_help()
            sys.exit(10)

        if args.source:
            self.source_path: str = args.source

        if args.input:
            self.input_path: str = args.input

    def __register_labels(self) -> None:
        op_cnt: int = 0
        for op in self.operation_list:
            if op['opcode'] == 'LABEL':
                label_name: int = self.label_dict.get(op['arg1']['value'])
                if label_name is not None:
                    exit_with_code(52, "Error: Label already exists.")
                self.label_dict[op['arg1']['value']] = op_cnt
            op_cnt += 1

    def __parse_input(self) -> None:
        try:
            with open(self.input_path, 'r') as file:
                self.input_lines = file.readlines()
        except FileNotFoundError:
            exit_with_code(11, "Error: Input file does not exist.")
        except PermissionError:
            exit_with_code(11, "Error: Input file is not readable.")

    def __execute_operations(self) -> None:
        while self.op_cnt < len(self.operation_list):
            operation: Operation = self.__op_factory.create_operation(self.operation_list[self.op_cnt]['opcode'])
            operation.check_args(self.operation_list[self.op_cnt])
            operation.execute(self)


class XMLParser:
    def parse_xml(self, source_path: str) -> List[Dict[str, Union[Dict[str, str], str]]]:
        """
        Go through the XML element tree, check if the XML file is well-formed and return the list of operations.
        :param source_path: string of the path to the XML file
        :return: list of operations
        """
        try:
            if source_path is not None:
                tree: ElementTree = ElementTree.parse(source_path)
                root: Element = tree.getroot()
            else:
                stdin: AnyStr = sys.stdin.read()
                root: Element = ElementTree.fromstring(stdin)
        except ElementTree.ParseError:
            exit_with_code(31, "Error: XML file is not well-formed.")
        except FileNotFoundError:
            exit_with_code(11, "Error: Source file does not exist.")
        except PermissionError:
            exit_with_code(11, "Error: Source file is not readable.")

        op_dict: Dict = {}
        for child in root:
            opcode: str = child.attrib.get('opcode')
            order: str = child.attrib.get('order')
            if opcode is None or order is None:
                exit_with_code(32, "Error: XML file is not well-formed.")
            order: str = order.strip()
            if child.tag != 'instruction':
                exit_with_code(32, "Error: XML file is not well-formed.")
            if order in op_dict.keys():
                exit_with_code(32, "Error: XML file is not well-formed.")
            if not order.isdecimal() or int(order) <= 0:
                exit_with_code(32, "Error: XML file is not well-formed.")
            op_dict[order]: Dict[str, str] = {"opcode": opcode}

            for child2 in child:
                arg_type = child2.attrib.get('type')
                if arg_type is None:
                    exit_with_code(32, "Error: XML file is not well-formed.")
                if re.match(r'^arg[1-3]$', child2.tag) is None:
                    exit_with_code(32, "Error: XML file is not well-formed.")
                if child2.tag in op_dict[order].keys():
                    exit_with_code(32, "Error: XML file is not well-formed.")
                arg: Dict[str, str] = {"type": arg_type, "value": child2.text}
                op_dict[order][child2.tag]: Dict[str, Dict[str, str] | str] = arg
        # sort the dictionary by the order of the operations
        op_dict: Dict[str, Dict[str, str] | str] = {key: value for key, value in sorted(op_dict.items(), key=lambda item: int(item[0]))}
        return list(op_dict.values())
