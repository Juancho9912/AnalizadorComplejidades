
from lexer_parser import parse_pseudocode
from complexity_analyzer import Analyzer, cost_to_str
from utils.helpers import *

def debug_factorial():
    src = """
    function factorial(n)
    begin
        if (n == 1) then
            return 1;
        else
            return n * factorial(n-1);
        end
    end
    """
    print("--- Debug Factorial ---")
    ast = parse_pseudocode(src)
    print("AST:", ast)
    
    analyzer = Analyzer(ast)
    # Monkey patch _analyze_node to print debug info
    original_analyze = analyzer._analyze_node
    
    def debug_analyze(node, ignore=None):
        res = original_analyze(node, ignore)
        # print(f"Analyze({node}) -> {cost_to_str(res[0])}")
        return res
    
    analyzer._analyze_node = debug_analyze
    
    w, b, av = analyzer.analyze()
    print("Result:", cost_to_str(w))

def debug_nested_for():
    src = """
    for i <- 1 to n do
    begin
        for j <- 1 to n do
        begin
            x <- x + 1;
        end
    end
    """
    print("\n--- Debug Nested For ---")
    ast = parse_pseudocode(src)
    print("AST:", ast)
    
    analyzer = Analyzer(ast)
    w, b, av = analyzer.analyze()
    print("Result:", cost_to_str(w))

if __name__ == "__main__":
    debug_factorial()
    debug_nested_for()
