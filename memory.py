class Memory:
    def __init__(self):
        self.reset_memory()
    
    def get_byte(self, addr):
        assert(addr >= 0 and addr < 65536)
        return self._memory[addr]
    
    def get_two_bytes(self, addr_start: int):
        assert(addr_start >= 0 and addr_start < 65536)
        return (self._memory[addr_start + 1] << 8) | self._memory[addr_start]

    def get_two_bytes_tuple(self, addr_start: int):
        assert(addr_start >= 0 and addr_start < 65536)
        return self._memory[addr_start], self._memory[addr_start + 1]
    
    def set_byte(self, addr: int, val: int):
        assert(addr >= 0 and addr < 65536)
        assert(val >= 0 and val < 256)
        assert(type(val) == int and type(addr) == int)
        self._memory[addr] = val
    
    def set_bytes(self, addr_start, arr: list):
        assert(type(addr_start) == int)
        for val in arr:
            assert(val >= 0 and val < 256)
            assert(type(val == int))

        for i in range(len(arr)):
            self._memory[i + addr_start] = arr[i]
    
    def reset_memory(self):
        '''
        sets all bytes to zero and loads reset vector
        '''
        self.zero_memory()
        # reset vector: 0xFFFD - 0xFFFC
        #               0x10     0x00   = 0x1000
        self.set_byte(0xFFFC, 0x00)
        self.set_byte(0xFFFD, 0x10)

    def zero_memory(self):
        '''
        sets all bytes to zero
        '''
        self._memory = [0 for i in range(65536)]