import sys
from lexer import CompilerLexer
from parser import CompilerParser
from semantic import AnalizadorSemantico
from codegen import GeneradorCodigo
from evaluator import Evaluador

# ─── Funciones auxiliares para estadísticas ─────────────────

def contar_estadisticas_sintacticas(ast):
    """
    Recibe el AST y devuelve:
    - nombre del programa
    - número de declaraciones de variables globales
    - número de instrucciones (statements) en el bloque principal
    - número de funciones definidas
    """
    # ast = ('programa', nombre, funciones, var_list, bloque)
    _, nombre, funciones, var_list, bloque = ast

    # Contar variables globales: suma de declaraciones en cada 'variables'
    total_vars_global = 0
    for var in var_list:   # cada var es ('variables', lista_declaraciones, tipo)
        _, declaraciones, _ = var
        total_vars_global += len(declaraciones)

    # Bloque principal: ('bloque', vars_locales, lista_statements)
    _, vars_locales, statements = bloque
    total_stmts = len(statements)

    total_funcs = len(funciones)

    return nombre, total_vars_global, total_stmts, total_funcs

def contar_variables_semanticas(tabla_simbolos):
    """
    Recibe la tabla de símbolos (objeto TablaSimbolos) y devuelve:
    - número de variables globales (ámbito índice 0)
    - número de variables locales (ámbitos > 0)
    """
    global_vars = 0
    local_vars = 0

    # La pila de ámbitos es una lista de diccionarios
    for i, ambito in enumerate(tabla_simbolos.pila):
        for info in ambito.values():
            if info['clase'] == 'variable':   # solo contamos variables, no funciones
                if i == 0:
                    global_vars += 1
                else:
                    local_vars += 1
    return global_vars, local_vars

# ─── Programa principal ─────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python main.py <archivo>')
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        source = f.read()

    # ========== FASE 1: ANÁLISIS LÉXICO ==========
    lexer = CompilerLexer()
    # Obtener todos los tokens en una lista para contarlos
    tokens = list(lexer.tokenize(source))
    print(f"\n[Fase 1] Total de tokens generados: {len(tokens)}")
    # (Opcional) Mostrar cada token
    # for tok in tokens:
    #     print(f"  {tok.type}: {tok.value}")

    # ========== FASE 2: ANÁLISIS SINTÁCTICO ==========
    parser = CompilerParser()
    ast = parser.parse(iter(tokens))

    if ast is None:
        print('[Compilador] Error sintáctico — no se puede continuar.')
        sys.exit(1)
    # Extraer estadísticas del AST
    prog_name, num_vars_global, num_stmts, num_funcs = contar_estadisticas_sintacticas(ast)

    print(f"\n[Fase 2] Programa '{prog_name}' reconocido correctamente.")
    print(f"        Declaraciones globales: {num_vars_global} variable(s).")
    print(f"        Instrucciones en el bloque principal: {num_stmts}.")
    print(f"        Funciones definidas: {num_funcs}.")

    # ========== FASE 3: ANÁLISIS SEMÁNTICO ==========
    semantico = AnalizadorSemantico()
    semantico.analizar(ast)   # este método ya imprime la tabla de símbolos

    # Contar variables desde la tabla de símbolos
    global_vars, local_vars = contar_variables_semanticas(semantico.tabla)
    print(f"\n[Fase 3] Variables globales declaradas: {global_vars}")
    print(f"        Variables locales (en funciones): {local_vars}")

    # Si hay errores semánticos, no continuamos
    if semantico.errores:
        sys.exit(1)

    # ========== FASE 4: GENERACIÓN DE CÓDIGO INTERMEDIO ==========
    codegen = GeneradorCodigo()
    codegen.generar(ast)   # este método ya imprime los cuádruplos

    # ========== FASE 5: EJECUCIÓN ==========
    # El ámbito global es el primer diccionario de la pila de la tabla
    tabla_global = semantico.tabla.pila[0] if semantico.tabla.pila else {}
    evaluador = Evaluador(tabla_global)
    evaluador.ejecutar(codegen.cuadruplos)