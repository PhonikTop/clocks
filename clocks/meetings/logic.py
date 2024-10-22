def get_average_score(votes):
    valid_votes = list(filter(None, votes.values()))
    average_score = (
        round(sum(map(int, valid_votes)) / len(valid_votes)) if valid_votes else 0
    )
    return average_score
