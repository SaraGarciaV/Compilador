# ═════════════════════════════════════════════════════════════
# TABLA DE SÍMBOLOS
# ═════════════════════════════════════════════════════════════

class TablaSimbolos:
    def __init__(self):
        # pila de ámbitos
        self.pila = [{}]
        self._dir_counter = 0

    def _next_dir(self):
        addr = f'0x{self._dir_counter:02X}'
        self._dir_counter += 1
        return addr

    def entrar_ambito(self):
        self.pila.append({})

    def salir_ambito(self):
        self.pila.pop()

    def agregar(self, nombre, tipo, ambito='global',
                tamanio=1, clase='variable',
                parametros=None, retorno=None, es_arreglo=False):

        tabla_actual = self.pila[-1]

        if nombre in tabla_actual:
            return False

        tabla_actual[nombre] = {
            'tipo': tipo,
            'dir': self._next_dir(),
            'ambito': ambito,
            'tamanio': tamanio,
            'clase': clase,
            'parametros': parametros or [],
            'retorno': retorno,
            'es_arreglo': es_arreglo
        }

        return True

    def buscar(self, nombre):
        # buscar desde el ámbito más interno al global
        for tabla in reversed(self.pila):
            if nombre in tabla:
                return tabla[nombre]
        return None

    def imprimir(self):
        print('\n── Tabla de Símbolos ──────────────────────────────')
        print(f'{"Nombre":<12} {"Dir":<8} {"Tipo":<8} {"Ámbito":<10} {"Clase":<10} {"Es Arreglo"}')
        print('─' * 70)

        for i, tabla in enumerate(self.pila):
            for nombre, info in tabla.items():
                print(
                    f'{nombre:<12} '
                    f'{info["dir"]:<8} '
                    f'{info["tipo"]:<8} '
                    f'{info["ambito"]:<10} '
                    f'{info["clase"]:<10} '
                    f'{info["es_arreglo"]}'
                )

        print('─' * 70)


# ═════════════════════════════════════════════════════════════
# MATRIZ DE TIPOS
# ═════════════════════════════════════════════════════════════

MATRIZ_TIPOS = {
    # Operaciones aritméticas
    ('int', 'int'): 'int',
    ('int', 'float'): 'float',
    ('float', 'int'): 'float',
    ('float', 'float'): 'float',
    # Operaciones lógicas
    ('bool', 'bool'): 'bool',
}

def verificar_tipos(t1, t2):
    return MATRIZ_TIPOS.get((t1, t2), None)


# ═════════════════════════════════════════════════════════════
# ANALIZADOR SEMÁNTICO
# ═════════════════════════════════════════════════════════════

class AnalizadorSemantico:

    def __init__(self):
        self.tabla = TablaSimbolos()
        self.errores = []

    def error(self, msg):
        self.errores.append(msg)
        print(f'[Semántico] Error: {msg}')

    # ═════════════════════════════════════════════════════════
    # ENTRADA PRINCIPAL
    # ═════════════════════════════════════════════════════════

    def analizar(self, ast):
        if ast is None:
            self.error('AST vacío')
            return

        # ('programa', nombre, funciones, vars, bloque)
        _, nombre, funciones, var_list, bloque = ast

        # registrar variables globales
        self._registrar_variables(var_list, 'global')

        # registrar funciones primero
        for funcion in funciones:
            self._registrar_funcion(funcion)

        # analizar funciones
        for funcion in funciones:
            self._analizar_funcion(funcion)

        # analizar main
        self._analizar_bloque(bloque)

        self.tabla.imprimir()

        if not self.errores:
            print('\n✓ Análisis semántico exitoso')
        else:
            print(f'\n✗ Se encontraron {len(self.errores)} error(es)')

    # ═════════════════════════════════════════════════════════
    # REGISTRO DE VARIABLES
    # ═════════════════════════════════════════════════════════

    def _registrar_variables(self, var_list, ambito):
        for var in var_list:
            _, declaraciones, tipo = var

            for decl in declaraciones:
                if decl[0] == 'arreglo':
                    _, nombre, tamanio = decl
                    ok = self.tabla.agregar(
                        nombre,
                        tipo,
                        ambito,
                        tamanio=tamanio,
                        es_arreglo=True
                    )
                    if not ok:
                        self.error(f'Variable "{nombre}" declarada más de una vez')
                else:
                    _, nombre = decl
                    ok = self.tabla.agregar(
                        nombre,
                        tipo,
                        ambito,
                        es_arreglo=False
                    )
                    if not ok:
                        self.error(f'Variable "{nombre}" declarada más de una vez')

    # ═════════════════════════════════════════════════════════
    # FUNCIONES
    # ═════════════════════════════════════════════════════════

    def _registrar_funcion(self, funcion):
        # ('funcion', nombre, parametros, bloque)
        _, nombre, parametros, _ = funcion
        tipos_parametros = []

        for p in parametros:
            _, _, tipo = p
            tipos_parametros.append(tipo)

        ok = self.tabla.agregar(
            nombre,
            'function',
            ambito='global',
            clase='funcion',
            parametros=tipos_parametros
        )

        if not ok:
            self.error(f'Función "{nombre}" ya declarada')

    def _analizar_funcion(self, funcion):
        _, nombre, parametros, bloque = funcion

        self.tabla.entrar_ambito()

        # registrar parámetros
        for param in parametros:
            _, nombre_param, tipo_param = param
            ok = self.tabla.agregar(
                nombre_param,
                tipo_param,
                ambito=nombre,
                es_arreglo=False
            )
            if not ok:
                self.error(f'Parámetro "{nombre_param}" duplicado')

        self._analizar_bloque(bloque)
        self.tabla.salir_ambito()

    # ═════════════════════════════════════════════════════════
    # BLOQUE
    # ═════════════════════════════════════════════════════════

    def _analizar_bloque(self, bloque):
        # ('bloque', vars, statements)
        _, var_list, statements = bloque

        self.tabla.entrar_ambito()
        self._registrar_variables(var_list, 'local')

        for stmt in statements:
            self._analizar_statement(stmt)

        self.tabla.salir_ambito()

    # ═════════════════════════════════════════════════════════
    # STATEMENTS
    # ═════════════════════════════════════════════════════════

    def _analizar_statement(self, stmt):
        kind = stmt[0]

        if kind == 'asignacion':
            self._analizar_asignacion(stmt)
        elif kind == 'asignacion_arr':
            self._analizar_asignacion_arr(stmt)
        elif kind in ('decremento', 'incremento'):
            self._verificar_declarada(stmt[1])
        elif kind == 'write':
            self._analizar_expresion(stmt[1])
        elif kind == 'if':
            self._analizar_if(stmt)
        elif kind == 'while':
            self._analizar_while(stmt)
        elif kind == 'for':
            self._analizar_for(stmt)
        elif kind == 'return':
            if stmt[1] is not None:
                self._analizar_expresion(stmt[1])

    # ═════════════════════════════════════════════════════════
    # ASIGNACIÓN
    # ═════════════════════════════════════════════════════════

    def _analizar_asignacion(self, stmt):
        _, nombre, expr = stmt
        self._verificar_declarada(nombre)
        
        tipo_expr = self._analizar_expresion(expr)
        tipo_var = self._tipo_de(nombre)

        if tipo_var and tipo_expr:
            if verificar_tipos(tipo_var, tipo_expr) is None:
                self.error(f'Tipos incompatibles en asignación: {tipo_var} := {tipo_expr}')

    def _analizar_asignacion_arr(self, stmt):
        _, nombre, indice, expr = stmt
        info = self._verificar_declarada(nombre)

        if info and not info.get('es_arreglo', False):
            self.error(f'"{nombre}" no es un arreglo')

        tipo_indice = self._analizar_expresion(indice)
        if tipo_indice and tipo_indice != 'int':
            self.error(f'El índice del arreglo "{nombre}" debe ser de tipo int (se obtuvo {tipo_indice})')

        self._analizar_expresion(expr)

    # ═════════════════════════════════════════════════════════
    # ESTRUCTURAS DE CONTROL
    # ═════════════════════════════════════════════════════════

    def _analizar_if(self, stmt):
        _, condicion, then_stmts, else_stmts = stmt

        tipo_cond = self._analizar_expresion(condicion)
        if tipo_cond and tipo_cond != 'bool':
            self.error(f'La condición del IF debe ser booleana, se obtuvo {tipo_cond}')

        for s in then_stmts:
            self._analizar_statement(s)

        if else_stmts:
            for s in else_stmts:
                self._analizar_statement(s)

    def _analizar_while(self, stmt):
        _, condicion, stmts = stmt

        tipo_cond = self._analizar_expresion(condicion)
        if tipo_cond and tipo_cond != 'bool':
            self.error(f'La condición del WHILE debe ser booleana, se obtuvo {tipo_cond}')

        for s in stmts:
            self._analizar_statement(s)

    def _analizar_for(self, stmt):
        _, nombre, inicio, condicion, avance, stmts = stmt
        self._verificar_declarada(nombre)
        
        self._analizar_expresion(inicio)

        tipo_cond = self._analizar_expresion(condicion)
        if tipo_cond and tipo_cond != 'bool':
            self.error(f'La condición del FOR debe ser booleana, se obtuvo {tipo_cond}')

        if nombre != avance[1]:
            self.error(
                f'La variable de control "{nombre}" '
                f'no coincide con la variable de avance '
                f'"{avance[1]}" en el for'
            )
            
        for s in stmts:
            self._analizar_statement(s)

    # ═════════════════════════════════════════════════════════
    # EXPRESIONES
    # ═════════════════════════════════════════════════════════

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
            info = self._verificar_declarada(nombre)
            
            if info and not info.get('es_arreglo', False):
                self.error(f'"{nombre}" no es un arreglo')

            tipo_indice = self._analizar_expresion(indice)
            if tipo_indice and tipo_indice != 'int':
                self.error(f'El índice del arreglo "{nombre}" debe ser de tipo int (se obtuvo {tipo_indice})')
                
            return self._tipo_de(nombre)

        elif kind == 'llamada_funcion':
            return self._analizar_llamada_funcion(expr)

        elif kind in ('+', '-', '*', '/', '%'):
            t1 = self._analizar_expresion(expr[1])
            t2 = self._analizar_expresion(expr[2])

            if t1 and t2:
                resultado = verificar_tipos(t1, t2)
                if resultado is None:
                    self.error(f'Operación aritmética inválida entre {t1} y {t2}')
                return resultado
            return None

        elif kind in ('==', '!=', '>', '<', '>=', '<='):
            t1 = self._analizar_expresion(expr[1])
            t2 = self._analizar_expresion(expr[2])

            if t1 and t2:
                # Validar que los operandos sean numéricos para comparaciones
                if t1 in ('int', 'float') and t2 in ('int', 'float'):
                    return 'bool'
                else:
                    self.error(f'Tipos incompatibles para operador relacional: {t1} y {t2}')
            return None

        elif kind in ('or', 'and'):
            t1 = self._analizar_expresion(expr[1])
            t2 = self._analizar_expresion(expr[2])

            if t1 and t2:
                # Validar que ambos sean booleanos
                if t1 == 'bool' and t2 == 'bool':
                    return 'bool'
                else:
                    self.error(f'Tipos incompatibles para operador lógico: {t1} y {t2}')
            return None

        elif kind == 'unario_menos':
            t1 = self._analizar_expresion(expr[1])
            if t1 in ('int', 'float'):
                return t1
            else:
                self.error(f'Operador unario "-" incompatible con el tipo {t1}')
            return None

        return None

    # ═════════════════════════════════════════════════════════
    # LLAMADAS A FUNCIONES
    # ═════════════════════════════════════════════════════════

    def _analizar_llamada_funcion(self, expr):
        # ('llamada_funcion', nombre, argumentos)
        _, nombre, argumentos = expr
        info = self.tabla.buscar(nombre)

        if info is None:
            self.error(f'Función "{nombre}" no declarada')
            return None

        if info['clase'] != 'funcion':
            self.error(f'"{nombre}" no es una función')
            return None

        parametros = info['parametros']

        # verificar cantidad de argumentos
        if len(argumentos) != len(parametros):
            self.error(
                f'La función "{nombre}" esperaba '
                f'{len(parametros)} argumento(s) '
                f'y recibió {len(argumentos)}'
            )

        # verificar tipos
        for i in range(min(len(argumentos), len(parametros))):
            tipo_arg = self._analizar_expresion(argumentos[i])
            tipo_param = parametros[i]

            if verificar_tipos(tipo_param, tipo_arg) is None:
                self.error(
                    f'Argumento {i+1} incompatible '
                    f'en llamada a "{nombre}"'
                )

        # Retorno fijo de ejemplo (modificable según requerimientos futuros)
        return 'int'

    # ═════════════════════════════════════════════════════════
    # HELPERS
    # ═════════════════════════════════════════════════════════

    def _verificar_declarada(self, nombre):
        info = self.tabla.buscar(nombre)
        if info is None:
            self.error(f'Variable "{nombre}" no declarada')
        return info  # Devuelve el símbolo completo (diccionario)

    def _tipo_de(self, nombre):
        info = self.tabla.buscar(nombre)
        return info['tipo'] if info else None