# utils/helpers.py
# Clases base del AST

class ASTNode:
    def __repr__(self): return self.__class__.__name__

class Sequence(ASTNode):
    def __init__(self, stmts): self.stmts = [s for s in stmts if s]
    def __repr__(self): return f"Seq({self.stmts})"

class Assign(ASTNode):
    def __init__(self, name, expr): self.name, self.expr = name, expr
    def __repr__(self): return f"Assign({self.name}, {self.expr})"

class Number(ASTNode):
    def __init__(self, v): self.v = int(v)
    def __repr__(self): return str(self.v)

class Var(ASTNode):
    def __init__(self, n): self.n = n
    def __repr__(self): return self.n

class For(ASTNode):
    def __init__(self, var, start, end, body):
        self.var, self.start, self.end, self.body = var, start, end, body
    def __repr__(self): return f"For({self.var}, {self.start}, {self.end}, {self.body})"

class While(ASTNode):
    def __init__(self, cond, body):
        self.cond, self.body = cond, body
    def __repr__(self): return f"While({self.cond}, {self.body})"

class Repeat(ASTNode):
    def __init__(self, body, cond):
        self.body, self.cond = body, cond
    def __repr__(self): return f"Repeat({self.cond}, {self.body})"

class If(ASTNode):
    def __init__(self, cond, then_b, else_b):
        self.cond, self.then_b, self.else_b = cond, then_b, else_b
    def __repr__(self): return f"If({self.cond}, {self.then_b}, {self.else_b})"

class Call(ASTNode):
    def __init__(self, name, args):
        self.name, self.args = name, args
    def __repr__(self): return f"Call({self.name}, {self.args})"

class FuncDef(ASTNode):
    def __init__(self, name, params, body):
        self.name, self.params, self.body = name, params, body
    def __repr__(self): return f"Func({self.name}, {self.body})"

class Return(ASTNode):
    def __init__(self, expr): self.expr = expr
    def __repr__(self): return f"Return({self.expr})"

class ExprBin(ASTNode):
    def __init__(self, op, a, b):
        self.op, self.a, self.b = op, a, b
    def __repr__(self): return f"({self.a} {self.op} {self.b})"

class Length(ASTNode):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Length({self.name})"

class ArrayAccess(ASTNode):
    def __init__(self, name, index):
        self.name, self.index = name, index
    def __repr__(self): return f"{self.name}[{self.index}]"
