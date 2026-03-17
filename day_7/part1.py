from collections import deque

def count_splits(grid):
    R = len(grid)
    C = len(grid[0])

    # find S
    start_row = start_col = -1
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 'S':
                start_row, start_col = r, c
                break
        if start_row != -1:
            break

    q = deque()
    q.append((start_row + 1, start_col))

    visited = set()
    used_splitters = set()
    splits = 0

    while q:
        r, c = q.popleft()

        if (r, c) in visited:
            continue
        visited.add((r, c))

        while r < R and 0 <= c < C:
            if grid[r][c] == '^':
                if (r, c) not in used_splitters:
                    splits += 1
                    used_splitters.add((r, c))

                # spawn beams
                if c - 1 >= 0:
                    q.append((r, c - 1))
                if c + 1 < C:
                    q.append((r, c + 1))
                break

            r += 1

    return splits



def read_input(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == "__main__":
    grid = read_input("input.txt")
    result = count_splits(grid)
    print(result)
