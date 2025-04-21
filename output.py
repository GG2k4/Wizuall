import math
import csv

def read_csv(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return Table(rows=0, cols=0)
    headers = rows[0]
    data = []
    for row in rows[1:]:
        clean = []
        for cell in row:
            try:
                clean.append(float(cell) if '.' in cell else int(cell))
            except Exception:
                clean.append(cell)
        data.append(clean)
    return Table(rows=len(data), cols=len(headers), headers=headers, data=data)

class Table:
    def __init__(self, rows: int, cols: int, headers=None, data=None):
        self.rows = rows
        self.cols = cols
        if headers is None:
            self.headers = [str(i) for i in range(cols)]
        else:
            self.headers = headers
        if data:
            self.data = data
        else:
            self.data = [[0.0 for _ in range(cols)] for _ in range(rows)]

    def append_row(self, values: list):
        if len(values) != self.cols:
            raise ValueError(f"Cannot append row: expected {self.cols} values, got {len(values)}")
        self.data.append(values)
        self.rows += 1
        return self

    def update_cell(self, row: int, col: int, value):
        if not (0 <= row < self.rows) or not (0 <= col < self.cols):
            raise IndexError(f"Cannot update cell: row {row} or col {col} out of range")
        self.data[row][col] = value
        return self

    def _check_shape(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError(f"Shape mismatch: {self.rows}x{self.cols} vs {other.rows}x{other.cols}")

    def __add__(self, other):
        if isinstance(other, Table):
            self._check_shape(other)
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] + other.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] + other for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Table):
            self._check_shape(other)
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] - other.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] - other for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[other - self.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Table):
            self._check_shape(other)
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] * other.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] * other for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, Table):
            self._check_shape(other)
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] / other.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] / other for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[other / self.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Table):
            self._check_shape(other)
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] % other.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[self.data[i][j] % other for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    def __rmod__(self, other):
        if isinstance(other, (int, float)):
            t = Table(self.rows, self.cols, self.headers)
            t.data = [[other % self.data[i][j] for j in range(self.cols)]
                      for i in range(self.rows)]
            return t
        return NotImplemented

    def __matmul__(self, other):
        if not isinstance(other, Table):
            return NotImplemented
        if self.cols != other.rows:
            raise ValueError(f"Cannot matrix-multiply {self.rows}x{self.cols} by {other.rows}x{other.cols}")
        t = Table(self.rows, other.cols, other.headers)
        for i in range(self.rows):
            for j in range(other.cols):
                acc = 0.0
                for k in range(self.cols):
                    acc += self.data[i][k] * other.data[k][j]
                t.data[i][j] = acc
        return t

    def flatten(self):
        return [cell for row in self.data for cell in row]

    def sum_table(self):
        return sum(self.flatten())

    def sum_rows(self):
        return [sum(r) for r in self.data]

    def sum_cols(self):
        return [sum(self.data[r][c] for r in range(self.rows)) for c in range(self.cols)]

    def avg_table(self):
        flat = self.flatten()
        return sum(flat) / len(flat) if flat else None

    def avg_rows(self):
        return [sum(r) / len(r) if r else None for r in self.data]

    def avg_cols(self):
        return [
            sum(self.data[r][c] for r in range(self.rows)) / self.rows
            if self.rows else None
            for c in range(self.cols)
        ]

    def var_table(self, population=True):
        flat = self.flatten()
        μ = sum(flat) / len(flat)
        dd = [(x - μ) ** 2 for x in flat]
        n = len(dd) if population else len(dd) - 1
        return sum(dd) / n if n > 0 else None

    def stdev_table(self, population=True):
        return math.sqrt(self.var_table(population))

    def var_rows(self, population=True):
        out = []
        for r in self.data:
            μ = sum(r) / len(r)
            dd = [(x - μ) ** 2 for x in r]
            n = len(dd) if population else len(dd) - 1
            out.append(sum(dd) / n if n > 0 else None)
        return out

    def stdev_rows(self, population=True):
        return [math.sqrt(v) if v is not None else None for v in self.var_rows(population)]

    def var_cols(self, population=True):
        out = []
        for c in range(self.cols):
            col = [self.data[r][c] for r in range(self.rows)]
            μ = sum(col) / len(col)
            dd = [(x - μ) ** 2 for x in col]
            n = len(dd) if population else len(dd) - 1
            out.append(sum(dd) / n if n > 0 else None)
        return out

    def stdev_cols(self, population=True):
        return [math.sqrt(v) if v is not None else None for v in self.var_cols(population)]

    def min_table(self):
        flat = self.flatten()
        return min(flat) if flat else None

    def max_table(self):
        flat = self.flatten()
        return max(flat) if flat else None

    def min_rows(self):
        return [min(r) if r else None for r in self.data]

    def max_rows(self):
        return [max(r) if r else None for r in self.data]

    def min_cols(self):
        return [min(self.data[r][c] for r in range(self.rows)) for c in range(self.cols)]

    def max_cols(self):
        return [max(self.data[r][c] for r in range(self.rows)) for c in range(self.cols)]
    
    def __str__(self):
        # compute column-widths
        widths = []
        for i, h in enumerate(self.headers):
            w = len(str(h))
            for row in self.data:
                w = max(w, len(str(row[i])))
            widths.append(w)
        # header line
        header = ' | '.join(str(h).ljust(widths[i]) for i, h in enumerate(self.headers))
        sep    = '-+-'.join('-' * widths[i] for i in range(len(self.headers)))
        # data lines
        rows = []
        for row in self.data:
            rows.append(' | '.join(str(row[i]).ljust(widths[i]) for i in range(len(self.headers))))
        return '\n'.join([header, sep] + rows)

    __repr__ = __str__

import matplotlib.pyplot as plt

def plot_table_heatmap(table):
    data = table.data
    fig, ax = plt.subplots()
    cax = ax.imshow(data, aspect='auto', interpolation='nearest')
    ax.set_xticks(range(table.cols))
    ax.set_xticklabels(table.headers)
    ax.set_yticks(range(table.rows))
    ax.set_yticklabels(range(table.rows))
    plt.colorbar(cax, ax=ax)
    plt.title("Table heatmap")
    plt.show()

def bar_chart(labels, values, title=None):
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    if title: ax.set_title(title)
    plt.show()

def line_chart(x, y, title=None):
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o')
    if title: ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    plt.show()

def scatter_plot(x, y, title=None):
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    if title: ax.set_title(title)
    plt.show()

def histogram(data, bins=10, title=None):
    fig, ax = plt.subplots()
    ax.hist(data, bins=bins)
    if title: ax.set_title(title)
    plt.show()

def plot_table(table_val):
    fig, ax = plt.subplots()
    ax.axis('off')
    tbl = ax.table(cellText=table_val.data, colLabels=table_val.headers, loc="center")
    tbl.auto_set_font_size(False)
    tbl.scale(1, 1.5)
    plt.title("Table View")
    plt.show()

def line_chart_table(table):
    labels = [str(h) for h in table.headers]
    x = list(range(len(labels)))
    fig, ax = plt.subplots()
    for idx, row in enumerate(table.data, start=1):
        ax.plot(x, row, marker='o', label=f"Series {idx}")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_xlabel("Header")
    ax.set_ylabel("Value")
    plt.title("All Series")
    ax.legend()
    plt.tight_layout()
    plt.show()

def main():
    x=5
    y=3.2
    z=[1, 2, 3]
    a=[2.3, 3.14, 2.71]
    b=[2, 3, 4, 5]
    c=Table(rows=0,cols=3)
    c.append_row([1, 2, 3])
    c.append_row([4, 3, 2])
    c.append_row([5, 6, 7])
    print(((x+y) if not isinstance(x, list) and not isinstance(y, list) else ([a+b for a,b in zip(x,y)] if isinstance(x, list) and isinstance(y, list) else ([elem+y for elem in x] if isinstance(x, list) else ([x+elem for elem in y])))))
    print(((y+z) if not isinstance(y, list) and not isinstance(z, list) else ([a+b for a,b in zip(y,z)] if isinstance(y, list) and isinstance(z, list) else ([elem+z for elem in y] if isinstance(y, list) else ([y+elem for elem in z])))))
    print(((z+y) if not isinstance(z, list) and not isinstance(y, list) else ([a+b for a,b in zip(z,y)] if isinstance(z, list) and isinstance(y, list) else ([elem+y for elem in z] if isinstance(z, list) else ([z+elem for elem in y])))))
    print(((z+a) if not isinstance(z, list) and not isinstance(a, list) else ([a+b for a,b in zip(z,a)] if isinstance(z, list) and isinstance(a, list) else ([elem+a for elem in z] if isinstance(z, list) else ([z+elem for elem in a])))))
    print(((a+b) if not isinstance(a, list) and not isinstance(b, list) else ([a+b for a,b in zip(a,b)] if isinstance(a, list) and isinstance(b, list) else ([elem+b for elem in a] if isinstance(a, list) else ([a+elem for elem in b])))))
    print(((b+c) if not isinstance(b, list) and not isinstance(c, list) else ([a+b for a,b in zip(b,c)] if isinstance(b, list) and isinstance(c, list) else ([elem+c for elem in b] if isinstance(b, list) else ([b+elem for elem in c])))))
    d=[c, a]
    print(sum(d))

if __name__=="__main__":
    main()