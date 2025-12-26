# So, for this problem in the input there will be two part separated by a new line
# The first part will be a list of range of numbers separated by a hyphen and second part will be a list of numbers
# The task is to find how many numbers from the second part fall within any of the ranges
# For example:
# Input:
# 1-5
# 10-15
# 20-25
# 
# 3
# 12
# 18
# 22
# Output:
# 3

def count_numbers_in_ranges(ranges, numbers):
    count = 0
    for number in numbers:
        for r in ranges:
            start, end = map(int, r.split('-'))
            if start <= number <= end:
                count += 1
                break
    return count

with open("input.txt", "r") as f:
    content = f.read().strip()

parts = content.split("\n\n")

ranges = parts[0].splitlines()
numbers = list(map(int, parts[1].splitlines()))

print(count_numbers_in_ranges(ranges, numbers))
