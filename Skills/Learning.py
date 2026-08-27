def update_matrix(matrix, winning_team, losing_team, lr=0.1):
    """Simple feedback loop: boost pairs that won together"""
    for i in range(len(winning_team)):
        for j in range(i+1, len(winning_team)):
            a, b = winning_team[i].id, winning_team[j].id
            matrix[a][b] = matrix.get(a, {}).get(b, 0.5) + lr
