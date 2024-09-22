class SingletonRegister:
    value: int = 0
    name: str = ""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
    
    