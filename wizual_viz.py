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