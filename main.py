from lexer import CompilerLexer
from parser import CompilerParser

lexer  = CompilerLexer()
parser = CompilerParser()

code = '''
program main{
    var a,b : int;
    begin;
        a := 5;
        b := a + 3;
        writeln("hola");
    end;
}
'''

parser.parse(lexer.tokenize(code))