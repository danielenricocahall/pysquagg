from math import sqrt, floor
from typing import Any, Iterable, Callable


class InvalidRangeException(Exception): ...


class PySquagg(list):
    def __init__(self, data: Iterable[Any], aggregator_function: Callable):
        super().__init__(data)
        self.aggregator_function = aggregator_function
        self._blocks = self.compute_blocks()

    @property
    def block_size(self):
        return floor(sqrt(len(self)))

    @property
    def block_count(self):
        return floor(len(self) / self.block_size)

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, blocks_):
        self._blocks = blocks_
        if hasattr(self, "_aggregated_values"):
            del self._aggregated_values

    @property
    def aggregated_values(self):
        if not hasattr(self, "_aggregated_values"):
            self.aggregated_values = [
                self.aggregator_function(block) for block in self.blocks
            ]
        return self._aggregated_values

    @aggregated_values.setter
    def aggregated_values(self, values):
        self._aggregated_values = values

    def compute_blocks(self):
        return [
            self[i : i + self.block_size] for i in range(0, len(self), self.block_size)
        ]

    def append(self, __object):
        block_size = self.block_size
        super().append(__object)
        new_block_size = self.block_size
        if new_block_size != block_size:
            self.blocks = self.compute_blocks()
        else:
            if len(self.blocks[-1]) < self.block_size:
                self.blocks[-1].append(__object)
            else:
                self.blocks.append([__object])
            self.aggregated_values[-1] = self.aggregator_function(self.blocks[-1])

    def insert(self, __index, __object):
        block_size = self.block_size
        super().insert(__index, __object)
        new_block_size = self.block_size
        if new_block_size != block_size:
            self.blocks = self.compute_blocks()
        else:
            block_index = __index // block_size
            self.blocks[block_index].insert(__index % block_size, __object)
            self.aggregated_values[block_index] = self.aggregator_function(
                self.blocks[block_index]
            )

    def sort(self, *, key=None, reverse=False):
        super().sort(key=key, reverse=reverse)
        self.blocks = self.compute_blocks()

    def extend(self, __iterable):
        block_size = self.block_size
        super().extend(__iterable)
        new_block_size = self.block_size
        if new_block_size != block_size:
            self.blocks = self.compute_blocks()
        else:
            if len(self.blocks[-1]) < self.block_size:
                index = self.block_size - len(self.blocks[-1])
                self.blocks[-1] += __iterable[:index]
                self.aggregated_values[-1] = self.aggregator_function(self.blocks[-1])
                remaining_iterable = __iterable[index:]
                if remaining_iterable:
                    self.__extend_blocks(remaining_iterable)
            else:
                self.__extend_blocks(__iterable)

    def __extend_blocks(self, iterable):
        new_blocks = [
            iterable[i : i + self.block_size]
            for i in range(0, len(iterable), self.block_size)
        ]
        self.blocks.extend(new_blocks)
        self.aggregated_values += [
            self.aggregator_function(block) for block in new_blocks
        ]

    def pop(self, __index=-1):
        block_size = self.block_size
        super().pop(__index)
        new_block_size = self.block_size
        if new_block_size != block_size:
            self.blocks = self.compute_blocks()
        else:
            block_index = __index // block_size
            self.blocks[block_index].pop(__index % block_size if __index >= 0 else -1)
            if len(self.blocks[block_index]) == 0:
                del self.blocks[block_index]
                del self.aggregated_values[block_index]
            else:
                self.aggregated_values[block_index] = self.aggregator_function(
                    self.blocks[block_index]
                )

    def reverse(self):
        super().reverse()
        self.blocks.reverse()
        self.blocks = [block[::-1] for block in self.blocks]

    def __add__(self, other):
        return PySquagg(super().__add__(other), self.aggregator_function)

    def __iadd__(self, other):
        self.extend(other)
        return self

    def query(self, left: int, right: int):
        if right - left <= 0:
            raise InvalidRangeException(
                f"Invalid range of {left} - {right}. Please supply a valid range!"
            )
        left_block = left // self.block_size
        right_block = right // self.block_size
        left_block_start_index = left_block * self.block_size
        left_block_end_index = left_block_start_index + len(self.blocks[left_block]) - 1
        if left != left_block_start_index:
            initial_value = self.aggregator_function(
                self[left : left_block_end_index + 1]
            )
        else:
            initial_value = self.aggregated_values[left_block]
        right_block_start_index = right_block * self.block_size
        right_block_end_index = (
            right_block_start_index + len(self.blocks[right_block]) - 1
        )
        if right != right_block_end_index:
            final_value = self.aggregator_function(
                self[right_block_start_index : right + 1]
            )
        else:
            final_value = self.aggregated_values[right_block]
        return self.aggregator_function(
            self.aggregated_values[left_block + 1 : right_block]
            + [initial_value, final_value]
        )

    def clear(self):
        super().clear()
        self.blocks = []
        self.aggregated_values = []
