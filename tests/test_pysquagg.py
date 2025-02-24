from pysquagg.pysquagg import PySquagg


def test_basic_pysquagg():
    pysquagg = PySquagg([1, 2, 3, 4])
    assert pysquagg.block_size == 2
    assert pysquagg.blocks == [[1, 2], [3, 4]]


def test_append():
    pysquagg = PySquagg([1, 2, 3, 4])
    pysquagg.append(5)
    assert pysquagg.block_size == 2
    assert pysquagg.blocks == [[1, 2], [3, 4, 5]]


def test_insert_no_change_to_block_size():
    pysquagg = PySquagg([1, 2, 3, 5, 6, 7])
    pysquagg.insert(3, 4)
    assert pysquagg.block_size == 2
    assert pysquagg.blocks == [[1, 2], [3, 4, 5], [6, 7]]


def test_insert_block_size_changes():
    pysquagg = PySquagg([1, 2, 3, 5, 6, 7, 8, 9])
    orig_blocks = pysquagg.blocks
    pysquagg.insert(3, 4)
    assert pysquagg.block_size == 3
    assert orig_blocks != pysquagg.blocks
    assert pysquagg.blocks == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def test_reverse():
    pysquagg = PySquagg([1, 2, 3, 4, 5, 6])
    pysquagg.reverse()
    assert pysquagg == [6, 5, 4, 3, 2, 1]
    assert pysquagg.blocks == [[6, 5], [4, 3], [2, 1]]
