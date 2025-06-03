def task1(matrix):
    # 1) Кількість рядків без нулів
    count_no_zero_rows = 0
    for row in matrix:
        if 0 not in row:
            count_no_zero_rows += 1

    # 2) Максимальне число, що зустрічається більше одного разу
    elements = []
    for row in matrix:
        elements.extend(row)

    counts = {}
    for num in elements:
        counts[num] = counts.get(num, 0) + 1

    max_repeated = None
    for num, cnt in counts.items():
        if cnt > 1:
            if max_repeated is None or num > max_repeated:
                max_repeated = num

    return count_no_zero_rows, max_repeated
