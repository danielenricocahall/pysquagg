import pytest
from pysquagg.pysquagg import PySquagg, InvalidRangeException


def test_basic_pysquagg():
    pysquagg = PySquagg([1, 2, 3, 4], aggregator_function=lambda x: x)
    assert pysquagg.block_size == 2
    assert pysquagg.blocks == [[1, 2], [3, 4]]


def test_append():
    pysquagg = PySquagg([1, 2, 3, 4], aggregator_function=lambda x: x)
    pysquagg.append(5)
    assert pysquagg.block_size == 2
    assert pysquagg.blocks == [[1, 2], [3, 4, 5]]


def test_insert_no_change_to_block_size():
    pysquagg = PySquagg([1, 2, 3, 5, 6, 7], aggregator_function=lambda x: x)
    pysquagg.insert(3, 4)
    assert pysquagg.block_size == 2
    assert pysquagg.blocks == [[1, 2], [3, 4, 5], [6, 7]]


def test_insert_block_size_changes():
    pysquagg = PySquagg([1, 2, 3, 5, 6, 7, 8, 9], aggregator_function=lambda x: x)
    orig_blocks = pysquagg.blocks
    pysquagg.insert(3, 4)
    assert pysquagg.block_size == 3
    assert orig_blocks != pysquagg.blocks
    assert pysquagg.blocks == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def test_reverse():
    pysquagg = PySquagg([1, 2, 3, 4, 5, 6], aggregator_function=sum)
    assert pysquagg.aggregated_values == [3, 7, 11]
    pysquagg.reverse()
    assert pysquagg.blocks == [[6, 5], [4, 3], [2, 1]]
    assert pysquagg.aggregated_values == [11, 7, 3]


def test_aggregated_values_recomputed_on_concat():
    pysquagg = PySquagg([1, 2, 3, 4], aggregator_function=sum)
    assert pysquagg.aggregated_values == [3, 7]
    pysquagg += [5, 6]
    assert pysquagg.aggregated_values == [3, 18]


def test_compute_aggregate_whole_blocks():
    pysquagg = PySquagg([1, 2, 3, 4, 5, 6], aggregator_function=sum)
    assert pysquagg.query(0, 5) == 21


def test_compute_aggregate_partial_blocks_left():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.query(1, 5) == 15


def test_compute_aggregate_partial_blocks_right():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.query(3, 7) == 25


def test_compute_aggregate_partial_blocks_both_sides():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.query(1, 6) == 21


def test_compute_blocks_invalid_range():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    with pytest.raises(InvalidRangeException):
        pysquagg.query(1, 0)
