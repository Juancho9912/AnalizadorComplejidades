"""
lexer_parser.py
---------------
Define la gramática del pseudocódigo y construye el parser con Lark.
"""

from lark import Lark, Transformer, v_args
from utils.helpers import (
    Sequence, Assign, Number, Var, For, While, Repeat,
    If, Call, FuncDef, Return, ExprBin, Length
)

def load_grammar():
    with open("utils/grammar.lark", "r", encoding="utf-8") as f:
        return f.read()

@v_args(inline=True)
class ToAST(Transformer):
    def start(self, *stmts):
        return Sequence(list(stmts))
    def funcdef(self, name, params=None, *stmts):
        pname = name.value
        params_list = []
        if isinstance(params, list):
            params_list = [p.value for p in params]
        return FuncDef(pname, params_list, Sequence(stmts))
    def params(self, *names):
        return list(names)
    def assign(self, name, expr):
        return Assign(name.value, expr)
    def number(self, token):
        return Number(token.value)
    def var(self, name):
        return Var(name.value)
    def length(self, name):
        return Length(name.value)
    def for_loop(self, var, start, end, *stmts):
        return For(var.value, start, end, Sequence(stmts))
    def while_loop(self, cond, *stmts):
        return While(str(cond).strip(), Sequence(stmts))
    def repeat_loop(self, *args):
        *body, cond = args
        return Repeat(Sequence(body), str(cond).strip())
    def if_stmt(self, cond, *rest):
        then_stmts = rest[0] if len(rest)>0 else Sequence([])
        else_stmts = rest[1] if len(rest)>1 else Sequence([])
        return If(str(cond).strip(), then_stmts, else_stmts)
    def call_stmt(self, name, args=None):
        args_list = [] if args is None else list(args)
        return Call(name.value, args_list)
    def args(self, *exprs):
        return list(exprs)
    def return_stmt(self, expr):
        return Return(expr)
    def add(self, a, b): return ExprBin('+', a, b)
    def sub(self, a, b): return ExprBin('-', a, b)
    def mul(self, a, b): return ExprBin('*', a, b)
    def div(self, a, b): return ExprBin('/', a, b)
    def empty(self): return None

def parse_pseudocode(source: str):
    grammar = load_grammar()
    parser = Lark(grammar, parser='lalr', transformer=ToAST())
    return parser.parse(source)
