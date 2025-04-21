from wizual_parser import parser
from wizual_helper import Table, read_csv

class EvalError(Exception):
    pass

def evaluate(node, sym):
    kind = node[0]
    if kind == "program":
        for stmt in node[1]:
            evaluate(stmt, sym)
    elif kind == "assign":
        name, expr = node[1], node[2]
        sym[name] = evaluate(expr, sym)
        return sym[name]
    elif kind == "binop":
        op, left_n, right_n = node[1], node[2], node[3]
        a = evaluate(left_n, sym)
        b = evaluate(right_n, sym)
        if isinstance(a, Table) or isinstance(b, Table):
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/': return a / b
            if op == '%': return a % b
            if op == '@': return a @ b
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/': return a / b
        if isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                raise EvalError("Cannot perform element-wise on lists of different lengths")
            if op == '+': return [a[i] + b[i] for i in range(len(a))]
            if op == '-': return [a[i] - b[i] for i in range(len(a))]
            if op == '*': return [a[i] * b[i] for i in range(len(a))]
            if op == '/': return [a[i] / b[i] for i in range(len(a))]
        if isinstance(a, list) and isinstance(b, (int, float)):
            if op == '+': return [x + b for x in a]
            if op == '-': return [x - b for x in a]
            if op == '*': return [x * b for x in a]
            if op == '/': return [x / b for x in a]
        if isinstance(b, list) and isinstance(a, (int, float)):
            if op == '+': return [a + x for x in b]
            if op == '-': return [a - x for x in b]
            if op == '*': return [a * x for x in b]
            if op == '/': return [a / x for x in b]
        raise EvalError(f"Unsupported operand types for '{op}': {type(a)} and {type(b)}")
    elif kind == "number":
        return node[1]
    elif kind == "string":
        return node[1]
    elif kind == "var":
        name = node[1]
        if name not in sym:
            raise NameError(f"Undefined variable '{name}'")
        return sym[name]
    elif kind == "list":
        return [evaluate(elem, sym) for elem in node[1]]
    elif kind == "slice":
        base_n, sl = node[1], node[2]
        base = evaluate(base_n, sym)
        if isinstance(base, list):
            if sl[0] == "index":
                return base[sl[1]]
            data = base[sl[1]:sl[2]]
            return data
        if isinstance(base, Table):
            if sl[0] == "index":
                return base.data[sl[1]]
            rows = base.data[sl[1]:sl[2]]
            return Table(rows=len(rows), cols=base.cols, headers=base.headers, data=rows)
        raise TypeError("Cannot slice non-indexable type")
    elif kind == "while":
        cond_n, block_n = node[1], node[2]
        while evaluate(cond_n, sym):
            evaluate(block_n, sym)
    elif kind == "if":
        cond_n, then_n = node[1], node[2]
        if evaluate(cond_n, sym):
            evaluate(then_n, sym)
    elif kind == "block":
        for stmt in node[1]:
            evaluate(stmt, sym)
    elif kind == "bool":
        op, left_n, right_n = node[1], node[2], node[3]
        a = evaluate(left_n, sym)
        b = evaluate(right_n, sym)
        if op == "==": return a == b
        if op == "!=": return a != b
        if op == "<":  return a < b
        if op == ">":  return a > b
        if op == "<=": return a <= b
        if op == ">=": return a >= b
        raise EvalError(f"Unknown boolean operator '{op}'")
    elif kind == "table":
        params = node[1]
        rows = 0
        cols = evaluate(params.get("cols", 0), sym)
        headers = (evaluate(params["headers"], sym)
                   if "headers" in params else [str(i) for i in range(cols)])
        return Table(rows=rows, cols=cols, headers=headers)
    elif kind == "call":
        name, args_n = node[1], node[2]
        args = [evaluate(a, sym) for a in args_n]
        builtins = {
            "sum":    lambda a: sum(a[0]) if isinstance(a[0], list) else None,
            "avg":    lambda a: sum(a[0]) / len(a[0]),
            "min":    lambda a: min(a[0]),
            "max":    lambda a: max(a[0]),
            "sort":   lambda a: sorted(a[0]),
            "reverse":lambda a: list(reversed(a[0])),
            "getRow": lambda a: a[0].data[a[1]],
            "getCol": lambda a: [r[a[1]] for r in a[0].data],
            "py":     lambda a: eval(a[0], globals(), sym),
            "appendRow":   lambda a: a[0].append_row(a[1]),
            "updateCell":  lambda a: a[0].update_cell(a[1], a[2], a[3]),
            "cols":        lambda a: Table(rows=a[0].rows, cols=len(a[1]), headers=a[1],
                                           data=[[row[a[0].headers.index(c)] for c in a[1]]
                                                 for row in a[0].data]),
            "sumTable":    lambda a: a[0].sum_table(),
            "sumRows":     lambda a: a[0].sum_rows(),
            "sumCols":     lambda a: a[0].sum_cols(),
            "avgTable":    lambda a: a[0].avg_table(),
            "avgRows":     lambda a: a[0].avg_rows(),
            "avgCols":     lambda a: a[0].avg_cols(),
            "varTable":    lambda a: a[0].var_table(),
            "stdevTable":  lambda a: a[0].stdev_table(),
            "varRows":     lambda a: a[0].var_rows(),
            "stdevRows":   lambda a: a[0].stdev_rows(),
            "varCols":     lambda a: a[0].var_cols(),
            "stdevCols":   lambda a: a[0].stdev_cols(),
            "minTable":    lambda a: a[0].min_table(),
            "maxTable":    lambda a: a[0].max_table(),
            "minRows":     lambda a: a[0].min_rows(),
            "maxRows":     lambda a: a[0].max_rows(),
            "minCols":     lambda a: a[0].min_cols(),
            "maxCols":     lambda a: a[0].max_cols(),
            "plotHeatmap": lambda a: __import__('wizual_viz').wizual_viz.plot_table_heatmap(a[0]),
            "barChart":    lambda a: __import__('wizual_viz').wizual_viz.bar_chart(a[0], a[1], a[2] if len(a)>2 else None),
            "lineChart":   lambda a: __import__('wizual_viz').wizual_viz.line_chart(a[0], a[1], a[2] if len(a)>2 else None),
            "scatterPlot": lambda a: __import__('wizual_viz').wizual_viz.scatter_plot(a[0], a[1], a[2] if len(a)>2 else None),
            "histogram":   lambda a: __import__('wizual_viz').wizual_viz.histogram(a[0], a[1] if len(a)>1 else 10, a[2] if len(a)>2 else None),
            "plotTable":   lambda a: __import__('wizual_viz').wizual_viz.plot_table(a[0]) if isinstance(a[0], Table) else None,
            "readCSV":     lambda a: read_csv(a[0]),
            "lineChartTable": lambda a: __import__('wizual_viz').line_chart_table(a[0]) if isinstance(a[0], Table) else None,
        }
        if name == "print":
            for a in args_n:
                val = evaluate(a, sym)
                print(val)
            return None
        if name not in builtins:
            raise NameError(f"Unknown function '{name}'")
        return builtins[name](args)
    else:
        raise EvalError(f"Unknown AST node '{kind}'")

def run(input_code):
    ast = parser.parse(input_code)
    symtable = {}
    evaluate(ast, symtable)
    return symtable
