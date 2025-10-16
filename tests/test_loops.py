from lexer_parser import parse_pseudocode
from complexity_analyzer import Analyzer, cost_to_str

def test_simple_for():
    src = """
    for i <- 1 to n do
    begin
        x <- x + 1;
    end
    """
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    w, b, av = analyzer.analyze()
    print("Bucle for simple ->", cost_to_str(w))
    assert "n" in cost_to_str(w)

def test_nested_for():
    src = """
    for i <- 1 to n do
    begin
        for j <- 1 to n do
        begin
            x <- x + 1;
        end
    end
    """
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    w, b, av = analyzer.analyze()
    print("Bucle for anidado ->", cost_to_str(w))
    assert "n^2" in cost_to_str(w)

def test_while():
    src = """
    x <- n;
    while (x > 0) do
    begin
        x <- x - 1;
    end
    """
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    w, b, av = analyzer.analyze()
    print("While lineal ->", cost_to_str(w))
    assert "n" in cost_to_str(w)

def test_repeat_until():
    src = """
    x <- n;
    repeat
        x <- x - 1;
    until (x = 0);
    """
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    w, b, av = analyzer.analyze()
    print("Repeat-until ->", cost_to_str(w))
    assert "n" in cost_to_str(w)
