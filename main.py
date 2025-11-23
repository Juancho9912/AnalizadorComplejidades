"""
main.py
---------
Punto de entrada del Analizador de Complejidades.

Ejecuta el análisis sobre un archivo de pseudocódigo.
"""

from lexer_parser import parse_pseudocode
from complexity_analyzer import Analyzer, cost_to_str
from llm_validator import compare_results

def analyze_file(path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    print(f"Analizando: {path}\n")
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    worst, best, avg = analyzer.analyze()

    print("Resultados:")
    print(f"  Peor caso (O): {cost_to_str(worst)}")
    print(f"  Mejor caso (Ω): {cost_to_str(best)}")
    print(f"  Promedio (Θ): {cost_to_str(avg)}")
    
    if analyzer.log:
        print("\n  Explicación:")
        for line in analyzer.log:
            print(f"    - {line}")
            
    # Fase 2: Validación con LLM
    compare_results(path, cost_to_str(worst), src)
    
    print("-" * 50)


if __name__ == "__main__":
    import sys
    import os

    examples_path = "examples"
    if not os.path.exists(examples_path):
        print("No se encontró la carpeta de ejemplos.")
        sys.exit(1)

    for file in os.listdir(examples_path):
        if file.endswith(".txt"):
            analyze_file(os.path.join(examples_path, file))
