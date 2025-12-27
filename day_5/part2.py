# For this second part, we only care about the first part of the input which 
# are the list of range of numbers each separated by a hyphen. 
# For example
# Input:
# 5-10
# 15-20
# 25-30
# 35-40

# So, we have find how many number fall within all the ranges.
# In this case, the ranges are:
# 5,6,7,8,9,10
# 15,16,17,18,19,20
# 25,26,27,28,29,30
# 35,36,37,38,39,40
# So the total count of numbers that fall within all the ranges is 24.
# Make sure there is no double counting of numbers that fall within overlapping ranges.

def count_numbers_in_ranges(ranges):
    intervals = sorted(tuple(map(int, r.split('-'))) for r in ranges)

    total = 0
    s, e = intervals[0]

    for ns, ne in intervals[1:]:
        if ns <= e + 1:
            e = max(e, ne)
        else:
            total += e - s + 1
            s, e = ns, ne

    return total + (e - s + 1)

with open("input.txt", "r") as f:
    content = f.read().strip()

parts = content.split("\n\n")

ranges = parts[0].splitlines()

print(count_numbers_in_ranges(ranges))
