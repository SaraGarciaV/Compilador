import sys
from lexer import CompilerLexer
from parser import CompilerParser
from semantic import AnalizadorSemantico
from codegen import GeneradorCodigo

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python main.py <archivo>')
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    lexer  = CompilerLexer()
    parser = CompilerParser()
    ast    = parser.parse(lexer.tokenize(source))

    semantico = AnalizadorSemantico()
    semantico.analizar(ast)

    if not semantico.errores:
        codegen = GeneradorCodigo()
        codegen.generar(ast)