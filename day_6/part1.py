def is_all_spaces_column(lines, col):
    for line in lines:
        if col < len(line) and line[col] != ' ':
            return False
    return True


def solve_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    if not lines:
        return 0

    height = len(lines)
    width = max(len(line) for line in lines)

    total = 0
    col = 0

    while col < width:
        if is_all_spaces_column(lines, col):
            col += 1
            continue

        start = col
        while col < width and not is_all_spaces_column(lines, col):
            col += 1
        end = col

        op = lines[-1][start:end].strip()

        nums = []
        for r in range(height - 1):
            chunk = lines[r][start:end].strip()
            if chunk:
                nums.append(int(chunk))

        result = nums[0]
        for n in nums[1:]:
            if op == '+':
                result += n
            else:
                result *= n

        total += result

    return total


if __name__ == "__main__":
    print(solve_from_file("input.txt"))

