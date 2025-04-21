import os

class CodegenError(Exception):
    pass

def emit_expression(node):
    kind = node[0]
    if kind == 'number':
        return repr(node[1])
    if kind == 'string':
        return repr(node[1])
    if kind == 'var':
        return node[1]
    if kind == 'list':
        elems = ', '.join(emit_expression(e) for e in node[1])
        return f'[{elems}]'
    if kind == 'binop':
        op = node[1]
        left_node, right_node = node[2], node[3]
        L = emit_expression(left_node)
        R = emit_expression(right_node)
        if op in ('+', '-', '*', '/', '%'):
            return (
                f'(({L}{op}{R}) if not isinstance({L}, list) and not isinstance({R}, list) '
                f'else ([a{op}b for a,b in zip({L},{R})] if isinstance({L}, list) and isinstance({R}, list) '
                f'else ([elem{op}{R} for elem in {L}] if isinstance({L}, list) '
                f'else ([{L}{op}elem for elem in {R}]))))') 
        return f'({L}{op}{R})'
    if kind == 'slice':
        base = emit_expression(node[1])
        sl = node[2]
        if sl[0] == 'index':
            return (
                f'({base}.data[{sl[1]}] if isinstance({base}, Table) '
                f'else {base}[{sl[1]}])'
            )
        if sl[0] == 'range':
            start, end = sl[1], sl[2]
            return (
                f'(Table(rows=len({base}.data[{start}:{end}]), cols={base}.cols, '
                f'headers={base}.headers, data={base}.data[{start}:{end}]) '
                f'if isinstance({base}, Table) '
                f'else {base}[{start}:{end}])'
            )
        raise CodegenError(f'Unknown slice type: {sl[0]}')
    if kind == 'bool':
        op = node[1]
        left = emit_expression(node[2])
        right= emit_expression(node[3])
        return f'({left}{op}{right})'
    if kind == 'call':
        name = node[1]
        args = node[2]
        if name == 'readCSV':
            if len(args) != 1:
                raise CodegenError(f"Function 'readCSV' expects 1 argument, got {len(args)}")
            return f"read_csv({emit_expression(args[0])})"
        if name == 'plotTable':
            if len(args) != 1:
                raise CodegenError(f"Function 'plotTable' expects 1 argument, got {len(args)}")
            return f"plot_table({emit_expression(args[0])})"
        if name in ('sum','avg','min','max','sort','reverse'):
            if len(args) != 1:
                raise CodegenError(f"Function '{name}' expects 1 argument, got {len(args)}")
            expr = emit_expression(args[0])
            if name == 'sum':     return f"sum({expr})"
            if name == 'avg':     return f"(sum({expr})/len({expr}))"
            if name == 'min':     return f"min({expr})"
            if name == 'max':     return f"max({expr})"
            if name == 'sort':    return f"sorted({expr})"
            if name == 'reverse': return f"list(reversed({expr}))"
        if name == 'appendRow':
            if len(args) != 2:
                raise CodegenError(f"Function 'appendRow' expects 2 arguments, got {len(args)}")
            tab  = emit_expression(args[0])
            vals = emit_expression(args[1])
            return f"{tab}.append_row({vals})"
        if name == 'updateCell':
            if len(args) != 4:
                raise CodegenError(f"Function 'updateCell' expects 4 arguments, got {len(args)}")
            tab = emit_expression(args[0])
            r   = emit_expression(args[1])
            c   = emit_expression(args[2])
            v   = emit_expression(args[3])
            return f"{tab}.update_cell({r},{c},{v})"
        if name == 'getRow':
            if len(args) != 2:
                raise CodegenError(f"Function 'getRow' expects 2 arguments, got {len(args)}")
            return f"{emit_expression(args[0])}.data[{emit_expression(args[1])}]"
        if name == 'getCol':
            if len(args) != 2:
                raise CodegenError(f"Function 'getCol' expects 2 arguments, got {len(args)}")
            tbl = emit_expression(args[0])
            idx = emit_expression(args[1])
            return f"[row[{idx}] for row in {tbl}.data]"
        if name == 'py':
            if len(args) != 1:
                raise CodegenError(f"Function 'py' expects 1 argument, got {len(args)}")
            return f"eval({emit_expression(args[0])})"
        if name == 'cols':
            if len(args) != 2:
                raise CodegenError(f"Function 'cols' expects 2 arguments, got {len(args)}")
            tbl = emit_expression(args[0])
            hdr = emit_expression(args[1])
            return (
                f"Table(rows={tbl}.rows, cols=len({hdr}), headers={hdr}, "
                f"data=[[row[{tbl}.headers.index(c)] for c in {hdr}] for row in {tbl}.data])"
            )
        if name in ('sumTable','sumRows','sumCols',
                    'avgTable','avgRows','avgCols',
                    'varTable','stdevTable',
                    'varRows','stdevRows',
                    'varCols','stdevCols',
                    'minTable','maxTable',
                    'minRows','maxRows',
                    'minCols','maxCols'):
            if len(args) != 1:
                raise CodegenError(f"Function '{name}' expects 1 argument, got {len(args)}")
            tbl = emit_expression(args[0])
            method = {
                'sumTable':   'sum_table',
                'sumRows':    'sum_rows',
                'sumCols':    'sum_cols',
                'avgTable':   'avg_table',
                'avgRows':    'avg_rows',
                'avgCols':    'avg_cols',
                'varTable':   'var_table',
                'stdevTable': 'stdev_table',
                'varRows':    'var_rows',
                'stdevRows':  'stdev_rows',
                'varCols':    'var_cols',
                'stdevCols':  'stdev_cols',
                'minTable':   'min_table',
                'maxTable':   'max_table',
                'minRows':    'min_rows',
                'maxRows':    'max_rows',
                'minCols':    'min_cols',
                'maxCols':    'max_cols'
            }[name]
            return f"{tbl}.{method}()"
        if name == 'plotHeatmap':
            if len(args) != 1:
                raise CodegenError(f"Function 'plotHeatmap' expects 1 argument, got {len(args)}")
            return f"plot_table_heatmap({emit_expression(args[0])})"
        if name in ('barChart','lineChart','scatterPlot'):
            expected = 2
            if name in ('barChart','lineChart','scatterPlot'):
                if len(args) < 2 or len(args) > 3:
                    raise CodegenError(f"Function '{name}' expects 2 or 3 arguments, got {len(args)}")
            fn = {
                'barChart':      'bar_chart',
                'lineChart':     'line_chart',
                'scatterPlot':   'scatter_plot'
            }[name]
            a0 = emit_expression(args[0])
            a1 = emit_expression(args[1])
            a2 = emit_expression(args[2]) if len(args) == 3 else None
            return f"{fn}({a0},{a1},{a2})"
        if name == 'histogram':
            if len(args) < 1 or len(args) > 3:
                raise CodegenError(f"Function 'histogram' expects 1 to 3 arguments, got {len(args)}")
            data = emit_expression(args[0])
            bins = emit_expression(args[1]) if len(args) > 1 else 10
            title= emit_expression(args[2]) if len(args) > 2 else None
            return f"histogram({data},{bins},{title})"
        if name == 'lineChartTable':
            if len(args) != 1:
                raise CodegenError(f"Function 'lineChartTable' expects 1 argument, got {len(args)}")
            return f"line_chart_table({emit_expression(args[0])})"
        call_args = ', '.join(emit_expression(a) for a in args)
        return f'{name}({call_args})'
    if kind == 'table':
        params = node[1]
        rn = params.get('rows', ('number', 0)); cn = params.get('cols', ('number', 0))
        Re = emit_expression(rn); Ce = emit_expression(cn)
        if 'headers' in params:
            H = emit_expression(params['headers'])
            return f'Table(rows={Re},cols={Ce},headers={H})'
        return f'Table(rows={Re},cols={Ce})'
    raise CodegenError(f'Cannot generate code for node: {kind}')(f'Unknown slice type: {sl[0]}')

def emit_statement(node, indent=''):
    kind = node[0]
    if kind == 'assign':
        n = node[1]
        e = emit_expression(node[2])
        return [f'{indent}{n}={e}']
    if kind == 'call':
        nm = node[1]
        args = node[2]
        if nm == 'print':
            if len(args) == 1 and args[0][0] == 'var':
                v = args[0][1]
                return [f"{indent}print('{v} =', {v}) if not isinstance({v}, Table) else print('{v} =', {v}, sep='\\n')"]
            ex = ', '.join(emit_expression(a) for a in args)
            return [f'{indent}print({ex})']
        return [f'{indent}{emit_expression(node)}']
    if kind == 'while':
        cond = emit_expression(node[1])
        L = [f'{indent}while {cond}:']
        L += emit_statement(node[2], indent + '    ')
        return L
    if kind == 'if':
        cond = emit_expression(node[1])
        lines = [f'{indent}if {cond}:']
        for stmt in node[2][1]:
            lines += emit_statement(stmt, indent + '    ')
        return lines
    if kind == 'block':
        out = []
        for s in node[1]:
            out += emit_statement(s, indent)
        return out
    raise CodegenError(f'Cannot generate code for statement: {kind}')

def generate_py(ast, out_path):
    if ast[0] != 'program':
        raise CodegenError('AST root is not program')
    base = os.path.dirname(__file__)
    hp = os.path.join(base, 'wizual_helper.py')
    vp = os.path.join(base, 'wizual_viz.py')
    with open(hp, 'r', encoding='utf-8', errors='replace') as f:
        helper_src = f.read().replace('\u2010', '-').splitlines()
    with open(vp, 'r', encoding='utf-8', errors='replace') as f:
        viz_src = f.read().replace('\u2010', '-').splitlines()
    lines = helper_src + [''] + viz_src + ['', 'def main():']
    for stmt in ast[1]:
        lines += emit_statement(stmt, '    ')
    lines += ['', 'if __name__=="__main__":', '    main()']
    dp = os.path.dirname(out_path)
    if dp:
        os.makedirs(dp, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))