"""
complexity_analyzer.py
----------------------
Analiza el AST y estima la complejidad (O, Ω, Θ) de un algoritmo.
CORREGIDO FINAL:
1. Incluye _detect_recursion_ast para arreglar el error de atributo.
2. Incluye el arreglo para bucles While (Heurística pesimista).
3. Detecta n^2 y recursión correctamente.
"""

import math
from utils.helpers import *

# ==========================================
# ESTRUCTURAS DE DATOS PARA COMPLEJIDAD
# ==========================================
# Representamos el costo como una lista de términos: [{'const': 1, 'n': 2}] es n^2

CONST = [{'const': 1, 'n': 0}]

def cost_const(k=1): 
    return [{'const': k, 'n': 0}]

def cost_n_power(e=1): 
    return [{'const': 1, 'n': e}]

def simplify(terms):
    """Simplifica y ordena términos polinómicos (ej: n + n -> 2n)."""
    d = {}
    for t in terms:
        e = t.get('n', 0)
        c = t.get('const', 0)
        d[e] = d.get(e, 0) + c
    
    # Filtra términos con coeficiente 0
    res = [{'const': c, 'n': e} for e, c in d.items() if c != 0]
    if not res: res = [{'const': 0, 'n': 0}]
    
    # Ordenar de mayor exponente a menor (n^2 antes que n)
    res.sort(key=lambda x: -x['n'])
    return res

def add_cost(a, b): 
    return simplify(a + b)

def mul_cost(a, b):
    res = []
    for ta in a:
        for tb in b:
            const = ta['const'] * tb['const']
            exp = ta['n'] + tb['n']
            res.append({'const': const, 'n': exp})
    return simplify(res)

def get_degree(cost):
    """Devuelve el exponente más alto de 'n'."""
    if not cost: return 0
    return cost[0]['n']

def cost_to_str(terms):
    """Convierte la estructura de costo a string legible (ej. n^2)."""
    if not terms: return "0"
    
    # Tomamos el término dominante (el primero, ya que están ordenados)
    dom = terms[0]
    e = dom['n']
    c = dom['const']
    
    if c == 0: return "0"
    
    # Formateo visual
    coeff = "" if c == 1 else f"{c}"
    if e == 0: return str(c)
    if e == 1: return f"{coeff}n" if coeff == "" else f"{coeff}*n"
    
    base = f"n^{e}"
    return base if coeff == "" else f"{coeff}*{base}"

# ==========================================
# CLASE ANALYZER PRINCIPAL
# ==========================================

class Analyzer:
    def __init__(self, ast):
        self.ast = ast
        self.funcs = {}
        self.log = []

    def analyze(self):
        # 1. Registrar funciones para poder analizar recursión luego
        if isinstance(self.ast, Sequence):
            for s in self.ast.stmts:
                if isinstance(s, FuncDef):
                    self.funcs[s.name] = s
        
        # 2. Analizar el nodo raíz
        return self._analyze_node(self.ast)

    def _analyze_node(self, node, ignore_recursion_name=None):
        """
        Retorna una tupla (Peor, Mejor, Promedio).
        ignore_recursion_name: Evita bucles infinitos al calcular f(n) en recursión.
        """
        if node is None: return CONST, CONST, CONST

        # --- BLOQUES Y SECUENCIAS ---
        if isinstance(node, Sequence):
            w, b, av = [], [], []
            for s in node.stmts:
                w1, b1, av1 = self._analyze_node(s, ignore_recursion_name)
                w = add_cost(w, w1); b = add_cost(b, b1); av = add_cost(av, av1)
            return simplify(w), simplify(b), simplify(av)

        # --- OPERACIONES SIMPLES (O(1)) ---
        if isinstance(node, (Assign, Return, ExprBin, Number, Var, Length)):
            return CONST, CONST, CONST
        
        # Si el agente agregó clases nuevas que no conocemos, asumimos O(1)
        if type(node).__name__ == 'ArrayAccess':
            return CONST, CONST, CONST

        # --- LOOPS ---
        if isinstance(node, For):
            count = self._estimate_count(node.end) # Detecta si es 'n'
            w, b, av = self._analyze_node(node.body, ignore_recursion_name)
            res_w = mul_cost(count, w)
            self.log.append(f"Bucle For detectado: iteraciones ~ {cost_to_str(count)}, cuerpo ~ {cost_to_str(w)} -> Total: {cost_to_str(res_w)}")
            return res_w, mul_cost(count, b), mul_cost(count, av)

        if isinstance(node, (While, Repeat)):
            # Heurística mejorada: Si hay letras en la condición, es O(n)
            count = self._estimate_cond(node.cond)
            w, b, av = self._analyze_node(node.body, ignore_recursion_name)
            res_w = mul_cost(count, w)
            self.log.append(f"Bucle While/Repeat detectado: condición '{node.cond}' -> iteraciones estimadas {cost_to_str(count)}. Total: {cost_to_str(res_w)}")
            return res_w, mul_cost(count, b), mul_cost(count, av)

        # --- CONDICIONALES ---
        if isinstance(node, If):
            w1, b1, av1 = self._analyze_node(node.then_b, ignore_recursion_name)
            w2, b2, av2 = self._analyze_node(node.else_b, ignore_recursion_name)
            
            worst = w1 if get_degree(w1) >= get_degree(w2) else w2
            best = b1 if get_degree(b1) <= get_degree(b2) else b2
            avg = simplify(add_cost(w1, w2))
            return worst, best, avg

        # --- LLAMADAS Y RECURSIÓN ---
        if isinstance(node, Call):
            if ignore_recursion_name and node.name == ignore_recursion_name:
                return CONST, CONST, CONST # Costo base de la llamada

            if node.name in self.funcs:
                fd = self.funcs[node.name]
                rec_params = self._detect_recursion_ast(fd) # <--- Aquí fallaba antes
                if rec_params:
                    # T(n) = a*T(n/b) + f(n)
                    fn_w, fn_b, fn_av = self._analyze_node(fd.body, ignore_recursion_name=fd.name)
                    return self._solve_recursion(rec_params, fn_w)
                else:
                    return self._analyze_node(fd.body)
            
            return CONST, CONST, CONST

        if isinstance(node, FuncDef):
            rec_params = self._detect_recursion_ast(node)
            if rec_params:
                fn_w, fn_b, fn_av = self._analyze_node(node.body, ignore_recursion_name=node.name)
                return self._solve_recursion(rec_params, fn_w)
            return self._analyze_node(node.body)

        return CONST, CONST, CONST

    # ==========================================
    # UTILIDADES (MÉTODOS QUE FALTABAN)
    # ==========================================

    def _estimate_count(self, expr):
        """Estima iteraciones de un FOR."""
        if isinstance(expr, Var) and expr.n.lower() == 'n': 
            return cost_n_power(1)
        if isinstance(expr, ExprBin):
            if (isinstance(expr.a, Var) and expr.a.n.lower() == 'n') or \
               (isinstance(expr.b, Var) and expr.b.n.lower() == 'n'):
                return cost_n_power(1)
        return cost_const(1)

    def _estimate_cond(self, cond_node_or_str):
        """
        Heurística mejorada para condiciones de While.
        Si la condición tiene variables, asumimos O(n).
        """
        s = str(cond_node_or_str).lower()
        if 'n' in s: return cost_n_power(1)
        import re
        if re.search(r'[a-zA-Z]', s): # Si hay letras, asume O(n)
            return cost_n_power(1)
        return cost_const(1)

    def _detect_recursion_ast(self, funcdef):
        """Busca llamadas recursivas navegando el AST."""
        calls = []
        self._find_calls(funcdef.body, funcdef.name, calls)
        
        if not calls: return None
        
        a = len(calls) 
        rec_type = 'sub'
        b = 1
        
        first_call = calls[0]
        if first_call.args:
            arg = first_call.args[0]
            if isinstance(arg, ExprBin) and arg.op == '/':
                rec_type = 'div'
                try:
                    if isinstance(arg.b, Number): b = arg.b.v
                except: pass
            elif isinstance(arg, ExprBin) and arg.op == '-':
                rec_type = 'sub'
        
        return (a, rec_type, b)

    def _find_calls(self, node, target_name, calls_list):
        """Helper recursivo para encontrar nodos Call."""
        if node is None: return
        
        if hasattr(node, 'stmts'): 
            for s in node.stmts: self._find_calls(s, target_name, calls_list)
        elif hasattr(node, 'body'): 
            self._find_calls(node.body, target_name, calls_list)
        elif hasattr(node, 'then_b'): 
            self._find_calls(node.then_b, target_name, calls_list)
            self._find_calls(node.else_b, target_name, calls_list)
        
        if isinstance(node, Call):
            if node.name == target_name:
                calls_list.append(node)
            for arg in node.args:
                self._find_calls(arg, target_name, calls_list)
        elif isinstance(node, Return):
            self._find_calls(node.expr, target_name, calls_list)
        elif isinstance(node, Assign):
            self._find_calls(node.expr, target_name, calls_list)
        elif isinstance(node, ExprBin):
            self._find_calls(node.a, target_name, calls_list)
            self._find_calls(node.b, target_name, calls_list)

    def _solve_recursion(self, params, fn_cost):
        """Aplica Teorema Maestro o Recurrencia Lineal."""
        a, r_type, b = params
        d = get_degree(fn_cost)
        
        if r_type == 'div':
            log_b_a = math.log(a, b) if b > 1 else 0
            if log_b_a > d:
                self.log.append(f"Teorema Maestro Caso 1: log_b(a) ({log_b_a:.2f}) > d ({d}). El costo recursivo domina.")
                return simplify([{'const':1, 'n': log_b_a}]), simplify([{'const':1, 'n': log_b_a}]), simplify([{'const':1, 'n': log_b_a}])
            elif math.isclose(log_b_a, d):
                self.log.append(f"Teorema Maestro Caso 2: log_b(a) == d ({d}). Costo n^d * log n.")
                return simplify([{'const':1, 'n': d}]), simplify([{'const':1, 'n': d}]), simplify([{'const':1, 'n': d}])
            else:
                self.log.append(f"Teorema Maestro Caso 3: log_b(a) ({log_b_a:.2f}) < d ({d}). El costo de f(n) domina.")
                return fn_cost, fn_cost, fn_cost

        elif r_type == 'sub':
            if a == 1:
                new_deg = d + 1
                self.log.append(f"Recurrencia Lineal: T(n) = T(n-1) + O(n^{d}). Total -> O(n^{new_deg})")
                res = simplify([{'const':1, 'n': new_deg}])
                return res, res, res
            else:
                # Exponencial
                self.log.append(f"Recurrencia Lineal: T(n) = {a}T(n-1). Crecimiento exponencial O({a}^n).")
                return simplify([{'const':1, 'n': 99}]), simplify([{'const':1, 'n': 99}]), simplify([{'const':1, 'n': 99}])
        
        return CONST, CONST, CONST