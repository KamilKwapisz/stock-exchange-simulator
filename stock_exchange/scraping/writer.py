def write_data(data: list, output: str = 'stock_data.csv', join_data: bool = True, separator: str = ','):
    output = f"../{output}"
    if join_data:
        data = [separator.join(row) for row in data]
        rows = [f"{row}\n" for row in data]
    else:
        rows = data
    with open(output, "w", encoding="utf-8") as csv_file:
        csv_file.writelines(rows)
