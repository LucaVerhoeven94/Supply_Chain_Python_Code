import simpy
from typing import Any

class TransportLink:
    def __init__(self, env: simpy.Environment, name: str, source_node: Any, dest_node: Any, 
                 batch_size: float, transit_hours: float, trigger_pct: float = 0.0, upstream_process: Any = None):
        self.env = env
        self.name = name
        self.source = source_node
        self.dest = dest_node
        self.batch_size = batch_size
        self.transit_hours = transit_hours
        self.trigger_pct = trigger_pct  
        self.upstream = upstream_process
        
        self.active_trucks_in_transit = 0
        self.total_trucks_dispatched = 0
        self.total_tons_transported = 0
        self.shipping_allowed = False if trigger_pct > 0.0 else True
        
        self.env.process(self._run())

    def _run(self):
        while True:
            is_campaign_end = self.upstream and self.upstream.status == "Completed"

            if self.trigger_pct > 0.0:
                threshold = self.source.container.capacity * self.trigger_pct
                if not self.shipping_allowed and (self.source.level >= threshold or is_campaign_end):
                    self.shipping_allowed = True
                if self.shipping_allowed and self.source.level < self.batch_size and not is_campaign_end:
                    self.shipping_allowed = False

            if self.shipping_allowed and self.source.level >= self.batch_size:
                yield self.source.container.get(self.batch_size)
                self.active_trucks_in_transit += 1
                self.total_trucks_dispatched += 1
                self.total_tons_transported += self.batch_size
                self.env.process(self._transit_routine())
                yield self.env.timeout(0.5)
            else:
                yield self.env.timeout(1.0)

    def _transit_routine(self):
        yield self.env.timeout(self.transit_hours)
        while self.dest.free_space < self.batch_size:
            yield self.env.timeout(0.5)
        yield self.dest.container.put(self.batch_size)
        self.active_trucks_in_transit -= 1


class RawMaterialSupplier:
    def __init__(self, env: simpy.Environment, dest_node: Any, rate: float):
        self.env, self.dest, self.rate = env, dest_node, rate
        self.env.process(self._run())
        
    def _run(self):
        while True:
            if self.dest.free_space >= self.rate:
                yield self.dest.container.put(self.rate)
            yield self.env.timeout(1.0)