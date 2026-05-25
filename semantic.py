
# TABLA DE SÍMBOLOS

class TablaSimbolos:
    def __init__(self):
        self.tabla = {}       # { nombre: {tipo, dir, ambito, tamanio} }
        self._dir_counter = 0

    def _next_dir(self):
        addr = f'0x{self._dir_counter:02X}'
        self._dir_counter += 1
        return addr

    def agregar(self, nombre, tipo, ambito='global', tamanio=1):
        if nombre in self.tabla:
            return False  # ya existe
        self.tabla[nombre] = {
            'tipo':    tipo,
            'dir':     self._next_dir(),
            'ambito':  ambito,
            'tamanio': tamanio,
        }
        return True

    def buscar(self, nombre):
        return self.tabla.get(nombre, None)

    def imprimir(self):
        print('\n── Tabla de Símbolos ──────────────────────────────')
        print(f'{"Nombre":<12} {"Dir":<8} {"Tipo":<8} {"Ámbito":<10} {"Tamaño"}')
        print('─' * 50)
        for nombre, info in self.tabla.items():
            print(f'{nombre:<12} {info["dir"]:<8} {info["tipo"]:<8} {info["ambito"]:<10} {info["tamanio"]}')
        print('─' * 50)


# MATRIZ DE COMPATIBILIDAD DE TIPOS

MATRIZ_TIPOS = {
    ('int',   'int'):   'int',
    ('int',   'float'): 'float',
    ('float', 'int'):   'float',
    ('float', 'float'): 'float',
}

def verificar_tipos(t1, t2):
    """Regresa el tipo resultante o None si es incompatible."""
    return MATRIZ_TIPOS.get((t1, t2), None)



# ANALIZADOR SEMÁNTICO


class AnalizadorSemantico:
    def __init__(self):
        self.tabla    = TablaSimbolos()
        self.errores  = []
        self.pila_tipos = []   # pila de tipos para expresiones

    def error(self, msg):
        self.errores.append(msg)
        print(f'[Semántico] Error: {msg}')

    # ── Entrada principal ──────────────────────────────────────

    def analizar(self, ast):
        if ast is None:
            self.error('AST vacío — el parser no produjo resultado')
            return
        # ast = ('programa', nombre, var_list, bloque)
        _, nombre, var_list, bloque = ast
        self._registrar_variables(var_list, 'global')
        self._analizar_bloque(bloque)
        self.tabla.imprimir()
        if not self.errores:
            print('\n Análisis semántico completado sin errores.')
        else:
            print(f'\n Se encontraron {len(self.errores)} error(es) semántico(s).')



    def _registrar_variables(self, var_list, ambito):
        for var in var_list:
            # var = ('variables', [declaraciones], tipo)
            _, declaraciones, tipo = var
            for decl in declaraciones:
                if decl[0] == 'arreglo':
                    _, nombre, tamanio = decl
                    ok = self.tabla.agregar(nombre, tipo, ambito, tamanio)
                    if not ok:
                        self.error(f'Variable "{nombre}" declarada más de una vez')
                else:
                    _, nombre = decl
                    ok = self.tabla.agregar(nombre, tipo, ambito)
                    if not ok:
                        self.error(f'Variable "{nombre}" declarada más de una vez')



    def _analizar_bloque(self, bloque):
        # bloque = ('bloque', [statements])
        _, statements = bloque
        for stmt in statements:
            self._analizar_statement(stmt)

    #  Statements

    def _analizar_statement(self, stmt):
        kind = stmt[0]
        if kind == 'asignacion':
            self._analizar_asignacion(stmt)
        elif kind == 'asignacion_arr':
            self._analizar_asignacion_arr(stmt)
        elif kind == 'decremento':
            self._verificar_declarada(stmt[1])
        elif kind == 'incremento':
            self._verificar_declarada(stmt[1])
        elif kind == 'write':
            self._analizar_expresion(stmt[1])
        elif kind == 'if':
            self._analizar_if(stmt)
        elif kind == 'while':
            self._analizar_while(stmt)
        elif kind == 'for':
            self._analizar_for(stmt)

    #  Asignación

    def _analizar_asignacion(self, stmt):
        # ('asignacion', id, expresion)
        _, nombre, expr = stmt
        self._verificar_declarada(nombre)
        tipo_expr = self._analizar_expresion(expr)
        tipo_var  = self._tipo_de(nombre)
        if tipo_var and tipo_expr:
            if verificar_tipos(tipo_var, tipo_expr) is None:
                self.error(f'Tipos incompatibles en asignación a "{nombre}": {tipo_var} := {tipo_expr}')

    def _analizar_asignacion_arr(self, stmt):
        # ('asignacion_arr', id, indice, expresion)
        _, nombre, indice, expr = stmt
        info = self._verificar_declarada(nombre)
        if info and info['tamanio'] == 1:
            self.error(f'"{nombre}" no es un arreglo')
        self._analizar_expresion(indice)
        self._analizar_expresion(expr)

    # If 

    def _analizar_if(self, stmt):
        # ('if', condicion, then_stmts, else_stmts)
        _, condicion, then_stmts, else_stmts = stmt
        self._analizar_condicion(condicion)
        for s in then_stmts:
            self._analizar_statement(s)
        if else_stmts:
            for s in else_stmts:
                self._analizar_statement(s)

    #  While 

    def _analizar_while(self, stmt):
        # ('while', condicion, stmts)
        _, condicion, stmts = stmt
        self._analizar_condicion(condicion)
        for s in stmts:
            self._analizar_statement(s)

    # For 

    def _analizar_for(self, stmt):
        # ('for', id, inicio, condicion, avance, stmts)
        _, nombre, inicio, condicion, avance, stmts = stmt
        self._verificar_declarada(nombre)
        self._analizar_expresion(inicio)
        self._analizar_condicion(condicion)
        for s in stmts:
            self._analizar_statement(s)

    #  Condición

    def _analizar_condicion(self, cond):
        kind = cond[0]
        if kind == 'and':
            self._analizar_condicion(cond[1])
            self._analizar_condicion(cond[2])
        else:
            # ('>=', expr1, expr2) | ('>', ...) | ('<', ...)
            _, expr1, expr2 = cond
            t1 = self._analizar_expresion(expr1)
            t2 = self._analizar_expresion(expr2)
            if t1 and t2 and verificar_tipos(t1, t2) is None:
                self.error(f'Tipos incompatibles en condición: {t1} {kind} {t2}')

    #  Expresión — regresa tipo 

    def _analizar_expresion(self, expr):
        if expr is None:
            return None
        kind = expr[0]

        if kind == 'num_int':
            return 'int'
        elif kind == 'num_float':
            return 'float'
        elif kind == 'string':
            return 'string'
        elif kind == 'id':
            return self._tipo_de(expr[1])
        elif kind == 'acceso_arr':
            _, nombre, indice = expr
            self._verificar_declarada(nombre)
            self._analizar_expresion(indice)
            return self._tipo_de(nombre)
        elif kind in ('+', '-', '*'):
            t1 = self._analizar_expresion(expr[1])
            t2 = self._analizar_expresion(expr[2])
            if t1 and t2:
                resultado = verificar_tipos(t1, t2)
                if resultado is None:
                    self.error(f'Operación "{kind}" entre tipos incompatibles: {t1} y {t2}')
                return resultado
        return None

    #  Helpers 

    def _verificar_declarada(self, nombre):
        info = self.tabla.buscar(nombre)
        if info is None:
            self.error(f'Variable "{nombre}" no declarada')
        return info

    def _tipo_de(self, nombre):
        info = self.tabla.buscar(nombre)
        return info['tipo'] if info else None