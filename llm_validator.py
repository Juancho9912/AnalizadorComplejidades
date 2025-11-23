import json

def get_llm_analysis(code_str):
    """
    Simula una consulta a un LLM para analizar complejidad.
    Retorna un diccionario con complexity, pattern y explanation.
    """
    code_lower = code_str.lower()
    
    # Regla 1: Divide y Vencerás (Binary Search)
    # Busca 'call' y '/ 2'
    if 'call' in code_lower and '/ 2' in code_lower:
        return {
            'complexity': 'O(log n)',
            'pattern': 'Divide y Vencerás',
            'explanation': 'Busca dividiendo el rango a la mitad.'
        }

    # Regla 2: Fuerza Bruta (Nested Loops)
    # Busca dos 'for' anidados. Simplificación: contar 'for'
    # Una detección más robusta requeriría parsing, pero esto es un mock.
    if code_lower.count('for ') >= 2:
        return {
            'complexity': 'O(n^2)',
            'pattern': 'Fuerza Bruta / Iterativo',
            'explanation': 'Recorre la matriz completa con doble bucle.'
        }

    # Regla 3: Recursión Múltiple (Fibonacci)
    # Busca múltiples 'call' en el código (indicativo de ramas recursivas múltiples)
    # Ojo: 'call' ... 'call'
    if code_lower.count('call ') >= 2:
        return {
            'complexity': 'O(2^n)',
            'pattern': 'Recursión Múltiple',
            'explanation': 'Múltiples llamadas recursivas generan crecimiento exponencial.'
        }

    # Regla 4: Recursión Lineal
    # Busca 'call' y '- 1'
    if 'call' in code_lower and '- 1' in code_lower:
        return {
            'complexity': 'O(n)',
            'pattern': 'Recursión Lineal',
            'explanation': 'Desciende uno por uno hasta el caso base.'
        }

    # Default
    return {
        'complexity': 'O(?)',
        'pattern': 'No detectado',
        'explanation': 'No se encontró un patrón conocido en este mock.'
    }

def compare_results(filename, analyzer_result, code_str):
    """
    Imprime una tabla comparativa entre el Analyzer y el LLM.
    """
    llm_result = get_llm_analysis(code_str)
    
    # Formatear el resultado del analyzer (que es una lista de dicts)
    # Asumimos que analyzer_result es el string ya formateado (ej: "n^2") 
    # o lo convertimos si viene crudo.
    # En main.py pasaremos el string ya convertido.
    
    print(f"\n--- Validación con LLM (Mock) para {filename} ---")
    print(f"{'Fuente':<20} | {'Complejidad':<15} | {'Patrón / Detalles':<30}")
    print("-" * 70)
    print(f"{'Analyzer (Algorítmico)':<20} | {analyzer_result:<15} | {'Análisis estático AST'}")
    print(f"{'LLM (Simulado)':<20} | {llm_result['complexity']:<15} | {llm_result['pattern']}")
    print("-" * 70)
    print(f"Explicación LLM: {llm_result['explanation']}\n")
