def task3(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    # 1) Кількість стовпців із принаймні одним 0
    count_zero_cols = 0
    for col in range(cols):
        for row in range(rows):
            if matrix[row][col] == 0:
                count_zero_cols += 1
                break

    # 2) Знаходження номера рядка з найдовшою серією однакових елементів
    max_series_length = 0
    max_series_row = -1

    for i, row in enumerate(matrix):
        current_length = 1
        max_length_in_row = 1
        for j in range(1, len(row)):
            if row[j] == row[j-1]:
                current_length += 1
                max_length_in_row = max(max_length_in_row, current_length)
            else:
                current_length = 1

        if max_length_in_row > max_series_length:
            max_series_length = max_length_in_row
            max_series_row = i

    return count_zero_cols, max_series_row
