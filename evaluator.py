# EVALUADOR DE CUÁDRUPLOS — MÁQUINA VIRTUAL

class Evaluador:
    def __init__(self, tabla_simbolos):
        self.memoria = {}
        self.salida  = []

        for nombre, info in tabla_simbolos.items():
            if info['tamanio'] > 1:
                self.memoria[nombre] = [0] * info['tamanio']
            else:
                self.memoria[nombre] = 0

    # ── Entrada principal ──────────────────────────────────────

    def ejecutar(self, cuadruplos):
        pc = 0
        while pc < len(cuadruplos):
            op, op1, op2, res = cuadruplos[pc]
            salto = self._ejecutar_cuadruplo(op, op1, op2, res, pc)
            if salto is not None:
                pc = salto - 1
            else:
                pc += 1

        print('\n── Salida del programa ────────────────────────────')
        for linea in self.salida:
            print(linea)
        print('─' * 50)

    # ── Ejecutar un cuádruplo ──────────────────────────────────

    def _ejecutar_cuadruplo(self, op, op1, op2, res, pc):
        """Regresa el número de línea destino si hay salto, None si no."""

        if op == '=':
            self.memoria[res] = self._valor(op1)

        elif op == '+':
            self.memoria[res] = self._valor(op1) + self._valor(op2)

        elif op == '-':
            self.memoria[res] = self._valor(op1) - self._valor(op2)

        elif op == '*':
            self.memoria[res] = self._valor(op1) * self._valor(op2)

        elif op == '>':
            self.memoria[res] = self._valor(op1) > self._valor(op2)

        elif op == '>=':
            self.memoria[res] = self._valor(op1) >= self._valor(op2)

        elif op == '<':
            self.memoria[res] = self._valor(op1) < self._valor(op2)

        elif op == 'AND':
            self.memoria[res] = self._valor(op1) and self._valor(op2)

        elif op == 'GOTOF':
            if not self._valor(op1):
                return res

        elif op == 'GOTO':
            return res

        elif op == 'WRITE':
            val = self._valor(op1)
            self.salida.append(val)

        elif op == '=[':
            idx = self._valor(op2)
            val = self._valor(op1)
            if isinstance(self.memoria.get(res), list):
                self.memoria[res][idx] = val
            else:
                self.memoria[res] = {idx: val}

        elif op == '[]=':
            idx = self._valor(op2)
            arr = self.memoria.get(op1, {})
            if isinstance(arr, list):
                self.memoria[res] = arr[idx] if idx < len(arr) else 0
            else:
                self.memoria[res] = arr.get(idx, 0)

        return None

    # ── Obtener valor de un operando ───────────────────────────

    def _valor(self, operando):
        if operando == '_':
            return None

        if isinstance(operando, str) and operando.startswith('"'):
            return operando[1:-1]

        try:
            if isinstance(operando, (int, float)):
                return operando
            if '.' in str(operando):
                return float(operando)
            return int(operando)
        except (ValueError, TypeError):
            pass

        return self.memoria.get(operando, 0)