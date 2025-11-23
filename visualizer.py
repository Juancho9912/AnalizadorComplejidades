from utils.helpers import *

def print_ast_tree(node, prefix="", is_last=True):
    """
    Imprime el AST en formato de árbol ASCII.
    """
    if node is None:
        return

    # Determinar el conector actual
    connector = "└── " if is_last else "├── "
    
    # Preparar el string a imprimir según el tipo de nodo
    node_str = ""
    children = []

    if isinstance(node, Sequence):
        node_str = "Sequence"
        children = node.stmts
    elif isinstance(node, FuncDef):
        params = ", ".join(node.params)
        node_str = f"FuncDef: {node.name}({params})"
        children = [node.body]
    elif isinstance(node, If):
        node_str = f"If: {node.cond}"
        children = [node.then_b]
        if node.else_b:
            children.append(node.else_b)
    elif isinstance(node, For):
        node_str = f"For: {node.var} <- {node.start} to {node.end}"
        children = [node.body]
    elif isinstance(node, While):
        node_str = f"While: {node.cond}"
        children = [node.body]
    elif isinstance(node, Repeat):
        node_str = f"Repeat Until: {node.cond}"
        children = [node.body]
    elif isinstance(node, Assign):
        node_str = f"Assign: {node.name} <- {node.expr}"
    elif isinstance(node, Return):
        node_str = f"Return: {node.expr}"
    elif isinstance(node, Call):
        args = ", ".join(map(str, node.args))
        node_str = f"Call: {node.name}({args})"
    else:
        # Nodos hoja o expresiones simples
        node_str = str(node)

    print(prefix + connector + node_str)

    # Preparar el prefijo para los hijos
    new_prefix = prefix + ("    " if is_last else "│   ")
    
    # Imprimir hijos
    count = len(children)
    for i, child in enumerate(children):
        is_last_child = (i == count - 1)
        print_ast_tree(child, new_prefix, is_last_child)
