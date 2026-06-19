import pandas as pd
import simpy
from typing import Dict, Any
from simulation.registry import SimulationRegistry

class TelemetryEngine:
    def __init__(self, env: simpy.Environment, registry: SimulationRegistry):
        self.env = env
        self.registry = registry
        self.logs = []
        self.env.process(self._record_states())

    def _record_states(self):
        while True:
            state = {'Timestamp_Hours': self.env.now}
            for key, node in self.registry.assets.items():
                state[f'Asset_{key}_Level_Tons'] = round(node.level, 2)
            for proc in self.registry.processes:
                state[f'Process_{proc.name}_Status'] = proc.status
                state[f'Process_{proc.name}_CumProduced_Tons'] = round(proc.total_produced_tons, 2)
            for link in self.registry.logistics:
                state[f'Logistics_{link.name}_ActiveTrucks'] = link.active_trucks_in_transit
                
            self.logs.append(state)
            yield self.env.timeout(1.0)

    def export_to_csv(self, file_path: str):
        df = pd.DataFrame(self.logs)
        df.to_csv(file_path, index=False)