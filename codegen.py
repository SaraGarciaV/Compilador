# ═════════════════════════════════════════════════════════════
# GENERADOR DE CÓDIGO INTERMEDIO — CUÁDRUPLOS
# ═════════════════════════════════════════════════════════════

class GeneradorCodigo:

    def __init__(self):
        self.cuadruplos = []
        self._temp_count = 0
        self._pila_saltos = []

        # funciones
        self._tabla_funciones = {}

        # pila de direcciones de retorno
        self._pila_returns = []

    # ═════════════════════════════════════════════════════════
    # TEMPORALES
    # ═════════════════════════════════════════════════════════

    def _nuevo_temp(self):
        self._temp_count += 1
        return f'T{self._temp_count}'

    # ═════════════════════════════════════════════════════════
    # EMITIR CUÁDRUPLO
    # ═════════════════════════════════════════════════════════

    def _emitir(self, op, op1, op2, res):
        self.cuadruplos.append((op, op1, op2, res))

    def _cont(self):
        return len(self.cuadruplos) + 1

    def _rellenar(self, indice, valor):
        op, op1, op2, _ = self.cuadruplos[indice]
        self.cuadruplos[indice] = (
            op,
            op1,
            op2,
            valor
        )

    # ═════════════════════════════════════════════════════════
    # ENTRADA PRINCIPAL
    # ═════════════════════════════════════════════════════════

    def generar(self, ast):
        if ast is None:
            print('[CodeGen] AST vacío')
            return

        # ('programa', nombre, funciones, vars, bloque)
        _, nombre, funciones, var_list, bloque = ast

        # GOTO al main
        idx_main = len(self.cuadruplos)
        self._emitir('GOTO', '_', '_', '_')

        # generar funciones primero
        for funcion in funciones:
            self._generar_funcion(funcion)

        # rellenar salto al main
        self._rellenar(idx_main, self._cont())

        # generar main
        self._generar_bloque(bloque)

        self.imprimir()

    # ═════════════════════════════════════════════════════════
    # FUNCIONES
    # ═════════════════════════════════════════════════════════

    def _generar_funcion(self, funcion):
        # ('funcion', nombre, parametros, bloque)
        _, nombre, parametros, bloque = funcion

        # guardar dirección inicial
        self._tabla_funciones[nombre] = self._cont()

        # etiqueta
        self._emitir('LABEL', '_', '_', nombre)

        # generar cuerpo
        self._generar_bloque(bloque)

        # retorno implícito
        self._emitir('RETURN', '_', '_', '_')

    # ═════════════════════════════════════════════════════════
    # BLOQUE
    # ═════════════════════════════════════════════════════════

    def _generar_bloque(self, bloque):
        # ('bloque', vars, statements)
        _, var_list, statements = bloque

        for stmt in statements:
            self._generar_statement(stmt)

    # ═════════════════════════════════════════════════════════
    # STATEMENTS
    # ═════════════════════════════════════════════════════════

    def _generar_statement(self, stmt):
        kind = stmt[0]

        if kind == 'asignacion':
            self._gen_asignacion(stmt)

        elif kind == 'asignacion_arr':
            self._gen_asignacion_arr(stmt)

        elif kind == 'decremento':
            self._emitir('-', stmt[1], '1', stmt[1])

        elif kind == 'incremento':
            self._emitir('+', stmt[1], '1', stmt[1])

        elif kind == 'write':
            res = self._gen_expresion(stmt[1])
            self._emitir('WRITE', res, '_', '_')

        elif kind == 'if':
            self._gen_if(stmt)

        elif kind == 'while':
            self._gen_while(stmt)

        elif kind == 'for':
            self._gen_for(stmt)

        elif kind == 'return':
            self._gen_return(stmt)

    # ═════════════════════════════════════════════════════════
    # RETURN
    # ═════════════════════════════════════════════════════════

    def _gen_return(self, stmt):
        # ('return', expr)
        _, expr = stmt

        valor = self._gen_expresion(expr)
        temp_return = self._nuevo_temp()

        # guardar valor retorno
        self._emitir('=', valor, '_', temp_return)

        # regresar
        self._emitir('RETURN', temp_return, '_', '_')

    # ═════════════════════════════════════════════════════════
    # ASIGNACIÓN
    # ═════════════════════════════════════════════════════════

    def _gen_asignacion(self, stmt):
        _, nombre, expr = stmt
        res = self._gen_expresion(expr)
        self._emitir('=', res, '_', nombre)

    def _gen_asignacion_arr(self, stmt):
        _, nombre, indice, expr = stmt
        idx = self._gen_expresion(indice)
        val = self._gen_expresion(expr)
        self._emitir('=[', val, idx, nombre)

    # ═════════════════════════════════════════════════════════
    # EXPRESIONES
    # ═════════════════════════════════════════════════════════

    def _gen_expresion(self, expr):
        if expr is None:
            return '_'

        kind = expr[0]

        if kind == 'num_int':
            return str(expr[1])

        elif kind == 'num_float':
            return str(expr[1])

        elif kind == 'string':
            return f'"{expr[1]}"'

        elif kind == 'id':
            return expr[1]

        elif kind == 'acceso_arr':
            _, nombre, indice = expr
            idx = self._gen_expresion(indice)
            t = self._nuevo_temp()
            # Cambiado a '=[]' para legibilidad
            self._emitir('=[]', nombre, idx, t)
            return t

        elif kind == 'llamada_funcion':
            return self._gen_llamada_funcion(expr)

        elif kind in ('+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=', 'and', 'or'):
            op1 = self._gen_expresion(expr[1])
            op2 = self._gen_expresion(expr[2])
            t = self._nuevo_temp()
            
            # Ajuste estético para mayúsculas en operadores lógicos
            op_code = kind.upper() if kind in ('and', 'or') else kind
            self._emitir(op_code, op1, op2, t)
            return t

        elif kind == 'unario_menos':
            op = self._gen_expresion(expr[1])
            t = self._nuevo_temp()
            self._emitir('UMINUS', op, '_', t)
            return t
        
        elif kind == 'post_incremento':
            t = self._nuevo_temp()
            self._emitir('+', expr[1], '1', t)
            return t

        return '_'

    # ═════════════════════════════════════════════════════════
    # LLAMADA A FUNCIÓN
    # ═════════════════════════════════════════════════════════

    def _gen_llamada_funcion(self, expr):
        # ('llamada_funcion', nombre, argumentos)
        _, nombre, argumentos = expr

        # generar PARAM
        for arg in argumentos:
            val = self._gen_expresion(arg)
            self._emitir('PARAM', val, '_', '_')

        # guardar dirección retorno
        dir_retorno = self._cont() + 2
        self._pila_returns.append(dir_retorno)

        # GOSUB
        self._emitir(
            'GOSUB',
            nombre,
            '_',
            self._tabla_funciones.get(nombre, '_')
        )

        # recuperar valor retorno
        temp = self._nuevo_temp()
        self._emitir('GETRET', nombre, '_', temp)

        return temp

    # ═════════════════════════════════════════════════════════
    # IF
    # ═════════════════════════════════════════════════════════

    def _gen_if(self, stmt):
        _, condicion, then_stmts, else_stmts = stmt

        t_cond = self._gen_expresion(condicion)
        idx_gotof = len(self.cuadruplos)

        self._emitir('GOTOF', t_cond, '_', '_')

        for s in then_stmts:
            self._generar_statement(s)

        if else_stmts:
            idx_goto = len(self.cuadruplos)
            self._emitir('GOTO', '_', '_', '_')
            self._rellenar(idx_gotof, self._cont())

            for s in else_stmts:
                self._generar_statement(s)

            self._rellenar(idx_goto, self._cont())
        else:
            self._rellenar(idx_gotof, self._cont())

    # ═════════════════════════════════════════════════════════
    # WHILE
    # ═════════════════════════════════════════════════════════

    def _gen_while(self, stmt):
        _, condicion, stmts = stmt

        inicio = self._cont()
        t_cond = self._gen_expresion(condicion)
        idx_gotof = len(self.cuadruplos)

        self._emitir('GOTOF', t_cond, '_', '_')

        for s in stmts:
            self._generar_statement(s)

        self._emitir('GOTO', '_', '_', inicio)
        self._rellenar(idx_gotof, self._cont())

    # ═════════════════════════════════════════════════════════
    # FOR
    # ═════════════════════════════════════════════════════════

    def _gen_for(self, stmt):
        _, nombre, inicio, condicion, avance, stmts = stmt

        val_inicio = self._gen_expresion(inicio)
        self._emitir('=', val_inicio, '_', nombre)

        pos_cond = self._cont()
        t_cond = self._gen_expresion(condicion)
        idx_gotof = len(self.cuadruplos)

        self._emitir('GOTOF', t_cond, '_', '_')

        for s in stmts:
            self._generar_statement(s)

        if avance[0] == 'incremento':
            self._emitir('+', avance[1], '1', avance[1])
        elif avance[0] == 'decremento':
            self._emitir('-', avance[1], '1', avance[1])
        elif avance[0] == 'asignacion':
            res = self._gen_expresion(avance[2])
            self._emitir('=', res, '_', avance[1])

        self._emitir('GOTO', '_', '_', pos_cond)
        self._rellenar(idx_gotof, self._cont())

    # ═════════════════════════════════════════════════════════
    # IMPRIMIR
    # ═════════════════════════════════════════════════════════

    def imprimir(self):
        print('\n── Cuádruplos ─────────────────────────────────────')
        print(f'{"#":<5} {"Op":<10} {"Op1":<10} {"Op2":<10} {"Res"}')
        print('─' * 60)

        for i, (op, op1, op2, res) in enumerate(self.cuadruplos, 1):
            print(
                f'{i:<5} '
                f'{str(op):<10} '
                f'{str(op1):<10} '
                f'{str(op2):<10} '
                f'{res}'
            )

        print('─' * 60)