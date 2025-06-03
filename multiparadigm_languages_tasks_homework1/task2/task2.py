def task2(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    # 1) Кількість стовпців без нулів
    count_no_zero_cols = 0
    for col in range(cols):
        has_zero = False
        for row in range(rows):
            if matrix[row][col] == 0:
                has_zero = True
                break
        if not has_zero:
            count_no_zero_cols += 1

    # 2) Обчислення характеристики рядка
    def row_characteristic(row):
        return sum(x for x in row if x > 0 and x % 2 == 0)

    # 3) Сортування рядків за характеристикою
    sorted_matrix = sorted(matrix, key=row_characteristic)

    return count_no_zero_cols, sorted_matrix
