from lexer_parser import parse_pseudocode
from complexity_analyzer import Analyzer, cost_to_str

def test_factorial():
    src = open("examples/factorial.txt").read()
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    w,b,av = analyzer.analyze()
    print("Factorial ->", cost_to_str(w))
    assert "n" in cost_to_str(w)

def test_fibonacci():
    src = open("examples/fibonacci.txt").read()
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    w,b,av = analyzer.analyze()
    print("Fibonacci ->", cost_to_str(w))
