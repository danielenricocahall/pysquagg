from math import sqrt, floor
from typing import Any, Iterable


class PySquagg(list):
    def __init__(self, data: Iterable[Any]):
        super().__init__(data)
        self.blocks = self.compute_blocks()

    @property
    def block_size(self):
        return floor(sqrt(len(self)))

    @property
    def block_count(self):
        return floor(len(self) / self.block_size)

    def compute_blocks(self):
        blocks = []
        for i in range(0, len(self), self.block_size):
            blocks.append(self[i : i + self.block_size])
        return blocks

    def append(self, __object):
        block_size = self.block_size
        super().append(__object)
        new_block_size = self.block_size
        if new_block_size != block_size:
            self.blocks = self.compute_blocks()
        else:
            self.blocks[-1].append(__object)

    def insert(self, __index, __object):
        block_size = self.block_size
        super().insert(__index, __object)
        new_block_size = self.block_size
        if new_block_size != block_size:
            self.blocks = self.compute_blocks()
        else:
            block_index = __index // block_size
            self.blocks[block_index].insert(__index % block_size, __object)

    def sort(self, *, key=None, reverse=False):
        super().sort(key=key, reverse=reverse)
        self.compute_blocks()

    def pop(self, __index=-1):
        block_size = self.block_size
        super().pop(__index)
        new_block_size = self.block_size
        if new_block_size != block_size:
            self.blocks = self.compute_blocks()

    def reverse(self):
        super().reverse()
        self.blocks.reverse()
        self.blocks = [block[::-1] for block in self.blocks]
