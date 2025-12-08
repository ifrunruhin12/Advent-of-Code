def is_invalid_id(id_str):
    doubled = (id_str + id_str)[1:-1]
    return id_str in doubled


def sum_of_invalid_ids(range_str):
    start, end = map(int, range_str.split('-'))
    total = 0

    for id_num in range(start, end + 1):
        if is_invalid_id(str(id_num)):
            total += id_num

    return total


def process_file(filename):
    with open(filename, "r") as f:
        content = f.read().strip()

    ranges = [r for r in content.split(",") if r]
    return sum(sum_of_invalid_ids(r) for r in ranges)


print(process_file("input.txt"))

