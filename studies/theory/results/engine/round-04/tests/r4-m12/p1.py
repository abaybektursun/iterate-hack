"""r4-m12 prediction 1: the recipe's equivalence test E(a, g) is defined as sympy.parsing.latex.parse_latex
parsing plus evaluation at points drawn with numpy default_rng(0). Test scripts must use the Python standard
library only, so E cannot be implemented as written; a hand-written LaTeX evaluator would be a different
equivalence test, not the recipe. The script therefore reports not computable."""
import json

print(json.dumps({
    "measured": None,
    "refuted_by_met": False,
    "alt_measured": None,
    "not_computable": "The recipe's equivalence E(a, g) requires sympy.parsing.latex.parse_latex (with its antlr4 "
                      "backend) and numpy.random.default_rng(0) sample points; test scripts are restricted to the "
                      "standard library, and a substitute LaTeX parser or RNG would not be the recipe as written.",
    "example_row": None,
}))
