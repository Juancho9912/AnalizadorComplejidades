"""
llm_validator.py
----------------
Valida la complejidad algorítmica usando la API de OpenAI (GPT).
Carga la API KEY desde un archivo .env para seguridad.
Incluye un sistema de respaldo (Mock) por si falla la conexión.
"""
import json
import os
from dotenv import load_dotenv  # Importamos la librería para .env
from openai import OpenAI

# ==============================================================================
# 🔑 CONFIGURACIÓN
# ==============================================================================
# Carga las variables del archivo .env
load_dotenv()

# Obtiene la clave del entorno. Si no existe, será None.
API_KEY = os.getenv("OPENAI_API_KEY")
# ==============================================================================

def get_llm_analysis(code_str):
    """
    Envía el código a GPT-3.5/4 para análisis.
    Retorna un diccionario: {complexity, pattern, explanation}
    """
    try:
        # Verificación de seguridad antes de intentar conectar
        if not API_KEY:
            print("⚠️ [Aviso] No se encontró OPENAI_API_KEY en el archivo .env")
            raise ValueError("Falta API Key")

        if API_KEY.startswith("sk-...") or "tu_clave" in API_KEY.lower():
             raise ValueError("La API Key parece ser un placeholder no válido.")

        client = OpenAI(api_key=API_KEY)

        # Prompt de Ingeniería para forzar JSON
        system_prompt = (
            "Eres un experto en algoritmia y Big-O. "
            "Tu tarea es analizar pseudocódigo y responder ÚNICAMENTE con un objeto JSON válido. "
            "El JSON debe tener estas claves: 'complexity' (ej: 'O(n)'), "
            "'pattern' (ej: 'Fuerza Bruta', 'Divide y Vencerás'), "
            "y 'explanation' (una frase breve en español)."
        )

        user_prompt = f"Analiza este algoritmo:\n\n{code_str}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Puedes cambiar a "gpt-4" si tienes acceso
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0, # Temperatura 0 para ser más determinista
            response_format={"type": "json_object"} # Fuerza salida JSON
        )

        # Parsear la respuesta
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Normalizar claves por si acaso
        return {
            "complexity": data.get("complexity", "O(?)"),
            "pattern": data.get("pattern", "No identificado"),
            "explanation": data.get("explanation", "Sin explicación")
        }

    except Exception as e:
        print(f"⚠️ [Aviso] Fallo en conexión con GPT ({str(e)})")
        print("   -> Usando sistema de respaldo (Mock) para continuar.")
        return _mock_analysis(code_str)

def _mock_analysis(code_str):
    """
    Sistema de respaldo (Simulación) para cuando no hay internet o API Key.
    """
    code = code_str.lower()
    
    # Reglas heurísticas simples
    if "call" in code and "/ 2" in code:
        return {'complexity': 'O(log n)', 'pattern': 'Divide y Vencerás', 'explanation': 'División recursiva del problema.'}
    
    # Detección de Fibonacci (Recursión múltiple)
    import re
    calls = re.findall(r"call\s+\w+", code)
    if len(calls) >= 2 and ("+" in code or "*" in code):
         return {'complexity': 'O(2^n)', 'pattern': 'Recursión Múltiple', 'explanation': 'Múltiples llamadas recursivas generan árbol exponencial.'}

    if "for" in code:
        # Contar anidación de indentación o 'begin' dentro de 'for'
        if code.count("for ") >= 3:
             return {'complexity': 'O(n^3)', 'pattern': 'Cúbico / Fuerza Bruta', 'explanation': 'Triple bucle anidado detectado.'}
        if code.count("for ") == 2:
             return {'complexity': 'O(n^2)', 'pattern': 'Cuadrático / Fuerza Bruta', 'explanation': 'Doble bucle anidado detectado.'}
        return {'complexity': 'O(n)', 'pattern': 'Iterativo Simple', 'explanation': 'Bucle simple detectado.'}

    if "call" in code and "- 1" in code:
        return {'complexity': 'O(n)', 'pattern': 'Recursión Lineal', 'explanation': 'Descenso lineal recursivo.'}
        
    return {'complexity': 'O(1)', 'pattern': 'Constante', 'explanation': 'Sin bucles ni recursión aparentes.'}

def compare_results(filename, my_result, code_str):
    llm_data = get_llm_analysis(code_str)
    
    llm_c = llm_data['complexity']
    pattern = llm_data['pattern']
    expl = llm_data['explanation']
    
    # Formateo visual de tabla
    print(f"\n--- Validación con GPT (IA) para {filename} ---")
    print(f"{'Fuente':<25} | {'Complejidad':<15} | {'Patrón / Detalles'}")
    print("-" * 75)
    print(f"{'Analyzer (Algorítmico)':<25} | {str(my_result):<15} | Análisis estático AST")
    print(f"{'GPT (OpenAI)':<25} | {llm_c:<15} | {pattern}")
    print("-" * 75)
    print(f"Explicación GPT: {expl}\n")