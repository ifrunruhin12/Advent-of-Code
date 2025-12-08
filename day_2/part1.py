# So, we will be given a range like (11-22, 99-200 etc) in the input file.
# Each number represents an ID. we have to find the invalid IDs in the range and print the sum of those invalid IDs.
# An ID would be invalid if it has repeative digits as if someone forgot to put a comma in between 
# Like 11 is an invalid ID because it has repetitive digit 1. also, 2424 is an invalid ID, so is 99, 2222, 1919, 3434, 1010. but 111, 212, 999 are valid IDs.
# It's clear that the IDs who has even number of digits are invalid if they have repetitive digits.
# It's not possible to have a invalid ID with odd number of digits.
# So, let's implement the function to find the sum of invalid IDs in the given range.

def sum_of_invalid_ids(range_str):
    start, end = map(int, range_str.split('-'))
    invalid_sum = 0

    for id_num in range(start, end + 1):
        id_str = str(id_num)
        length = len(id_str)

        if length % 2 == 0:
            half = length // 2
            if id_str[:half] == id_str[half:]:
                invalid_sum += id_num

    return invalid_sum


def process_file(filename):
    with open(filename, "r") as f:
        content = f.read().strip()

    ranges = [r for r in content.split(",") if r]

    total = sum(sum_of_invalid_ids(r) for r in ranges)
    return total


print(process_file("input.txt"))

