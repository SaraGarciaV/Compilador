# ═════════════════════════════════════════════════════════════
# EVALUADOR DE CUÁDRUPLOS — MÁQUINA VIRTUAL
# ═════════════════════════════════════════════════════════════

class Evaluador:

    def __init__(self, tabla_simbolos):
        self.memoria = {}
        self.salida = []

        # pila de direcciones retorno
        self.pila_retorno = []

        # pila parámetros
        self.pila_parametros = []

        # valor retorno funciones
        self.valor_retorno = None

        # inicializar memoria
        for nombre, info in tabla_simbolos.items():
            if info.get('es_arreglo', False):
                self.memoria[nombre] = [0] * info['tamanio']
            else:
                self.memoria[nombre] = 0

    # ═════════════════════════════════════════════════════════
    # ENTRADA PRINCIPAL
    # ═════════════════════════════════════════════════════════

    def ejecutar(self, cuadruplos):
        pc = 0
        while pc < len(cuadruplos):
            op, op1, op2, res = cuadruplos[pc]
            salto = self._ejecutar_cuadruplo(
                op,
                op1,
                op2,
                res,
                pc
            )

            if salto is not None:
                pc = salto - 1
            else:
                pc += 1

        print('\n── Salida del programa ────────────────────────────')
        for linea in self.salida:
            print(linea)
        print('─' * 50)

    # ═════════════════════════════════════════════════════════
    # EJECUTAR CUÁDRUPLO
    # ═════════════════════════════════════════════════════════

    def _ejecutar_cuadruplo(self, op, op1, op2, res, pc):

        # ═════════════════════════════════════════════════════
        # ASIGNACIÓN
        # ═════════════════════════════════════════════════════

        if op == '=':
            self.memoria[res] = self._valor(op1)

        # ═════════════════════════════════════════════════════
        # OPERACIONES ARITMÉTICAS
        # ═════════════════════════════════════════════════════

        elif op == '+':
            self.memoria[res] = self._valor(op1) + self._valor(op2)

        elif op == '-':
            self.memoria[res] = self._valor(op1) - self._valor(op2)

        elif op == '*':
            self.memoria[res] = self._valor(op1) * self._valor(op2)

        elif op == '/':
            v2 = self._valor(op2)
            if v2 == 0:
                raise RuntimeError(f"Error en tiempo de ejecución: División por cero en la instrucción {pc}.")
            self.memoria[res] = self._valor(op1) / v2

        elif op == '%':
            v2 = self._valor(op2)
            if v2 == 0:
                raise RuntimeError(f"Error en tiempo de ejecución: Módulo por cero en la instrucción {pc}.")
            self.memoria[res] = self._valor(op1) % v2

        elif op == 'UMINUS':
            self.memoria[res] = -self._valor(op1)

        # ═════════════════════════════════════════════════════
        # RELACIONALES
        # ═════════════════════════════════════════════════════

        elif op == '>':
            self.memoria[res] = self._valor(op1) > self._valor(op2)

        elif op == '>=':
            self.memoria[res] = self._valor(op1) >= self._valor(op2)

        elif op == '<':
            self.memoria[res] = self._valor(op1) < self._valor(op2)
            
        elif op == '<=':
            self.memoria[res] = self._valor(op1) <= self._valor(op2)

        elif op == '==':
            self.memoria[res] = self._valor(op1) == self._valor(op2)

        elif op == '!=':
            self.memoria[res] = self._valor(op1) != self._valor(op2)

        # ═════════════════════════════════════════════════════
        # LÓGICOS
        # ═════════════════════════════════════════════════════

        elif op == 'AND':
            self.memoria[res] = self._valor(op1) and self._valor(op2)

        elif op == 'OR':
            self.memoria[res] = self._valor(op1) or self._valor(op2)

        # ═════════════════════════════════════════════════════
        # SALTOS
        # ═════════════════════════════════════════════════════

        elif op == 'GOTOF':
            if not self._valor(op1):
                return res

        elif op == 'GOTO':
            return res

        # ═════════════════════════════════════════════════════
        # GOSUB
        # ═════════════════════════════════════════════════════

        elif op == 'GOSUB':
            # guardar dirección retorno
            self.pila_retorno.append(pc + 2)
            # saltar función
            return res

        # ═════════════════════════════════════════════════════
        # RETURN
        # ═════════════════════════════════════════════════════

        elif op == 'RETURN':
            # guardar valor retorno
            if op1 != '_':
                self.valor_retorno = self._valor(op1)
            # regresar al caller
            if self.pila_retorno:
                return self.pila_retorno.pop()

        # ═════════════════════════════════════════════════════
        # PARÁMETROS
        # ═════════════════════════════════════════════════════

        elif op == 'PARAM':
            valor = self._valor(op1)
            self.pila_parametros.append(valor)

        # ═════════════════════════════════════════════════════
        # RECIBIR PARÁMETRO
        # ═════════════════════════════════════════════════════

        elif op == 'POP_PARAM':
            if self.pila_parametros:
                self.memoria[res] = self.pila_parametros.pop(0)

        # ═════════════════════════════════════════════════════
        # OBTENER RETORNO
        # ═════════════════════════════════════════════════════

        elif op == 'GETRET':
            self.memoria[res] = self.valor_retorno

        # ═════════════════════════════════════════════════════
        # LABEL
        # ═════════════════════════════════════════════════════

        elif op == 'LABEL':
            pass

        # ═════════════════════════════════════════════════════
        # WRITE
        # ═════════════════════════════════════════════════════

        elif op == 'WRITE':
            val = self._valor(op1)
            self.salida.append(val)

        # ═════════════════════════════════════════════════════
        # ASIGNACIÓN ARREGLO
        # ═════════════════════════════════════════════════════

        elif op == '=[':
            idx = self._valor(op2)
            val = self._valor(op1)
            arreglo = self.memoria.get(res)

            if not isinstance(arreglo, list):
                raise RuntimeError(f"Error en tiempo de ejecución: '{res}' no es un arreglo en la instrucción {pc}.")
                
            if not (0 <= idx < len(arreglo)):
                raise RuntimeError(f"Error en tiempo de ejecución: Índice {idx} fuera de límites para el arreglo '{res}' en la instrucción {pc}.")

            arreglo[idx] = val

        # ═════════════════════════════════════════════════════
        # ACCESO ARREGLO
        # ═════════════════════════════════════════════════════

        elif op == '=[]':
            idx = self._valor(op2)
            arr = self.memoria.get(op1)

            if not isinstance(arr, list):
                raise RuntimeError(f"Error en tiempo de ejecución: '{op1}' no es un arreglo en la instrucción {pc}.")
                
            if not (0 <= idx < len(arr)):
                raise RuntimeError(f"Error en tiempo de ejecución: Índice {idx} fuera de límites para el arreglo '{op1}' en la instrucción {pc}.")

            self.memoria[res] = arr[idx]

        return None

    # ═════════════════════════════════════════════════════════
    # OBTENER VALOR
    # ═════════════════════════════════════════════════════════

    def _valor(self, operando):
        if operando == '_':
            return None

        # strings
        if (
            isinstance(operando, str)
            and operando.startswith('"')
        ):
            return operando[1:-1]

        # números
        try:
            if isinstance(operando, (int, float)):
                return operando

            if '.' in str(operando):
                return float(operando)

            return int(operando)

        except (ValueError, TypeError):
            pass

        # variables
        return self.memoria.get(operando, 0)
    