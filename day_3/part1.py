# So, I have a string like 818181911112111 
# I want to find the highest two digits number without changing the position of the digits.
# For example, in the string 818181911112111, the highest two digit number is 92.
# So, this is basically a sliding window problem where I need to find the highest two digits number in the string.
# Let's do it the most efficient way possible without using nested loops.

def highest_two_digit_number(s):
    max_right = -1
    best = -1

    for ch in reversed(s):
        d = int(ch)
        if max_right != -1:
            best = max(best, d * 10 + max_right)
        max_right = max(max_right, d)

    return best

total_sum = 0

with open("input.txt", "r") as f:
    for line in f:
        s = line.strip()
        total_sum += highest_two_digit_number(s)

print(total_sum)

