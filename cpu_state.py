class CPUState:
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
            self._ALLOWED_KEYS = set(_make_default_state.keys())
        return self._ALLOWED_KEYS

    def set_by_id(key: str, value):
        if key not in self.allowed_keys():
            raise ValueError()
        self._state[key] = value
    
    def get_by_id(key:str):
        if key not in self.allowed_keys():
            raise ValueError()
        return self._state[key]

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, new_state):
        self._state = new_state

