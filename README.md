# Overview
 This is `pysquagg`, a library containing a data structure intended for expediant computation of aggregations on a collection using Square Root Decomposition. The data structure is an extension of [Mo's Algorithm](https://www.geeksforgeeks.org/mos-algorithm-query-square-root-decomposition-set-1-introduction/).
 
# Motivation
The principles behind Mo's Algorithm is interesting and useful, but the implementation is a bit cumbersome. This library is intended to make it easier to use the algorithm in Python, plus introduce dynamic behavior, such that a collection can be modified after the data structure is created, and the corresponding blocks + aggregates are updated accordingly.


# API & Usage
The API for using `pysquagg` is simple, as we're only providing a single class `PySquagg`:
```python

from pysquagg.pysquagg import PySquagg

pysquagg_instance = PySquagg([1, 2, 3, 4, 5, 6], aggregator_function=sum)
pysquagg_instance.blocks # will print [[1, 2], [3, 4], [5]]
pysquagg_instance.aggregated_values # will print [3, 7, 5]
pysquagg_instance.query(0, 5) # will print 21
pysquagg_instance += [7, 8]
pysquagg_instance.blocks # will print [[1, 2], [3, 4], [5, 6], [7, 8]]
```
# Performance Characteristics

## Complexity

| Operation | Average Case Time Complexity | Worst Case Time Complexity |
|-----------|----------------------------|----------------------------|
| `query`   | `O($\sqrt{n}$)`            | `O($\sqrt{n}$)`            |
| `append`  | `O($\sqrt{n}$)`            | `O(n)`                     |
| `insert`  | `O(n) `                    | `O(n)`                     |
| `pop`     | `O(n) `                    | `O(n)`                     |
| `extend` | `O($\sqrt{n + m}$)`         | `O(n + m)`                 |

The main reason for other operations being linear in the worst case is the fact that when the collection is modified, the blocks and aggregates need to be recomputed when the square root of the size of the collection changes. Furthermore, as `PySquagg` is a subclass of list, some of these performance characteristics are inherent.
## Benchmarks

Some preliminary benchmarking can be conducted from scripts in the `benchmarks` directory. One highlight from comparing `query` to performing computations on the arbitrary slices (using `sum` as the aggregator function) is:

| Operation | PySquagg (s) |  Naive (s) |
|-----------|--------------|------------|
| `query`   | 0.032        | 1.48      |


# Constraints
The aggregator functions need to be associative and commutative, and the data structure is not thread-safe.


# TODO
- [ ] Identify if we can reduce the runtime of some operations to be sublinear


> 💡 Interested in contributing? Check out the [Local Development & Contributions Guide](https://github.com/danielenricocahall/pysquagg/blob/main/CONTRIBUTING.md).