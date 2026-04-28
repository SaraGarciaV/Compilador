from sly import Parser
from lexer import CompilerLexer

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens

    # ── Programa general ──────────────────────────────────────────
    @_('PROGRAM MAIN LBRACE var_section BEGIN SEMICOLON statement_list END SEMICOLON RBRACE')
    def program(self, p):
        print("[SINTÁCTICO] Programa válido")

    # ── Declaración de variables ──────────────────────────────────
    @_('VAR id_list COLON type SEMICOLON')
    def var_section(self, p):
        pass

    @_('id_list COMMA ID')
    def id_list(self, p):
        pass

    @_('ID')
    def id_list(self, p):
        pass

    @_('INT', 'FLOAT', 'STRING')
    def type(self, p):
        pass

    # ── Lista de estatutos ────────────────────────────────────────
    @_('statement_list statement')
    def statement_list(self, p):
        pass

    @_('empty')
    def statement_list(self, p):
        pass

    @_('')
    def empty(self, p):
        pass

    # ── Estatutos ─────────────────────────────────────────────────
    @_('assignment')
    def statement(self, p):
        pass

    @_('writeln_stmt')
    def statement(self, p):
        pass

    @_('if_stmt')
    def statement(self, p):
        pass

    @_('for_stmt')
    def statement(self, p):
        pass

    @_('while_stmt')
    def statement(self, p):
        pass

    # ── Asignaciones ──────────────────────────────────────────────
    @_('ID ASSIGN expression SEMICOLON')
    def assignment(self, p):
        pass

    @_('ID OP_INC SEMICOLON')
    def assignment(self, p):
        pass

    @_('ID OP_DEC SEMICOLON')
    def assignment(self, p):
        pass

    # ── writeln ───────────────────────────────────────────────────
    @_('WRITELN LPAREN STR_LIT RPAREN SEMICOLON')
    def writeln_stmt(self, p):
        pass

    @_('WRITELN LPAREN expression RPAREN SEMICOLON')
    def writeln_stmt(self, p):
        pass

    # ── if / else ─────────────────────────────────────────────────
    @_('IF LPAREN expression RPAREN THEN LBRACE statement_list RBRACE')
    def if_stmt(self, p):
        pass

    @_('IF LPAREN expression RPAREN THEN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE')
    def if_stmt(self, p):
        pass

    # ── for ───────────────────────────────────────────────────────
    @_('FOR LPAREN assignment expression SEMICOLON ID OP_INC RPAREN LBRACE statement_list RBRACE')
    def for_stmt(self, p):
        pass

    # ── while ─────────────────────────────────────────────────────
    @_('WHILE LPAREN expression RPAREN DO LBRACE statement_list RBRACE')
    def while_stmt(self, p):
        pass

    # ── Expresiones ───────────────────────────────────────────────
    @_('logic_expr')
    def expression(self, p):
        pass

    @_('logic_expr AND rel_expr')
    def logic_expr(self, p):
        pass

    @_('logic_expr OR rel_expr')
    def logic_expr(self, p):
        pass

    @_('rel_expr')
    def logic_expr(self, p):
        pass

    @_('arith_expr OP_GT arith_expr')
    def rel_expr(self, p):
        pass

    @_('arith_expr OP_LT arith_expr')
    def rel_expr(self, p):
        pass

    @_('arith_expr OP_GTE arith_expr')
    def rel_expr(self, p):
        pass

    @_('arith_expr OP_LTE arith_expr')
    def rel_expr(self, p):
        pass

    @_('arith_expr OP_EQ arith_expr')
    def rel_expr(self, p):
        pass

    @_('arith_expr OP_NEQ arith_expr')
    def rel_expr(self, p):
        pass

    @_('arith_expr')
    def rel_expr(self, p):
        pass

    @_('arith_expr OP_SUM term')
    def arith_expr(self, p):
        pass

    @_('arith_expr OP_SUB term')
    def arith_expr(self, p):
        pass

    @_('term')
    def arith_expr(self, p):
        pass

    @_('term OP_MUL factor')
    def term(self, p):
        pass

    @_('term OP_DIV factor')
    def term(self, p):
        pass

    @_('factor')
    def term(self, p):
        pass

    @_('LPAREN expression RPAREN')
    def factor(self, p):
        pass

    @_('INT_LIT')
    def factor(self, p):
        pass

    @_('FLOAT_LIT')
    def factor(self, p):
        pass

    @_('STR_LIT')
    def factor(self, p):
        pass

    @_('ID')
    def factor(self, p):
        pass

    # ── Errores ───────────────────────────────────────────────────
    def error(self, p):
        if p:
            print(f"[SINTÁCTICO] Error cerca de '{p.value}' (línea {p.lineno})")
        else:
            print("[SINTÁCTICO] Error: fin de archivo inesperado")



