import sys
from lexer import CompilerLexer

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python main.py <archivo>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    lexer = CompilerLexer()
    for tok in lexer.tokenize(source):
        print(tok)