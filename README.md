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

| Operation | Time Complexity |
|-----------|-----------------|
| `query`   | `O($\sqrt{n}$)` |
| `append`  | `O(n)`          |
| `insert`  | `O(n) `         |
| `pop`     | `O(n) `         |
| `sort`    | `O(n log n) `   |


# Constraints
The aggregator functions need to be associative and commutative, and the data structure is not thread-safe.






> 💡 Interested in contributing? Check out the [Local Development & Contributions Guide](https://github.com/danielenricocahall/pysquagg/blob/main/CONTRIBUTING.md).