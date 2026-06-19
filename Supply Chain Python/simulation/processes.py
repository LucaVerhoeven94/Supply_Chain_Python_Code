import simpy
from typing import Any

class ProductionProcess:
    def __init__(self, env, name, source_node, dest_node, flow_rate, process_yield, 
                 active_by_default=True, max_production=None, empty_status="Suspended"):
        self.env = env
        self.name = name
        self.source = source_node
        self.dest = dest_node
        self.flow_rate = flow_rate  
        self.process_yield = process_yield
        self.is_running = active_by_default
        self.max_production = max_production 
        self.empty_status = empty_status 
        
        self.status = "Idle"                
        self.total_produced_tons = 0.0      
        self.is_under_maintenance = False  
        
        self.process_loop = self.env.process(self._run())

    def _run(self):
        while True:
            # 1. Master Maintenance Lockout
            if self.is_under_maintenance:
                self.is_running = False
                self.status = "Under Maintenance"
                yield self.env.timeout(1.0)
                continue

            # 2. Production Cap Check
            if self.max_production and self.total_produced_tons >= self.max_production:
                self.is_running = False
                self.status = "Completed"
                yield self.env.timeout(1.0)
                continue

            # 3. Normal Fluid Dynamics Work
            if self.is_running:
                consumed = self.flow_rate
                produced = consumed * self.process_yield
                
                if self.source.level < consumed:
                    self.status = self.empty_status 
                    yield self.env.timeout(1.0)
                    continue
                    
                if self.dest.free_space < produced:
                    self.status = "Blocked"
                    yield self.env.timeout(1.0)
                    continue
                
                self.status = "Running"
                yield self.source.container.get(consumed)
                yield self.dest.container.put(produced)
                self.total_produced_tons += produced
            else:
                if self.status != "Completed": 
                    self.status = "Suspended"
                
            yield self.env.timeout(1.0)


class BatchProductionProcess(ProductionProcess):
    def __init__(self, env, name, source_node, dest_node, batch_size, processing_hours, process_yield, active_by_default=True):
        self.batch_size = batch_size
        self.processing_hours = processing_hours
        super().__init__(env, name, source_node, dest_node, flow_rate=0.0, process_yield=process_yield, active_by_default=active_by_default)

    def _run(self):
        while True:
            # 1. Master Maintenance Lockout
            if self.is_under_maintenance:
                self.is_running = False
                self.status = "Under Maintenance"
                yield self.env.timeout(1.0)
                continue

            if self.is_running:
                # If source doesn't have enough for a full batch, sleep cleanly
                if self.source.level < self.batch_size:
                    self.status = "Suspended"
                    yield self.env.timeout(1.0)
                    continue
                
                produced_batch = self.batch_size * self.process_yield
                if self.dest.free_space < produced_batch:
                    self.status = "Blocked"
                    yield self.env.timeout(1.0)
                    continue
                
                self.status = "Processing Batch"
                yield self.source.container.get(self.batch_size)
                yield self.env.timeout(self.processing_hours)
                yield self.dest.container.put(produced_batch)
                self.total_produced_tons += produced_batch
            else:
                self.status = "Suspended"
                yield self.env.timeout(1.0)