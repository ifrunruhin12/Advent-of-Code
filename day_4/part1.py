def solve(grid_str: str) -> int:
    lines = grid_str.strip().splitlines()
    rows, cols = len(lines), len(lines[0])

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),          (0, 1),
        (1, -1),  (1, 0), (1, 1)
    ]

    accessible = 0

    for r in range(rows):
        for c in range(cols):
            if lines[r][c] != '@':
                continue

            cnt = 0
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if lines[nr][nc] == '@':
                        cnt += 1

            if cnt < 4:
                accessible += 1

    return accessible

# Read input from file and solve
with open("input.txt", "r") as f:
    grid_input = f.read()

print(solve(grid_input))

