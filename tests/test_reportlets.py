from PipelineQC import reportlets


def test_calc_nrow_ncol():
    assert reportlets._calc_nrows_ncols(7) == (3, 7)
    assert reportlets._calc_nrows_ncols(8) == (3, 8)
    assert reportlets._calc_nrows_ncols(9) == (6, 8)


def test_get_row_cal():
    for i in range(3):
        for j in range(7):
            assert reportlets._get_row_col(i, j, 7) == (i, j)
    for i in range(3):
        for j in range(8):
            assert reportlets._get_row_col(i, j, 12) == (i * 2, j)
        for j in range(8, 12):
            assert reportlets._get_row_col(i, j, 12) == (i * 2 + 1, j - 8)
