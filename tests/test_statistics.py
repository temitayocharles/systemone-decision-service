from decide.statistics import percentile_nearest_rank


def test_percentile_nearest_rank():
    assert percentile_nearest_rank([1, 2, 3, 4, 5], 0.95) == 5.0
    assert percentile_nearest_rank([10, 20, 30, 40], 0.50) == 20.0
