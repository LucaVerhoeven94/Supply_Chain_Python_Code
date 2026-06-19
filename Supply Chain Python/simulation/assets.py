import simpy

class StorageTank:
    def __init__(self, env: simpy.Environment, name: str, capacity_m3: float, density: float, init_fill_pct: float = 0.0):
        self.env = env
        self.name = name
        self.density = density
        self.max_tons = capacity_m3 * 0.95 * density
        self.container = simpy.Container(env, capacity=self.max_tons, init=self.max_tons * init_fill_pct)
        
    @property
    def level(self) -> float:
        return self.container.level
    
    @property
    def free_space(self) -> float:
        return self.container.capacity - self.container.level