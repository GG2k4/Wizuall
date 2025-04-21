import argparse
import sys
from wizual_interpreter import run, EvalError
from wizual_lexer import LexError
from wizual_parser import parser as ply_parser
from wizual_codegen import generate_py


def execute_all(buffered_stmts):
    code = "".join(buffered_stmts)
    return run(code)


def repl():
    print("Welcome to WizuAll REPL. Type your statements ending with ';'. Ctrl-D to exit.")
    buffered = []
    while True:
        try:
            line = input("WizuAll> ")
        except EOFError:
            print()
            break
        if not line.strip():
            continue
        buffered.append(line + "\n")
        if not line.strip().endswith(';'):
            continue
        try:
            execute_all(buffered)
        except (LexError, SyntaxError, EvalError, NameError, TypeError, ValueError) as e:
            print("Error:", e)
        buffered.clear()
    print("Goodbye!")


def main():
    parser = argparse.ArgumentParser(prog="wizuall")
    parser.add_argument('file', nargs='?', help="WizuAll source file to execute", default='example.viz')
    parser.add_argument('--compile', '-c', metavar='OUT.py', help="Generate a Python script from the WizuAll source", default='output.py')
    args = parser.parse_args()
    if args.file:
        try:
            with open(args.file) as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: file '{args.file}' not found.")
            sys.exit(1)
        if args.compile:
            try:
                ast = ply_parser.parse(code)
                generate_py(ast, args.compile)
                print(f"Generated {args.compile}")
            except Exception as e:
                print("Error during compilation:", e)
                sys.exit(1)
        else:
            try:
                sym = run(code)
                print("Symbol Table:")
                print(sym)
            except (LexError, SyntaxError, EvalError, NameError, TypeError, ValueError) as e:
                print("Error:", e)
                sys.exit(1)
    else:
        repl()


if __name__ == "__main__":
    main()
