# main.py
import sys
from lexer import tokenize
from parser import Parser
from transformer import transform_node
from codegen import generate_code

def main(js_code: str):
    tokens = tokenize(js_code)
    parser = Parser(tokens)
    ast = parser.parse()
    python_lines = [transform_node(node) for node in ast]
    python_code = generate_code(python_lines)
    print(python_code)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py input.js")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        js_code = f.read()
    main(js_code)
