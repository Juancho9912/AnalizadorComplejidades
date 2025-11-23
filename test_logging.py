from complexity_analyzer import Analyzer, cost_to_str
from lexer_parser import parse_pseudocode

def test_logging():
    src = """
    function test(n)
    begin
        for i <- 1 to n do
        begin
            x <- x + 1;
        end
    end
    """
    print("--- Testing Logging for For Loop ---")
    ast = parse_pseudocode(src)
    analyzer = Analyzer(ast)
    analyzer.analyze()
    for log in analyzer.log:
        print("LOG:", log)

    src_rec = """
    function factorial(n)
    begin
        if n = 1 then return 1;
        else return n * factorial(n-1);
    end
    """
    print("\n--- Testing Logging for Recursion ---")
    ast = parse_pseudocode(src_rec)
    analyzer = Analyzer(ast)
    analyzer.analyze()
    for log in analyzer.log:
        print("LOG:", log)

if __name__ == "__main__":
    test_logging()
