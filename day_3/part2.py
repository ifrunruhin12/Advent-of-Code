def max_joltage(s, keep=12):
    remove = len(s) - keep
    stack = []

    for ch in s:
        while stack and remove > 0 and stack[-1] < ch:
            stack.pop()
            remove -= 1
        stack.append(ch)

    return int("".join(stack[:keep]))

total = 0

with open("input.txt") as f:
    for line in f:
        s = line.strip()
        total += max_joltage(s)

print(total)

