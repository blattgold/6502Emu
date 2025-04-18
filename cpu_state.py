class CPUState:
    """
    pc: program counter
    hz: clock rate of the cpu
    clock_cycles: clock cycles taken processing current instruction
    clock_cycles_total: total clock cycles taken
    current_instruction: current instruction
    instructions_total: total amount of instructions ran
    ---
    Registers:
    [A]ccumulator
    [X]-index
    [Y]-index
    [S]tack pointer
    ---
    Flags:
    [C]arry
    [Z]ero
    [I]nterrupt disable
    [D]ecimal mode
    [B]reak command
    o[V]erflow
    [N]egative
    """
    _ALLOWED_KEYS = None

    def __init__(self, empty=True):
        self._state = {} if empty else self._make_default_state()

    def _make_default_state(self) -> dict:
        return {
            "pc": 0,
            "hz": 10,
            "clock_cycles": 0,
            "clock_cycles_total": 0,
            "current_instruction": 0,
            "instructions_total": 0,
            "X": 0,
            "Y": 0,
            "A": 0,
            "S": 0,
            "C": False,
            "Z": False,
            "I": False,
            "D": False,
            "B": False,
            "V": False,
            "N": False,
        }
    
    def allowed_keys(self) -> set:
        if not self._ALLOWED_KEYS:
            self._ALLOWED_KEYS = set(self._make_default_state().keys())

        return self._ALLOWED_KEYS

    def set_by_id(self, key: str, value):
        if key not in self.allowed_keys():
            raise ValueError()
        
        self._state[key] = value
    
    def get_by_id(self, key:str):
        if key not in self.allowed_keys():
            raise ValueError()
        
        return self._state[key]
    
    def merge(self, other_state):
        for key in other_state.state.keys():
            if key not in self.allowed_keys():
                raise ValueError()
        
        self._state.update(other_state.state)
    
    def get_state_copy(self):
        state_copy = CPUState()
        state_copy.merge(self)
        return state_copy

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, new_state):
        self._state = new_state

