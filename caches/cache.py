from math import ceil, log


class Cache:
    def __init__(self, num_sets, blocks_per_set, block_size):
        self.num_sets = num_sets
        self.blocks_per_set = blocks_per_set
        self.block_size = block_size

        self.sets = [[0] * blocks_per_set for _ in range(num_sets)]
        self.access_time = [[0] * blocks_per_set for _ in range(num_sets)]
        self.valid = [[False] * blocks_per_set for _ in range(num_sets)]

        self.offset_bits = int(ceil(log(block_size, 2)))
        self.set_bits = int(ceil(log(num_sets, 2)))
        self.offset_mask = int((2 ** self.offset_bits) - 1)
        self.set_mask = int((2 ** self.set_bits) - 1) << self.offset_bits

        self.reset_count()

    def reset_count(self):
        self.accesses = self.misses = self.read_misses = self.write_misses = 0

    def __str__(self):
        return ("Cache: {} sets of {} ".format(self.num_sets, self.blocks_per_set)
                + "blocks of size {} ".format(self.block_size)
                + "and miss rate {}/{}".format(self.misses, self.accesses))

    def _choose_victim(self, set_index):
        for block in range(self.blocks_per_set):
            if not self.valid[set_index][block]:
                return block
        return min(enumerate(self.access_time[set_index]), key=lambda x: x[1])[0]

    def _address_in_set(self, set_index, base_address):
        for block in range(self.blocks_per_set):
            if self.valid[set_index][block] and self.sets[set_index][block] == base_address:
                return True
        return False

    def _update(self, set_index, base_address):
        victim = self._choose_victim(set_index)
        self.sets[set_index][victim] = base_address
        self.valid[set_index][victim] = True
        max_time = max(self.access_time[set_index])
        self.access_time[set_index][victim] = max_time + 1

    def access(self, address, size, access_type):
        self.accesses += 1
        set_index = (address & self.set_mask) >> self.offset_bits
        set_index %= self.num_sets
        offset = address & self.offset_mask
        if offset + size > self.block_size:
            # Don't want to deal with accesses that need to span multiple blocks
            raise ValueError("Access of {} bytes at {} requires >1 block".format(size, address))
        base_address = address - offset
        if not self._address_in_set(set_index, base_address):
            self._update(set_index, base_address)
            self.misses += 1
            if access_type == "r":
                self.read_misses += 1
            elif access_type == "w":
                self.write_misses += 1
            else:
                raise ValueError("Unknown access type {}".format(access_type))
