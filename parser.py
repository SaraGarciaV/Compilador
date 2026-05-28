from sly import Parser
from lexer import CompilerLexer

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens

    # ─── Precedencia de operadores (menor a mayor) ────────────
    precedence = (
        ('left', OR),
        ('left', AND),
        ('left', EQ, NE),
        ('left', LT, GT, GTE, LTE),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE, MOD),
        ('right', UNARY_MINUS),
    )

    # ══════════════════════════════════════════════════════════
    # PROGRAMA
    # ══════════════════════════════════════════════════════════

    @_('PROGRAM ID LBRACE declaraciones bloque RBRACE')
    def programa(self, p):
        funciones = [d for d in p.declaraciones if d[0] == 'funcion']
        variables = [d for d in p.declaraciones if d[0] == 'variables']
        return ('programa', p.ID, funciones, variables, p.bloque)

    @_('declaraciones var_o_funcion')
    def declaraciones(self, p):
        return p.declaraciones + [p.var_o_funcion]

    @_('')
    def declaraciones(self, p):
        return []

    @_('variables')
    def var_o_funcion(self, p):
        return p.variables

    @_('funcion')
    def var_o_funcion(self, p):
        return p.funcion

    # ══════════════════════════════════════════════════════════
    # FUNCIONES
    # ══════════════════════════════════════════════════════════

    @_('FUNCTION ID LPAREN parametros RPAREN LBRACE bloque RBRACE')
    def funcion(self, p):
        return ('funcion', p.ID, p.parametros, p.bloque)

    # ══════════════════════════════════════════════════════════
    # PARÁMETROS
    # ══════════════════════════════════════════════════════════

    @_('parametro_lista')
    def parametros(self, p):
        return p.parametro_lista

    @_('')
    def parametros(self, p):
        return []

    @_('parametro_lista COMMA parametro')
    def parametro_lista(self, p):
        return p.parametro_lista + [p.parametro]

    @_('parametro')
    def parametro_lista(self, p):
        return [p.parametro]

    @_('ID COLON tipo')
    def parametro(self, p):
        return ('parametro', p.ID, p.tipo)

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

    @_('BEGIN SEMICOLON var_list statement_list END SEMICOLON')
    def bloque(self, p):
        return ('bloque', p.var_list, p.statement_list)

    @_('BEGIN SEMICOLON statement_list END SEMICOLON')
    def bloque(self, p):
        return ('bloque', [], p.statement_list)

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
    
    @_('ID LPAREN argumentos RPAREN SEMICOLON')
    def statement(self, p):
        return ('llamada', p.ID, p.argumentos)
    # ══════════════════════════════════════════════════════════
    # ASIGNACIÓN
    # ══════════════════════════════════════════════════════════

    @_('ID LBRACKET expresion RBRACKET ASSIGN expresion SEMICOLON')
    def asignacion(self, p):
        return ('asignacion_arr', p.ID, p.expresion0, p.expresion1)

    @_('ID ASSIGN expresion SEMICOLON')
    def asignacion(self, p):
        return ('asignacion', p.ID, p.expresion)

    # ══════════════════════════════════════════════════════════
    # DECREMENTO / INCREMENTO
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

    @_('IF LPAREN expresion RPAREN THEN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE')
    def if_stat(self, p):
        return ('if', p.expresion, p.statement_list0, p.statement_list1)

    @_('IF LPAREN expresion RPAREN THEN LBRACE statement_list RBRACE')
    def if_stat(self, p):
        return ('if', p.expresion, p.statement_list, None)

    # ══════════════════════════════════════════════════════════
    # WHILE
    # ══════════════════════════════════════════════════════════

    @_('WHILE LPAREN expresion RPAREN DO LBRACE statement_list RBRACE')
    def while_stat(self, p):
        return ('while', p.expresion, p.statement_list)

    # ══════════════════════════════════════════════════════════
    # FOR
    # ══════════════════════════════════════════════════════════

    @_('FOR LPAREN ID ASSIGN expresion SEMICOLON expresion SEMICOLON ID INCREMENT RPAREN LBRACE statement_list RBRACE')
    def for_stat(self, p):
        return ('for', p.ID0, p.expresion0, p.expresion1,
                ('incremento', p.ID1), p.statement_list)

    @_('FOR LPAREN ID ASSIGN expresion SEMICOLON expresion SEMICOLON ID DECREMENT RPAREN LBRACE statement_list RBRACE')
    def for_stat(self, p):
        return ('for', p.ID0, p.expresion0, p.expresion1,
                ('decremento', p.ID1), p.statement_list)

    @_('FOR LPAREN ID ASSIGN expresion SEMICOLON expresion SEMICOLON ID ASSIGN expresion RPAREN LBRACE statement_list RBRACE')
    def for_stat(self, p):
        return ('for', p.ID0, p.expresion0, p.expresion1,
                ('asignacion', p.ID1, p.expresion2), p.statement_list)

    # ══════════════════════════════════════════════════════════
    # EXPRESIÓN
    # ══════════════════════════════════════════════════════════

    @_('expresion OR expresion')
    def expresion(self, p):
        return ('or', p.expresion0, p.expresion1)

    @_('expresion AND expresion')
    def expresion(self, p):
        return ('and', p.expresion0, p.expresion1)

    @_('expresion EQ expresion')
    def expresion(self, p):
        return ('==', p.expresion0, p.expresion1)

    @_('expresion NE expresion')
    def expresion(self, p):
        return ('!=', p.expresion0, p.expresion1)

    @_('expresion GTE expresion')
    def expresion(self, p):
        return ('>=', p.expresion0, p.expresion1)

    @_('expresion GT expresion')
    def expresion(self, p):
        return ('>', p.expresion0, p.expresion1)

    @_('expresion LT expresion')
    def expresion(self, p):
        return ('<', p.expresion0, p.expresion1)

    @_('expresion PLUS termino')
    def expresion(self, p):
        return ('+', p.expresion, p.termino)

    @_('expresion MINUS termino')
    def expresion(self, p):
        return ('-', p.expresion, p.termino)

    @_('expresion TIMES termino')
    def expresion(self, p):
        return ('*', p.expresion, p.termino)

    @_('expresion DIVIDE termino')
    def expresion(self, p):
        return ('/', p.expresion, p.termino)

    @_('expresion MOD termino')
    def expresion(self, p):
        return ('%', p.expresion, p.termino)

    @_('termino')
    def expresion(self, p):
        return p.termino
    
    @_('RETURN expresion SEMICOLON')
    def statement(self, p):
        return ('return', p.expresion)

    @_('RETURN SEMICOLON')
    def statement(self, p):
        return ('return', None)
    
    @_('expresion LTE expresion')
    def expresion(self, p):
        return ('<=', p.expresion0, p.expresion1)

    # ══════════════════════════════════════════════════════════
    # ARGUMENTOS
    # ══════════════════════════════════════════════════════════

    @_('lista_argumentos')
    def argumentos(self, p):
        return p.lista_argumentos

    @_('')
    def argumentos(self, p):
        return []

    @_('lista_argumentos COMMA expresion')
    def lista_argumentos(self, p):
        return p.lista_argumentos + [p.expresion]

    @_('expresion')
    def lista_argumentos(self, p):
        return [p.expresion]

    # ══════════════════════════════════════════════════════════
    # TÉRMINO
    # ══════════════════════════════════════════════════════════
    
    @_('MINUS termino %prec UNARY_MINUS')
    def termino(self, p):
        return ('unario_menos', p.termino)

    @_('ID LPAREN argumentos RPAREN')
    def termino(self, p):
        return ('llamada_funcion', p.ID, p.argumentos)

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
    
    @_('ID INCREMENT')
    def termino(self, p):
        return ('post_incremento', p.ID)

    # ══════════════════════════════════════════════════════════
    # MANEJO DE ERRORES
    # ══════════════════════════════════════════════════════════

    def error(self, p):
        if p:
            print(f'[Parser] Error sintáctico en línea {p.lineno}: token inesperado "{p.value}"')
        else:
            print('[Parser] Error sintáctico: fin de archivo inesperado')
