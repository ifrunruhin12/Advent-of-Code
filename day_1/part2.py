# Okay so this time we are counting how many times we will be crossing 0 while following the instructions.
# So if we are at 95 and we turn right 10 steps we will cross 0 once.
# Similarly if we are at 5 and we turn left 10 steps we will also cross 0 once.
# We need to account for multiple crossings as well. For example if we are at 95 and we turn right 110 steps we will cross 0 twice.
# Be careful: if the dial were pointing at 50, a single rotation like R1000 would cause the dial to point at 0 ten times before returning back to 50!


with open("input.txt", "r") as f:
    lines = [line.strip() for line in f]

def count_zero_crossings(instructions):
    position = 50
    zero_crossings = 0

    for instr in instructions:
        direction = instr[0]
        steps = int(instr[1:])

        loops, steps = divmod(steps, 100)
        zero_crossings += loops

        if direction == 'R':
            if position >= 100 - steps:
                zero_crossings += 1
            position = (position + steps) % 100
        else:
            if position <= steps and position != 0:
                zero_crossings += 1
            position = (position - steps) % 100

    return zero_crossings

result = count_zero_crossings(lines)
print(result)

