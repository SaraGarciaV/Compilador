from sly import Parser
from lexer import CompilerLexer


class CompilerParser(Parser):
    tokens = CompilerLexer.tokens

    # ─── Precedencia de operadores (menor a mayor) ────────────
    precedence = (
        ('left', AND),
        ('left', LT, GT, GTE),
        ('left', PLUS, MINUS),
        ('left', TIMES),
    )

    # ══════════════════════════════════════════════════════════
    # PROGRAMA
    # ══════════════════════════════════════════════════════════

    @_('PROGRAM ID LBRACE var_list bloque RBRACE')
    def programa(self, p):
        return ('programa', p.ID, p.var_list, p.bloque)

    @_('PROGRAM ID LBRACE bloque RBRACE')
    def programa(self, p):
        return ('programa', p.ID, [], p.bloque)

    # ══════════════════════════════════════════════════════════
    # DECLARACIÓN DE VARIABLES
    # ══════════════════════════════════════════════════════════

    @_('var_list variables')
    def var_list(self, p):
        return p.var_list + [p.variables]

    @_('variables')
    def var_list(self, p):
        return [p.variables]

    @_('VAR declaracion_list COLON tipo SEMICOLON')
    def variables(self, p):
        return ('variables', p.declaracion_list, p.tipo)

    @_('declaracion_list COMMA declaracion')
    def declaracion_list(self, p):
        return p.declaracion_list + [p.declaracion]

    @_('declaracion')
    def declaracion_list(self, p):
        return [p.declaracion]

    @_('ID LBRACKET NUM_INT RBRACKET')
    def declaracion(self, p):
        return ('arreglo', p.ID, p.NUM_INT)

    @_('ID')
    def declaracion(self, p):
        return ('id', p.ID)

    @_('INT')
    def tipo(self, p):
        return 'int'

    @_('FLOAT')
    def tipo(self, p):
        return 'float'

    # ══════════════════════════════════════════════════════════
    # BLOQUE begin...end
    # ══════════════════════════════════════════════════════════

    @_('BEGIN SEMICOLON statement_list END SEMICOLON')
    def bloque(self, p):
        return ('bloque', p.statement_list)

    # ══════════════════════════════════════════════════════════
    # LISTA DE STATEMENTS
    # ══════════════════════════════════════════════════════════

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]

    # ══════════════════════════════════════════════════════════
    # STATEMENTS
    # ══════════════════════════════════════════════════════════

    @_('asignacion')
    def statement(self, p):
        return p.asignacion

    @_('decremento')
    def statement(self, p):
        return p.decremento

    @_('incremento')
    def statement(self, p):
        return p.incremento

    @_('if_stat')
    def statement(self, p):
        return p.if_stat

    @_('while_stat')
    def statement(self, p):
        return p.while_stat

    @_('for_stat')
    def statement(self, p):
        return p.for_stat

    @_('write_stat')
    def statement(self, p):
        return p.write_stat

    # ══════════════════════════════════════════════════════════
    # ASIGNACIÓN  id := expr ;  o  id[expr] := expr ;
    # ══════════════════════════════════════════════════════════

    @_('ID LBRACKET expresion RBRACKET ASSIGN expresion SEMICOLON')
    def asignacion(self, p):
        return ('asignacion_arr', p.ID, p.expresion0, p.expresion1)

    @_('ID ASSIGN expresion SEMICOLON')
    def asignacion(self, p):
        return ('asignacion', p.ID, p.expresion)

    # ══════════════════════════════════════════════════════════
    # DECREMENTO  id-- ;   INCREMENTO  id++ ;
    # ══════════════════════════════════════════════════════════

    @_('ID DECREMENT SEMICOLON')
    def decremento(self, p):
        return ('decremento', p.ID)

    @_('ID INCREMENT SEMICOLON')
    def incremento(self, p):
        return ('incremento', p.ID)

    # ══════════════════════════════════════════════════════════
    # WRITE
    # ══════════════════════════════════════════════════════════

    @_('WRITE LPAREN STRING RPAREN SEMICOLON')
    def write_stat(self, p):
        return ('write', ('string', p.STRING))

    @_('WRITE LPAREN expresion RPAREN SEMICOLON')
    def write_stat(self, p):
        return ('write', p.expresion)

    # ══════════════════════════════════════════════════════════
    # IF
    # ══════════════════════════════════════════════════════════

    @_('IF LPAREN condicion RPAREN THEN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE')
    def if_stat(self, p):
        return ('if', p.condicion, p.statement_list0, p.statement_list1)

    @_('IF LPAREN condicion RPAREN THEN LBRACE statement_list RBRACE')
    def if_stat(self, p):
        return ('if', p.condicion, p.statement_list, None)

    # ══════════════════════════════════════════════════════════
    # WHILE
    # ══════════════════════════════════════════════════════════

    @_('WHILE LPAREN condicion RPAREN DO LBRACE statement_list RBRACE')
    def while_stat(self, p):
        return ('while', p.condicion, p.statement_list)

    # ══════════════════════════════════════════════════════════
    # FOR
    # ══════════════════════════════════════════════════════════

    @_('FOR LPAREN ID ASSIGN expresion SEMICOLON condicion SEMICOLON ID INCREMENT RPAREN LBRACE statement_list RBRACE')
    def for_stat(self, p):
        return ('for', p.ID0, p.expresion, p.condicion, ('incremento', p.ID1), p.statement_list)

    @_('FOR LPAREN ID ASSIGN expresion SEMICOLON condicion SEMICOLON ID DECREMENT RPAREN LBRACE statement_list RBRACE')
    def for_stat(self, p):
        return ('for', p.ID0, p.expresion, p.condicion, ('decremento', p.ID1), p.statement_list)

    # ══════════════════════════════════════════════════════════
    # CONDICIÓN
    # ══════════════════════════════════════════════════════════

    @_('condicion AND condicion')
    def condicion(self, p):
        return ('and', p.condicion0, p.condicion1)

    @_('LPAREN condicion RPAREN')
    def condicion(self, p):
        return p.condicion

    @_('expresion GTE expresion')
    def condicion(self, p):
        return ('>=', p.expresion0, p.expresion1)

    @_('expresion GT expresion')
    def condicion(self, p):
        return ('>', p.expresion0, p.expresion1)

    @_('expresion LT expresion')
    def condicion(self, p):
        return ('<', p.expresion0, p.expresion1)

    # ══════════════════════════════════════════════════════════
    # EXPRESIÓN
    # ══════════════════════════════════════════════════════════

    @_('expresion PLUS termino')
    def expresion(self, p):
        return ('+', p.expresion, p.termino)

    @_('expresion MINUS termino')
    def expresion(self, p):
        return ('-', p.expresion, p.termino)

    @_('expresion TIMES termino')
    def expresion(self, p):
        return ('*', p.expresion, p.termino)

    @_('termino')
    def expresion(self, p):
        return p.termino

    # ══════════════════════════════════════════════════════════
    # TÉRMINO
    # ══════════════════════════════════════════════════════════

    @_('ID LBRACKET expresion RBRACKET')
    def termino(self, p):
        return ('acceso_arr', p.ID, p.expresion)

    @_('LPAREN expresion RPAREN')
    def termino(self, p):
        return p.expresion

    @_('ID')
    def termino(self, p):
        return ('id', p.ID)

    @_('NUM_INT')
    def termino(self, p):
        return ('num_int', p.NUM_INT)

    @_('NUM_FLOAT')
    def termino(self, p):
        return ('num_float', p.NUM_FLOAT)

    # ══════════════════════════════════════════════════════════
    # MANEJO DE ERRORES
    # ══════════════════════════════════════════════════════════

    def error(self, p):
        if p:
            print(f'[Parser] Error sintáctico en línea {p.lineno}: token inesperado "{p.value}"')
        else:
            print('[Parser] Error sintáctico: fin de archivo inesperado')