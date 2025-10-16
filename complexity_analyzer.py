"""
complexity_analyzer.py
----------------------
Analiza el AST y estima la complejidad (O, Ω, Θ) de un algoritmo.
"""

import math
import re
from utils.helpers import *

CONST = [{'const':1, 'n':0}]
def cost_const(k=1): return [{'const':k,'n':0}]
def cost_n_power(e=1): return [{'const':1,'n':e}]

def simplify(terms):
    d = {}
    for t in terms:
        e = t.get('n',0)
        c = t.get('const',0)
        d[e] = d.get(e,0) + c
    res = [{'const':c, 'n':e} for e,c in d.items()]
    res.sort(key=lambda x: -x['n'])
    return res

def add_cost(a,b): return simplify(a+b)
def mul_cost(a,b):
    res=[]
    for ta in a:
        for tb in b:
            const=ta['const']*tb['const']
            exp=ta['n']+tb['n']
            res.append({'const':const,'n':exp})
    return simplify(res)

def cost_to_str(terms):
    if not terms: return "0"
    dom=terms[0]
    e=dom['n']; c=dom['const']
    if e==0: return str(c)
    if c==1:
        return "n" if e==1 else f"n^{e}"
    else:
        return f"{c}*n^{e}" if e!=1 else f"{c}*n"

class Analyzer:
    def __init__(self, ast):
        self.ast = ast
        self.funcs = {}

    def analyze(self):
        if isinstance(self.ast, Sequence):
            for s in self.ast.stmts:
                if isinstance(s, FuncDef):
                    self.funcs[s.name] = s
        return self._analyze_node(self.ast)

    def _analyze_node(self, node):
        if node is None: return CONST, CONST, CONST
        if isinstance(node, Sequence):
            w,b,av=[],[],[]
            for s in node.stmts:
                w1,b1,av1=self._analyze_node(s)
                w=add_cost(w,w1); b=add_cost(b,b1); av=add_cost(av,av1)
            return simplify(w),simplify(b),simplify(av)

        if isinstance(node, Assign) or isinstance(node, Return):
            return CONST,CONST,CONST

        if isinstance(node, For):
            count=self._estimate_count(node.end)
            w,b,av=self._analyze_node(node.body)
            return mul_cost(count,w),mul_cost(count,b),mul_cost(count,av)

        if isinstance(node, While) or isinstance(node, Repeat):
            count=self._estimate_cond(node.cond)
            w,b,av=self._analyze_node(node.body)
            return mul_cost(count,w),mul_cost(count,b),mul_cost(count,av)

        if isinstance(node, If):
            w1,b1,av1=self._analyze_node(node.then_b)
            w2,b2,av2=self._analyze_node(node.else_b)
            worst=max(w1,w2,key=lambda x:x[0]['n'])
            best=min(b1,b2,key=lambda x:x[0]['n'])
            avg=simplify([{'const':(w1[0]['const']+w2[0]['const'])/2,'n':(w1[0]['n']+w2[0]['n'])/2}])
            return worst,best,avg

        if isinstance(node, Call):
            if node.name in self.funcs:
                fd=self.funcs[node.name]
                rec=self._detect_recursion(fd)
                if rec: return self._solve_master(*rec)
            return CONST,CONST,CONST

        if isinstance(node, FuncDef):
            w,b,av=self._analyze_node(node.body)
            rec=self._detect_recursion(node)
            if rec: return self._solve_master(*rec)
            return w,b,av

        return CONST,CONST,CONST

    def _estimate_count(self, expr):
        if isinstance(expr, Number): return cost_const(expr.v)
        if isinstance(expr, Var) and expr.n.lower()=='n': return cost_n_power(1)
        return cost_const(1)

    def _estimate_cond(self, cond):
        return cost_n_power(1) if 'n' in cond else cost_const(1)

    def _detect_recursion(self, funcdef):
        body_text=str(funcdef.body)
        matches=re.findall(r"call\s+"+funcdef.name+r"\s*\(([^)]*)\)",body_text)
        if not matches: return None
        a=len(matches)
        arg=matches[0]
        if "n/2" in arg: return (a,2,1)
        if "n-1" in arg: return (a,None,1)
        return (a,None,1)

    def _solve_master(self,a,b,f):
        if b is None: return simplify([{'const':1,'n':1}]),*([CONST]*2)
        exp=math.log(a,b)
        return simplify([{'const':1,'n':exp}]),*([CONST]*2)
