from lib.interpret_class import Interpret
import sys

if __name__ == "__main__":
    interpret = Interpret()
    interpret.interpret()
    sys.stderr.close()
