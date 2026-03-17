def count_timelines(grid):
    R = len(grid)
    C = len(grid[0])
    
    memo = {}
    
    def dfs(r, c):
        # out of bounds
        if c < 0 or c >= C:
            return 0
        # reached bottom → 1 timeline
        if r == R:
            return 1
        
        if (r, c) in memo:
            return memo[(r, c)]
        
        cell = grid[r][c]
        
        if cell == '.':
            res = dfs(r + 1, c)
        elif cell == '^':
            res = 0
            # left split
            res += dfs(r, c - 1) if c - 1 >= 0 else 0
            # right split
            res += dfs(r, c + 1) if c + 1 < C else 0
        else:
            # S or any other character → move down
            res = dfs(r + 1, c)
        
        memo[(r, c)] = res
        return res
    
    # find S
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 'S':
                start_row, start_col = r, c
                break
    
    # start one step below S
    return dfs(start_row + 1, start_col)

def read_input(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == "__main__":
    grid = read_input("input.txt")
    result = count_timelines(grid)
    print(result)

