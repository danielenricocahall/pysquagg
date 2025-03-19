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
    assert pysquagg.blocks == [[1, 2], [3, 4], [5]]


@pytest.mark.parametrize("parallel", [True, False])
def test_insert_no_change_to_block_size(parallel):
    pysquagg = PySquagg([1, 2, 3, 5, 6, 7], aggregator_function=sum, parallel=parallel)
    assert pysquagg.aggregated_values == [3, 8, 13]
    pysquagg.insert(3, 4)
    assert pysquagg.block_size == 2
    assert pysquagg.blocks == [[1, 2], [3, 4], [5, 6], [7]]
    assert pysquagg.aggregated_values == [3, 7, 11, 7]


@pytest.mark.parametrize("parallel", [True, False])
def test_insert_block_size_changes(parallel):
    pysquagg = PySquagg(
        [1, 2, 3, 5, 6, 7, 8, 9], aggregator_function=sum, parallel=parallel
    )
    orig_blocks = pysquagg.blocks
    pysquagg.insert(3, 4)
    assert pysquagg.block_size == 3
    assert orig_blocks != pysquagg.blocks
    assert pysquagg.blocks == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert pysquagg.aggregated_values == [6, 15, 24]


def test_reverse():
    pysquagg = PySquagg([1, 2, 3, 4, 5, 6], aggregator_function=sum)
    assert pysquagg.aggregated_values == [3, 7, 11]
    pysquagg.reverse()
    assert pysquagg.blocks == [[6, 5], [4, 3], [2, 1]]
    assert pysquagg.aggregated_values == [11, 7, 3]


def test_concat_finish_last_block():
    pysquagg = PySquagg([1, 2, 3, 4, 5], aggregator_function=sum)
    assert pysquagg.aggregated_values == [3, 7, 5]
    pysquagg += [6]
    assert pysquagg.aggregated_values == [3, 7, 11]


@pytest.mark.parametrize("parallel", [True, False])
def test_concat_add_new_blocks(parallel):
    pysquagg = PySquagg([1, 2, 3, 4], aggregator_function=sum, parallel=parallel)
    assert pysquagg.aggregated_values == [3, 7]
    pysquagg += [5, 6, 7, 8]
    assert pysquagg.aggregated_values == [3, 7, 11, 15]


@pytest.mark.parametrize("parallel", [True, False])
def test_blocks_and_agg_concat_finish_last_block_and_add_new_blocks(parallel):
    pysquagg = PySquagg(list(range(10)), aggregator_function=sum, parallel=parallel)
    pysquagg += [10, 11, 12, 13, 14]
    assert pysquagg.aggregated_values == [3, 12, 21, 30, 39]


def test_pop_last_value():
    pysquagg = PySquagg([1, 2, 3, 4, 5], aggregator_function=sum)
    assert pysquagg.aggregated_values == [3, 7, 5]
    val = pysquagg.pop()
    assert val == 5
    assert pysquagg.aggregated_values == [3, 7]


@pytest.mark.parametrize("parallel", [True, False])
def test_pop_value(parallel):
    pysquagg = PySquagg([1, 2, 3, 4, 5], aggregator_function=sum, parallel=parallel)
    assert pysquagg.aggregated_values == [3, 7, 5]
    val = pysquagg.pop(2)
    assert val == 3
    assert pysquagg.blocks == [[1, 2], [4, 5]]
    assert pysquagg.aggregated_values == [3, 9]


@pytest.mark.parametrize("parallel", [True, False])
def test_pop_change_block_size(parallel):
    pysquagg = PySquagg(
        [1, 2, 3, 4, 5, 6, 7, 8, 9], aggregator_function=sum, parallel=parallel
    )
    assert pysquagg.aggregated_values == [6, 15, 24]
    val = pysquagg.pop(2)
    assert val == 3
    assert pysquagg.blocks == [[1, 2], [4, 5], [6, 7], [8, 9]]
    assert pysquagg.aggregated_values == [3, 9, 13, 17]


def test_remove():
    pysquagg = PySquagg([1, 2, 3, 4, 5], aggregator_function=sum)
    assert pysquagg.aggregated_values == [3, 7, 5]
    pysquagg.remove(3)
    assert pysquagg.blocks == [[1, 2], [4, 5]]
    assert pysquagg.aggregated_values == [3, 9]


def test_remove_element_not_present():
    pysquagg = PySquagg([1, 2, 3, 4, 5], aggregator_function=sum)
    with pytest.raises(ValueError):
        pysquagg.remove(6)


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


@pytest.mark.parametrize("left,right", [(0, 0), (1, 0), (0, 10), (-1, 5)])
def test_compute_blocks_invalid_range(left, right):
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    with pytest.raises(InvalidRangeException):
        pysquagg.query(left, right)


@pytest.mark.parametrize("parallel", [True, False])
def test_sort(parallel):
    pysquagg = PySquagg(
        [0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum, parallel=parallel
    )
    assert pysquagg.blocks == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, 12, 21]
    pysquagg.sort(reverse=True)
    assert pysquagg.blocks == [[8, 7, 6], [5, 4, 3], [2, 1, 0]]
    assert pysquagg.aggregated_values == [21, 12, 3]


def test_set_item():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.blocks == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, 12, 21]
    pysquagg[3] = -1
    assert pysquagg.blocks == [[0, 1, 2], [-1, 4, 5], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, 8, 21]


def test_set_range_same_block():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.blocks == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, 12, 21]
    pysquagg[3:6] = [-1, -2, -3]
    assert pysquagg.blocks == [[0, 1, 2], [-1, -2, -3], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, -6, 21]


def test_set_range_across_blocks():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.blocks == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, 12, 21]
    pysquagg[2:7] = [-1, -2, -3, -4, -5]
    assert pysquagg.blocks == [[0, 1, -1], [-2, -3, -4], [-5, 7, 8]]
    assert pysquagg.aggregated_values == [0, -9, 10]


def test_set_range_extra_values():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.blocks == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, 12, 21]
    pysquagg[3:6] = [-1, -2, -3, -4]
    assert pysquagg.blocks == [[0, 1, 2], [-1, -2, -3], [-4, 6, 7], [8]]
    assert pysquagg.aggregated_values == [3, -6, 9, 8]


def test_set_range_fewer_values():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert pysquagg.blocks == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    assert pysquagg.aggregated_values == [3, 12, 21]
    pysquagg[3:6] = [-1]
    assert pysquagg.blocks == [[0, 1], [2, -1], [6, 7], [8]]
    assert pysquagg.aggregated_values == [1, 1, 13, 8]


def test_clear():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    pysquagg.clear()
    assert pysquagg.blocks == []
    assert pysquagg.aggregated_values == []


def test_empty_list():
    pysquagg = PySquagg([], aggregator_function=sum)
    assert pysquagg.blocks == []
    assert pysquagg.aggregated_values == []


def test_iter():
    pysquagg = PySquagg([0, 1, 2, 3, 4, 5, 6, 7, 8], aggregator_function=sum)
    assert list(iter(pysquagg)) == [([0, 1, 2], 3), ([3, 4, 5], 12), ([6, 7, 8], 21)]
