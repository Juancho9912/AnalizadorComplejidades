# utils/helpers.py
# Clases base del AST

class ASTNode: pass

class Sequence(ASTNode):
    def __init__(self, stmts): self.stmts = [s for s in stmts if s]

class Assign(ASTNode):
    def __init__(self, name, expr): self.name, self.expr = name, expr

class Number(ASTNode):
    def __init__(self, v): self.v = int(v)

class Var(ASTNode):
    def __init__(self, n): self.n = n

class For(ASTNode):
    def __init__(self, var, start, end, body):
        self.var, self.start, self.end, self.body = var, start, end, body

class While(ASTNode):
    def __init__(self, cond, body):
        self.cond, self.body = cond, body

class Repeat(ASTNode):
    def __init__(self, body, cond):
        self.body, self.cond = body, cond

class If(ASTNode):
    def __init__(self, cond, then_b, else_b):
        self.cond, self.then_b, self.else_b = cond, then_b, else_b

class Call(ASTNode):
    def __init__(self, name, args):
        self.name, self.args = name, args

class FuncDef(ASTNode):
    def __init__(self, name, params, body):
        self.name, self.params, self.body = name, params, body

class Return(ASTNode):
    def __init__(self, expr): self.expr = expr

class ExprBin(ASTNode):
    def __init__(self, op, a, b):
        self.op, self.a, self.b = op, a, b

class Length(ASTNode):
    def __init__(self, name): self.name = name
