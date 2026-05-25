
# GENERADOR DE CÓDIGO INTERMEDIO — CUÁDRUPLOS

class GeneradorCodigo:
    def __init__(self):
        self.cuadruplos  = []   # lista de (op, op1, op2, res)
        self._temp_count = 0    # contador de temporales AVAIL
        self._pila_saltos = []  # pila de saltos ciegos

    # AVAIL: banco de temporales

    def _nuevo_temp(self):
        self._temp_count += 1
        return f'T{self._temp_count}'

    #  Emitir cuádruplo 
    def _emitir(self, op, op1, op2, res):
        self.cuadruplos.append((op, op1, op2, res))

    def _cont(self):
        """Número de la siguiente línea (base 1)."""
        return len(self.cuadruplos) + 1

    def _rellenar(self, indice, valor):
        """Rellena el destino de un salto ciego."""
        op, op1, op2, _ = self.cuadruplos[indice]
        self.cuadruplos[indice] = (op, op1, op2, valor)

    # Entrada principal

    def generar(self, ast):
        if ast is None:
            print('[CodeGen] AST vacío, no se genera código.')
            return
        _, nombre, var_list, bloque = ast
        self._generar_bloque(bloque)
        self.imprimir()

    #  Bloque 
    def _generar_bloque(self, bloque):
        _, statements = bloque
        for stmt in statements:
            self._generar_statement(stmt)

    # Statements 

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

    #  Asignación 

    def _gen_asignacion(self, stmt):
        _, nombre, expr = stmt
        res = self._gen_expresion(expr)
        self._emitir('=', res, '_', nombre)

    def _gen_asignacion_arr(self, stmt):
        _, nombre, indice, expr = stmt
        idx = self._gen_expresion(indice)
        val = self._gen_expresion(expr)
        self._emitir('=[', val, idx, nombre)

    # Expresión — regresa temporal o valor 

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
            self._emitir('[]=', nombre, idx, t)
            return t
        elif kind in ('+', '-', '*'):
            op1 = self._gen_expresion(expr[1])
            op2 = self._gen_expresion(expr[2])
            t   = self._nuevo_temp()
            self._emitir(kind, op1, op2, t)
            return t
        return '_'

    #  Condición — regresa temporal booleano

    def _gen_condicion(self, cond):
        kind = cond[0]
        if kind == 'and':
            t1 = self._gen_condicion(cond[1])
            t2 = self._gen_condicion(cond[2])
            t  = self._nuevo_temp()
            self._emitir('AND', t1, t2, t)
            return t
        else:
            # ('>=', expr1, expr2) | ('>', ...) | ('<', ...)
            op1 = self._gen_expresion(cond[1])
            op2 = self._gen_expresion(cond[2])
            t   = self._nuevo_temp()
            self._emitir(kind, op1, op2, t)
            return t

    #  IF 
    def _gen_if(self, stmt):
        _, condicion, then_stmts, else_stmts = stmt

        # 1. Evaluar condición
        t_cond = self._gen_condicion(condicion)

        # 2. GOTOF ciego — no sabemos aún a dónde salta
        idx_gotof = len(self.cuadruplos)
        self._emitir('GOTOF', t_cond, '_', '_')

        # 3. Bloque THEN
        for s in then_stmts:
            self._generar_statement(s)

        if else_stmts:
            # 4. GOTO ciego al final del else (salta el bloque else)
            idx_goto = len(self.cuadruplos)
            self._emitir('GOTO', '_', '_', '_')

            # 5. Rellenar GOTOF al inicio del ELSE
            self._rellenar(idx_gotof, self._cont())

            # 6. Bloque ELSE
            for s in else_stmts:
                self._generar_statement(s)

            # 7. Rellenar GOTO al final
            self._rellenar(idx_goto, self._cont())
        else:
            # Sin else: rellenar GOTOF al siguiente statement
            self._rellenar(idx_gotof, self._cont())

    # WHILE 

    def _gen_while(self, stmt):
        _, condicion, stmts = stmt

        # 1. Guardar posición de inicio (para el GOTO de regreso)
        inicio = self._cont()

        # 2. Evaluar condición
        t_cond = self._gen_condicion(condicion)

        # 3. GOTOF ciego — salto al final si condición falsa
        idx_gotof = len(self.cuadruplos)
        self._emitir('GOTOF', t_cond, '_', '_')

        # 4. Cuerpo del while
        for s in stmts:
            self._generar_statement(s)

        # 5. GOTO incondicional de regreso al inicio
        self._emitir('GOTO', '_', '_', inicio)

        # 6. Rellenar GOTOF al siguiente statement
        self._rellenar(idx_gotof, self._cont())

    #  FOR
    def _gen_for(self, stmt):
        _, nombre, inicio, condicion, avance, stmts = stmt

        # 1. Inicializar variable de control
        val_inicio = self._gen_expresion(inicio)
        self._emitir('=', val_inicio, '_', nombre)

        # 2. Guardar posición de evaluación de condición
        pos_cond = self._cont()

        # 3. Evaluar condición
        t_cond = self._gen_condicion(condicion)

        # 4. GOTOF ciego
        idx_gotof = len(self.cuadruplos)
        self._emitir('GOTOF', t_cond, '_', '_')

        # 5. Cuerpo del for
        for s in stmts:
            self._generar_statement(s)

        # 6. Avance (++ o --)
        if avance[0] == 'incremento':
            self._emitir('+', avance[1], '1', avance[1])
        else:
            self._emitir('-', avance[1], '1', avance[1])

        # 7. GOTO de regreso a la condición
        self._emitir('GOTO', '_', '_', pos_cond)

        # 8. Rellenar GOTOF
        self._rellenar(idx_gotof, self._cont())

    #  Imprimir cuádruplos 

    def imprimir(self):
        print('\n── Cuádruplos ─────────────────────────────────────')
        print(f'{"#":<5} {"Op":<8} {"Op1":<10} {"Op2":<10} {"Res"}')
        print('─' * 50)
        for i, (op, op1, op2, res) in enumerate(self.cuadruplos, 1):
            print(f'{i:<5} {str(op):<8} {str(op1):<10} {str(op2):<10} {res}')
        print('─' * 50)