def write_data(data: list, output: str = 'stock_data.csv'):
    data = [",".join(row) for row in data]
    rows = [f"{row}\n" for row in data]
    with open(output, "w", encoding="utf-8") as csv_file:
        csv_file.writelines(rows)
