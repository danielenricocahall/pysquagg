import random
import timeit

from pysquagg.pysquagg import PySquagg

aggregator_function = sum
n = 100000
data = list(range(n))
ps = PySquagg(data, aggregator_function)

num_queries = 10000
queries = []
for _ in range(num_queries):
    left = random.randint(0, n - 1)
    right = random.randint(0, n - 1)
    if left > right:
        left, right = right, left
    queries.append((left, right))


def benchmark_pysquagg():
    total = 0
    for left, right in queries:
        total += ps.query(left, right)
    return total


# Benchmark using a naive approach (direct sum on slices)
def benchmark_naive():
    total = 0
    for left, right in queries:
        total += sum(data[left : right + 1])
    return total


if __name__ == "__main__":
    pysquagg_time = timeit.timeit(benchmark_pysquagg, number=10)
    naive_time = timeit.timeit(benchmark_naive, number=10)
    print(f"PySquagg average time per run: {pysquagg_time / 10:.6f} seconds")
    print(f"Naive approach average time per run: {naive_time / 10:.6f} seconds")
