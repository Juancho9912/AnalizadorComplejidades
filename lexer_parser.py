"""
lexer_parser.py
---------------
Define la gramática del pseudocódigo y construye el parser con Lark.
"""

from lark import Lark, Transformer, v_args
from utils.helpers import (
    Sequence, Assign, Number, Var, For, While, Repeat,
    If, Call, FuncDef, Return, ExprBin, Length, ArrayAccess
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
        return Assign(name.value if hasattr(name, 'value') else name, expr)
    def array_access(self, name, expr):
        return ArrayAccess(name.value, expr)
    def number(self, token):
        return Number(token.value)
    def var(self, name):
        return Var(name.value)
    def length(self, name):
        return Length(name.value)
    def for_loop(self, var, start, end, *stmts):
        return For(var.value, start, end, Sequence(stmts))
    def loop_body(self, *stmts):
        return Sequence(list(stmts))
    def if_body(self, *stmts):
        return Sequence(list(stmts))
    def block(self, *stmts):
        return Sequence(list(stmts))
    
    def else_part(self, body):
        return body
    
    def elif_part(self, expr, body):
        return If(str(expr).strip(), body, Sequence([]))

    def if_stmt(self, cond, then_b, *rest):
        # rest can be (else_b,) or (elif_node,) or (elif_node, else_b)
        else_b = Sequence([])
        
        if len(rest) == 1:
            if isinstance(rest[0], If): # elif_node
                else_b = rest[0]
            else: # else_b
                else_b = rest[0]
        elif len(rest) == 2:
            # elif_node, else_b
            elif_node = rest[0]
            final_else = rest[1]
            # Inject final_else into elif_node's else_b
            # Note: This assumes elif_node is an If created by elif_part
            elif_node.else_b = final_else
            else_b = elif_node
            
        return If(str(cond).strip(), then_b, else_b)

    def call_stmt(self, name, args=None):
        args_list = [] if args is None else list(args)
        return Call(name.value, args_list)
        
    def func_call(self, name, args=None):
        args_list = [] if args is None else list(args)
        return Call(name.value, args_list)

    def comp_op(self, a, op, b):
        return ExprBin(op.value, a, b)

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
    parser = Lark(grammar, parser='earley')
    tree = parser.parse(source)
    return ToAST().transform(tree)
