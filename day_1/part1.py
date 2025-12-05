# So, first we need to understand the lock sequence. 
# The lock is circular lock the starts from pointing at 50. and can be rotated left or right.
# The lock has numbers from 0 to 99.
# When we turn the lock to right the number goes up and when we turn it to left the number goes down.
# If we go past 99 it wraps around to 0 and if we go past 0 it wraps around to 99.
# We will be given a list containing stuff like L10, R21 etc.
# We need to find how many times we point to 0 while following the instructions.

with open("input.txt", "r") as f:
    lines = [line.strip() for line in f]

def count_zeros(instructions):
    position = 50
    zero_count = 0

    for instruction in instructions:
        direction = instruction[0]
        steps = int(instruction[1:])

        if direction == 'R':
            position = (position + steps) % 100
        elif direction == 'L':
            position = (position - steps) % 100

        if position == 0:
            zero_count += 1

    return zero_count

result = count_zeros(lines)
print(result)
