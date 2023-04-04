import argparse
import sys
import xml.etree.ElementTree as ET

def parse_args(args):
    if not args.source and not args.input:
        print("Error: At least one of --source or --input must be specified.")
        parser.print_help()
        sys.exit(10)

    if args.source:
        print(f"Source file: {args.source}")
        tree = ET.parse(args.source)
        root = tree.getroot()
        for child in root:
            for child2 in child:
                print(child2.tag, child2.attrib, child2.text)
            print(child.tag, child.attrib)

    if args.input:
        print(f"Input file: {args.input}")

if __name__ == "__main__":
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        if len(sys.argv) > 2:
            print("Error: --help cannot be combined with other arguments.")
            sys.exit(10)

    parser = argparse.ArgumentParser(description="Python script for interpreting XML file which is generated from IPPcode23.")

    parser.add_argument('--source', type=str, metavar='<file>', help="Specify the source file.")
    parser.add_argument('--input', type=str, metavar='<file>', help="Specify the input file.")

    args = parser.parse_args()
    parse_args(args)
