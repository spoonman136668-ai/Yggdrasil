"""DEV exact arithmetic control; explicit expressions only, otherwise abstain."""
import ast
import re
from fractions import Fraction


class Unsupported(ValueError):
    pass


def arithmetic(text):
    if not isinstance(text, bytes) or not 1 <= len(text) <= 128:
        raise Unsupported('expression size')
    if not re.fullmatch(rb'[0-9+*/(). \t-]+', text) or b'**' in text or b'//' in text:
        raise Unsupported('unsupported syntax')
    try:
        root = ast.parse(text.decode('ascii').strip(), mode='eval')
    except (SyntaxError, ValueError) as exc:
        raise Unsupported('invalid expression') from exc
    if sum(1 for _ in ast.walk(root)) > 48:
        raise Unsupported('expression complexity')

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            result = Fraction(node.value)
        elif isinstance(node, ast.Constant) and type(node.value) is float:
            result = Fraction(ast.get_source_segment(text.decode('ascii').strip(), node))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
            result = visit(node.operand)
            if isinstance(node.op, ast.USub):
                result = -result
        elif isinstance(node, ast.BinOp) and type(node.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                result = a + b
            elif isinstance(node.op, ast.Sub):
                result = a - b
            elif isinstance(node.op, ast.Mult):
                result = a * b
            else:
                if not b:
                    raise Unsupported('zero denominator')
                result = a / b
        else:
            raise Unsupported('unsupported node')
        if max(result.numerator.bit_length(), result.denominator.bit_length()) > 256:
            raise Unsupported('arithmetic bound')
        return result
    return visit(root.body)


def scores(context, options):
    """Returns scores and coverage. No labels, answer position or oracle parsing."""
    if not 2 <= len(options) <= 16:
        raise ValueError('invalid option count')
    try:
        value = arithmetic(context.strip().removesuffix(b'?').removesuffix(b'='))
        matches = [arithmetic(option) == value for option in options]
    except Unsupported:
        return [0.] * len(options), False
    if sum(matches) != 1:
        return [0.] * len(options), False
    return [20. if matched else 0. for matched in matches], True
