import ast
import operator as op


OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Lt: op.lt,
    ast.Gt: op.gt,
    ast.LtE: op.le,
    ast.GtE: op.ge
}


def safe_eval(expr):
    """
    Eval is evil. Use safe_eval to evaluate arithmetic safely.
    :param expr: String representation of arithmetic using only +, -, *
    :return: Integer result of the operations
    """
    try:
        return _eval(ast.parse(expr, mode='eval').body)

    except Exception as exc:
        raise TypeError(f"{expr} failed in safe_eval") from exc


def _eval(ast_node):
    if isinstance(ast_node, ast.Num):
        return ast_node.n
    elif isinstance(ast_node, ast.Compare):
        return _eval_compare(ast_node)
    elif isinstance(ast_node, ast.BinOp) and type(ast_node.op) in OPERATORS:
        return OPERATORS[type(ast_node.op)](_eval(ast_node.left), _eval(ast_node.right))
    elif isinstance(ast_node.op, ast.USub):
        return op.neg(_eval(ast_node.operand))
    else:
        raise TypeError(f"Disallowed operator in {ast_node}")


def _eval_compare(ast_node):
    left = _eval(ast_node.left)
    for operation, comp in zip(ast_node.ops, ast_node.comparators):
        right = _eval(comp)
        if type(operation) not in OPERATORS:
            raise TypeError(f"Disallowed operator in {ast_node}")
        if OPERATORS[type(operation)](left, right):
            left = right
        else:
            return False
    return True
