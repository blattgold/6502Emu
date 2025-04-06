class Memory:
    def __init__(self):
        self.resetMemory()
    
    def getByte(self, addr):
        return self._memory[addr]
    
    def setByte(self, addr: int, val: int):
        assert(addr >= 0 and addr < 65536)
        assert(val >= 0 and val < 256)
        assert(type(val) == int and type(addr) == int)
        self._memory[addr] = val
    
    def setBytes(self, addrStart, valArray):
        assert(type(addrStart) == int)
        for val in valArray:
            assert(val >= 0 and val < 256)
            assert(type(val == int))

        for i in range(len(valArray)):
            self._memory[i + addrStart] = valArray[i]
    
    def resetMemory(self):
        '''
        sets all bytes to zero and loads reset vector
        '''
        self.zeroMemory()
        # reset vector: 0xFFFD - 0xFFFC
        #               0x10     0x00   = 0x1000
        self.setByte(0xFFFC, 0x00)
        self.setByte(0xFFFD, 0x10)

    def zeroMemory(self):
        '''
        sets all bytes to zero
        '''
        self._memory = [0 for i in range(65536)]