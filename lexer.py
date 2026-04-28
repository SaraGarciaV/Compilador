from sly import Lexer

class CompilerLexer(Lexer):

    # Palabras reservadas
    tokens = {
        PROGRAM, MAIN, VAR, INT, FLOAT, STRING,
        BEGIN, END,
        IF, THEN, ELSE,
        FOR, WHILE, DO,
        WRITELN,
        AND, OR,
        ID,
        INT_LIT, FLOAT_LIT, STR_LIT,
        ASSIGN,
        OP_INC, OP_DEC,
        OP_GTE, OP_LTE, OP_EQ, OP_NEQ,
        OP_GT, OP_LT,
        OP_SUM, OP_SUB, OP_MUL, OP_DIV,
        LBRACE, RBRACE,
        LPAREN, RPAREN,
        SEMICOLON, COLON, COMMA,
    }

    # Ignorar espacios y saltos de línea
    ignore = ' \t\r\n'

    # Palabras reservadas (se revisan antes que ID)
    PROGRAM  = r'program'
    MAIN     = r'main'
    VAR      = r'var'
    INT      = r'int'
    FLOAT    = r'float'
    STRING   = r'string'
    BEGIN    = r'begin'
    END      = r'end'
    IF       = r'if'
    THEN     = r'then'
    ELSE     = r'else'
    FOR      = r'for'
    WHILE    = r'while'
    DO       = r'do'
    WRITELN  = r'writeln'
    AND      = r'and'
    OR       = r'or'

    # Identificador (debe ir DESPUÉS de las palabras reservadas)
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # Literales
    FLOAT_LIT = r'\d+\.\d+'
    INT_LIT   = r'\d+'
    STR_LIT   = r'"[^"]*"'

    # Operadores de dos caracteres (van antes que los de uno)
    OP_INC  = r'\+\+'
    OP_DEC  = r'--'
    OP_GTE  = r'>='
    OP_LTE  = r'<='
    OP_EQ   = r'=='
    OP_NEQ  = r'!='
    ASSIGN  = r':='

    # Operadores de un carácter
    OP_GT  = r'>'
    OP_LT  = r'<'
    OP_SUM = r'\+'
    OP_SUB = r'-'
    OP_MUL = r'\*'
    OP_DIV = r'/'

    # Delimitadores
    LBRACE    = r'\{'
    RBRACE    = r'\}'
    LPAREN    = r'\('
    RPAREN    = r'\)'
    SEMICOLON = r';'
    COLON     = r':'
    COMMA     = r','

    def error(self, t):
        print(f"[LÉXICO] Carácter ilegal: '{t.value[0]}' en posición {self.index}")
        self.index += 1
        