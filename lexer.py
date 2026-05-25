from sly import Lexer

class CompilerLexer(Lexer):

    # ─── Tokens ───────────────────────────────────────────────
    tokens = {
        # Palabras reservadas
        PROGRAM, VAR, INT, FLOAT, BEGIN, END,
        IF, THEN, ELSE, WHILE, DO, FOR, WRITE, AND,
        FUNCTION,

        # Identificadores y literales
        ID, NUM_FLOAT, NUM_INT, STRING,

        # Operadores de asignación y unarios
        ASSIGN, DECREMENT, INCREMENT,

        # Operadores relacionales
        GTE, GT, LT,

        # Operadores aritméticos
        PLUS, MINUS, TIMES,

        # Delimitadores
        SEMICOLON, COLON, COMMA,
        LPAREN, RPAREN,
        LBRACE, RBRACE,
        LBRACKET, RBRACKET,
    }

    # ─── Ignorar espacios y saltos de línea ───────────────────
    ignore = ' \t'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # ─── Ignorar comentarios de línea (//) ────────────────────
    ignore_comment = r'//.*'

    # ─── Palabras reservadas ──────────────────────────────────
    # Deben ir ANTES que ID para que SLY las reconozca primero
    ID['program']   = PROGRAM
    ID['var']       = VAR
    ID['int']       = INT
    ID['float']     = FLOAT
    ID['begin']     = BEGIN
    ID['end']       = END
    ID['if']        = IF
    ID['then']      = THEN
    ID['else']      = ELSE
    ID['while']     = WHILE
    ID['do']        = DO
    ID['for']       = FOR
    ID['write']     = WRITE
    ID['and']       = AND
    ID['function']  = FUNCTION

    # ─── Literales ────────────────────────────────────────────
    # NUM_FLOAT antes que NUM_INT para que no consuma solo la parte entera
    @_(r'\d+\.\d*')
    def NUM_FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def NUM_INT(self, t):
        t.value = int(t.value)
        return t

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        return t

    @_(r'"[^"]*"')
    def STRING(self, t):
        t.value = t.value[1:-1]  # quita las comillas
        return t

    # ─── Operadores (los de 2 chars ANTES que los de 1 char) ──
    ASSIGN      = r':='
    DECREMENT   = r'--'
    INCREMENT   = r'\+\+'
    GTE         = r'>='
    GT          = r'>'
    LT          = r'<'
    PLUS        = r'\+'
    MINUS       = r'-'
    TIMES       = r'\*'

    # ─── Delimitadores ────────────────────────────────────────
    SEMICOLON   = r';'
    COLON       = r':'
    COMMA       = r','
    LPAREN      = r'\('
    RPAREN      = r'\)'
    LBRACE      = r'\{'
    RBRACE      = r'\}'
    LBRACKET    = r'\['
    RBRACKET    = r'\]'

    # ─── Manejo de errores ────────────────────────────────────
    def error(self, t):
        print(f'[Lexer] Línea {self.lineno}: carácter ilegal "{t.value[0]}"')
        self.index += 1