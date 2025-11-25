"""
main.py
- Muestra el AST.
- Muestra Eficiencia Línea por Línea (Trace).
- Muestra Totales.
- Compara con LLM.
"""
from lexer_parser import parse_pseudocode
from complexity_analyzer import Analyzer, cost_to_str
import llm_validator
import sys
import os
import visualizer  # Asegúrate de tener el visualizer.py de la fase anterior

def analyze_file(path):
    filename = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    print(f"\n{'='*60}")
    print(f"ANALIZANDO: {filename}")
    print(f"{'='*60}\n")
    
    try:
        ast = parse_pseudocode(src)
        
        # 1. Visualización del Árbol (Estructural)
        print("Estructura del Código (AST):")
        visualizer.print_ast_tree(ast)
        print("-" * 50)

        # 2. Análisis Matemático
        analyzer = Analyzer(ast)
        worst, best, avg = analyzer.analyze()
        worst_str = cost_to_str(worst)

        # --- NUEVO: IMPRESIÓN DEL ANÁLISIS LÍNEA POR LÍNEA ---
        print("\nANÁLISIS DE EFICIENCIA POR LÍNEA:")
        print(f"{'Estructura / Instrucción':<45} | {'Costo Local/Acumulado'}")
        print("-" * 70)
        
        for depth, text, cost in analyzer.details:
            indent = "  " * depth
            # Truncar texto muy largo para que no rompa la tabla
            pretty_text = (indent + "└ " + text)[:43] 
            print(f"{pretty_text:<45} | {cost}")
        print("-" * 70)

        # 3. Resultados Totales
        print("\nRESULTADOS TOTALES:")
        print(f"  • Peor caso (O): {worst_str}")
        print(f"  • Mejor caso (Ω): {cost_to_str(best)}")
        print(f"  • Promedio (Θ): {cost_to_str(avg)}")
        
        if analyzer.log:
            print("\nRazonamiento Teórico:")
            for step in analyzer.log:
                print(f"  -> {step}")

        # 4. Validación con LLM
        # Enviamos el código para que la IA también nos dé su opinión
        llm_validator.compare_results(filename, worst_str, src)

    except Exception as e:
        print(f"❌ Error analizando {path}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    examples_path = "examples"
    if not os.path.exists(examples_path):
        print("Crea la carpeta 'examples' y pon tus .txt ahí.")
        sys.exit(1)

    # Filtramos para analizar tus archivos principales
    files = [f for f in os.listdir(examples_path) if f.endswith(".txt")]
    
    for file in files:
        analyze_file(os.path.join(examples_path, file))