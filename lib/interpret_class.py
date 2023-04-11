import argparse
import sys
import xml.etree.ElementTree as ET
from lib.op_factory import OpFactory
from lib.utils import exit_with_code


class Interpret:
    def __init__(self):
        self.source_path = None
        self.input_path = None
        self.input_lines = None
        self.input_line = 0
        self.arg_parser = None
        self.operation_list = []
        self.op_cnt = 0
        self.global_frame = {}
        self.local_frame = []
        self.tmp_frame = None
        self.label_dict = {}
        self.stack = []
        self.call_stack = []
        self.op_factory = OpFactory()

    def interpret(self):
        if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
            if len(sys.argv) > 2:
                print("Error: --help cannot be combined with other arguments.")
                sys.exit(10)
        self.arg_parser = argparse.ArgumentParser(
            description="Python script for interpreting XML file which is generated from IPPcode23.")
        self.arg_parser.add_argument('--source', type=str, metavar='<file>', help="Specify the source file.")
        self.arg_parser.add_argument('--input', type=str, metavar='<file>', help="Specify the input file.")

        args = self.arg_parser.parse_args()
        self.parse_args(args)
        self.parse_xml()
        if self.input_path is not None:
            self.parse_input()
        self.register_labels()
        self.execute_operations()

    def parse_args(self, args):

        if not args.source and not args.input:
            print("Error: At least one of --source or --input must be specified.")
            self.arg_parser.print_help()
            sys.exit(10)

        if args.source:
            self.source_path = args.source

        if args.input:
            self.input_path = args.input

    def register_labels(self):
        op_cnt = 0
        for op in self.operation_list:
            if op['opcode'] == 'LABEL':
                label_name = self.label_dict.get(op['arg1']['value'])
                if label_name is not None:
                    exit_with_code(52, "Error: Label already exists.")
                self.label_dict[op['arg1']['value']] = op_cnt
            op_cnt += 1

    def parse_xml(self):
        try:
            if self.source_path is not None:
                tree = ET.parse(self.source_path)
                root = tree.getroot()
            else:
                stdin = sys.stdin.read()
                root = ET.fromstring(stdin)
        except ET.ParseError:
            exit_with_code(31, "Error: XML file is not well-formed.")
        op_dict = {}
        for child in root:
            op_dict[child.attrib['order']] = {"opcode": child.attrib['opcode']}
            for child2 in child:
                arg = {"type": child2.attrib['type'], "value": child2.text}
                op_dict[child.attrib['order']][child2.tag] = arg
        op_dict = {key: value for key, value in sorted(op_dict.items(), key=lambda item: int(item[0]))}
        self.operation_list = list(op_dict.values())

    def parse_input(self):
        with open(self.input_path, 'r') as file:
            self.input_lines = file.readlines()

    def execute_operations(self):
        while self.op_cnt < len(self.operation_list):
            operation = self.op_factory.create_operation(self.operation_list[self.op_cnt]['opcode'])
            operation.execute(operation, self)
