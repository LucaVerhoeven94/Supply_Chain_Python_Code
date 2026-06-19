from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class SimulationRegistry:
    """Central registry acting as the single source of truth for topology and telemetry."""
    assets: Dict[str, Any] = field(default_factory=dict)
    processes: List[Any] = field(default_factory=list)
    logistics: List[Any] = field(default_factory=list)
    controllers: List[Any] = field(default_factory=list)
    metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def register_asset(self, key: str, asset: Any, site: str, display_name: str):
        self.assets[key] = asset
        self.metadata[key] = {"site": site, "name": display_name, "type": "asset"}

    def register_process(self, process: Any):
        self.processes.append(process)

    def register_logistics(self, link: Any):
        self.logistics.append(link)

    def register_controller(self, controller: Any):
        self.controllers.append(controller)