"""
complexity_analyzer.py
----------------------
Analiza el AST y estima la complejidad (O, Ω, Θ).
NUEVO: Genera un reporte detallado línea por línea (Node-by-Node).
"""

import math
import re
from utils.helpers import *

# ==========================================
# ESTRUCTURAS DE DATOS
# ==========================================
CONST = [{'const': 1, 'n': 0}]

def cost_const(k=1): return [{'const': k, 'n': 0}]
def cost_n_power(e=1): return [{'const': 1, 'n': e}]

def simplify(terms):
    d = {}
    for t in terms:
        e = t.get('n', 0)
        c = t.get('const', 0)
        d[e] = d.get(e, 0) + c
    res = [{'const': c, 'n': e} for e, c in d.items() if c != 0]
    if not res: res = [{'const': 0, 'n': 0}]
    res.sort(key=lambda x: -x['n'])
    return res

def add_cost(a, b): return simplify(a + b)

def mul_cost(a, b):
    res = []
    for ta in a:
        for tb in b:
            const = ta['const'] * tb['const']
            exp = ta['n'] + tb['n']
            res.append({'const': const, 'n': exp})
    return simplify(res)

def get_degree(cost):
    if not cost: return 0
    return cost[0]['n']

def cost_to_str(terms):
    if not terms: return "0"
    dom = terms[0]
    e = dom['n']
    c = dom['const']
    if c == 0: return "0"
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
        self.log = []        # Razonamiento matemático global
        self.details = []    # NUEVO: Reporte línea por línea (Indent, Texto, Costo)

    def analyze(self):
        # 1. Registrar funciones
        if isinstance(self.ast, Sequence):
            for s in self.ast.stmts:
                if isinstance(s, FuncDef):
                    self.funcs[s.name] = s
        
        # 2. Analizar nodo raíz
        return self._analyze_node(self.ast, depth=0)

    def _record(self, depth, text, cost):
        """Guarda el costo de una línea específica."""
        # CORRECCIÓN: Verificar si ya es string antes de convertir
        if isinstance(cost, str):
            c_str = cost
        else:
            c_str = cost_to_str(cost)
        self.details.append((depth, text, c_str))

    def _analyze_node(self, node, ignore_recursion_name=None, depth=0):
        if node is None: return CONST, CONST, CONST

        # --- SECUENCIAS (BLOQUES) ---
        if isinstance(node, Sequence):
            w, b, av = [], [], []
            for s in node.stmts:
                w1, b1, av1 = self._analyze_node(s, ignore_recursion_name, depth)
                w = add_cost(w, w1); b = add_cost(b, b1); av = add_cost(av, av1)
            return simplify(w), simplify(b), simplify(av)

        # --- FUNCIONES ---
        if isinstance(node, FuncDef):
            self._record(depth, f"Function {node.name}(...)", "Declaración")
            rec_params = self._detect_recursion_ast(node)
            if rec_params:
                # Análisis de recursión
                fn_w, fn_b, fn_av = self._analyze_node(node.body, node.name, depth + 1)
                final_w, final_b, final_av = self._solve_recursion(rec_params, fn_w)
                self._record(depth, "-> Costo Total Recursivo", cost_to_str(final_w))
                return final_w, final_b, final_av
            return self._analyze_node(node.body, ignore_recursion_name, depth + 1)

        # --- LOOPS (FOR) ---
        if isinstance(node, For):
            count = self._estimate_count(node.end)
            count_str = cost_to_str(count)
            
            self._record(depth, f"For Loop (iteraciones ~ {count_str})", f"Multiplica por {count_str}")
            
            # Analizar cuerpo
            w, b, av = self._analyze_node(node.body, ignore_recursion_name, depth + 1)
            
            total_w = mul_cost(count, w)
            total_b = mul_cost(count, b)
            total_av = mul_cost(count, av)
            
            self._record(depth, "-> Fin For Loop", cost_to_str(total_w))
            return total_w, total_b, total_av

        # --- LOOPS (WHILE) ---
        if isinstance(node, (While, Repeat)):
            count = self._estimate_cond(node.cond)
            count_str = cost_to_str(count)
            
            self._record(depth, f"While Loop (Condición: {count_str})", f"Multiplica por {count_str}")
            
            w, b, av = self._analyze_node(node.body, ignore_recursion_name, depth + 1)
            
            total_w = mul_cost(count, w)
            total_b = mul_cost(count, b)
            total_av = mul_cost(count, av)
            
            self._record(depth, "-> Fin While Loop", cost_to_str(total_w))
            return total_w, total_b, total_av

        # --- IF / ELSE ---
        if isinstance(node, If):
            self._record(depth, "If Condition", "O(1)")
            
            self._record(depth+1, "Rama Then:", "...")
            w1, b1, av1 = self._analyze_node(node.then_b, ignore_recursion_name, depth + 1)
            
            self._record(depth+1, "Rama Else:", "...")
            w2, b2, av2 = self._analyze_node(node.else_b, ignore_recursion_name, depth + 1)
            
            worst = w1 if get_degree(w1) >= get_degree(w2) else w2
            best = b1 if get_degree(b1) <= get_degree(b2) else b2
            avg = simplify(add_cost(w1, w2))
            
            self._record(depth, "-> Fin If (Max ramas)", cost_to_str(worst))
            return worst, best, avg

        # --- LLAMADAS RECURSIVAS ---
        if isinstance(node, Call):
            # Si es la llamada recursiva que estamos resolviendo matemáticamente
            if ignore_recursion_name and node.name == ignore_recursion_name:
                self._record(depth, f"Call Recursivo: {node.name}", "Deferido a Ecuación")
                return CONST, CONST, CONST

            if node.name in self.funcs:
                fd = self.funcs[node.name]
                rec_params = self._detect_recursion_ast(fd)
                if rec_params:
                    # T(n) = a*T(n/b) + f(n)
                    fn_w, fn_b, fn_av = self._analyze_node(fd.body, fd.name, depth + 1)
                    res = self._solve_recursion(rec_params, fn_w)
                    self._record(depth, f"Call {node.name} (Recursión)", cost_to_str(res[0]))
                    return res
                else:
                    return self._analyze_node(fd.body, ignore_recursion_name, depth)
            
            self._record(depth, f"Call {node.name}", "O(1)")
            return CONST, CONST, CONST

        # --- OPERACIONES SIMPLES (Asignación, Return, etc) ---
        # Tratamos de describir qué operación es
        desc = "Instrucción Simple"
        if isinstance(node, Assign): desc = f"Assign: {node.name} <- ..."
        elif isinstance(node, Return): desc = "Return"
        elif isinstance(node, ExprBin): desc = "Operación Matemática"
        
        # Ojo: No imprimimos el detalle de cada suma pequeña para no saturar, 
        # pero sí las asignaciones importantes.
        if isinstance(node, (Assign, Return)):
            self._record(depth, desc, "O(1)")
            
        return CONST, CONST, CONST

    # ==========================================
    # UTILIDADES (Lógica Matemática)
    # ==========================================

    def _estimate_count(self, expr):
        if isinstance(expr, Var) and expr.n.lower() == 'n': return cost_n_power(1)
        if isinstance(expr, ExprBin):
            if (isinstance(expr.a, Var) and expr.a.n.lower() == 'n') or \
               (isinstance(expr.b, Var) and expr.b.n.lower() == 'n'):
                return cost_n_power(1)
        return cost_const(1)

    def _estimate_cond(self, cond):
        s = str(cond).lower()
        if 'n' in s: return cost_n_power(1)
        if re.search(r'[a-zA-Z]', s): return cost_n_power(1)
        return cost_const(1)

    def _detect_recursion_ast(self, funcdef):
        calls = []
        self._find_calls_deep(funcdef.body, funcdef.name, calls)
        if not calls: return None
        a = len(calls)
        rec_type, b = 'sub', 1
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

    def _find_calls_deep(self, node, target_name, calls_list):
        if node is None: return
        if isinstance(node, Call) and node.name == target_name:
            calls_list.append(node)
        if hasattr(node, '__dict__'):
            for key, val in vars(node).items():
                if isinstance(val, list):
                    for item in val:
                        if hasattr(item, '__class__'): self._find_calls_deep(item, target_name, calls_list)
                elif hasattr(val, '__class__'): self._find_calls_deep(val, target_name, calls_list)

    def _solve_recursion(self, params, fn_cost):
        a, r_type, b = params
        d = get_degree(fn_cost)
        explanation = ""
        
        if r_type == 'div':
            explanation = f"Recurrencia División: T(n) = {a}T(n/{b}) + O(n^{d})"
            log_b_a = math.log(a, b) if b > 1 else 0
            if log_b_a > d:
                res = simplify([{'const':1, 'n': log_b_a}])
            elif math.isclose(log_b_a, d):
                res = simplify([{'const':1, 'n': d}]) # n^d log n simplificado
            else:
                res = fn_cost
        elif r_type == 'sub':
            if a == 1:
                explanation = f"Recurrencia Lineal: T(n) = T(n-1) + O(n^{d})"
                res = simplify([{'const':1, 'n': d + 1}])
            else:
                explanation = f"Recurrencia Múltiple: T(n) = {a}T(n-1)"
                res = simplify([{'const':1, 'n': 99}]) # Exponencial
        
        self.log.append(explanation)
        return res, res, res