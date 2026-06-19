from typing import Dict, Tuple, List
from simulation.registry import SimulationRegistry

class TopologyLayoutEngine:
    """Calculates clean positions using pipeline stages and rows instead of raw coordinates."""
    def __init__(self, registry: SimulationRegistry, surface_width: int = 1200, surface_height: int = 700):
        self.registry = registry
        self.width = surface_width
        self.height = surface_height

    def compute_layout(self) -> Tuple[Dict[str, Tuple[int, int, int, int]], Dict[str, Tuple[int, int, int, int]]]:
        site_groups: Dict[str, List[str]] = {}
        for key, meta in self.registry.metadata.items():
            site = meta["site"]
            site_groups.setdefault(site, []).append(key)

        site_bounds = {}
        tank_positions = {}
        
        num_sites = len(site_groups)
        site_width = (self.width - (40 * (num_sites + 1))) // num_sites
        site_height = self.height - 185

        for idx, (site_name, asset_keys) in enumerate(site_groups.items()):
            # Create the main site box
            sx = 25 + idx * (site_width + 40)
            sy = 95
            site_bounds[site_name] = (sx, sy, site_width, site_height)
            
            for key in asset_keys:
                meta = self.registry.metadata[key]
                # Default values if stage/tier are missing
                stage = meta.get("stage", 0)
                tier = meta.get("tier", 0)
                
                # Calculate X positioning based on stage columns
                # Germany has 3 columns, Belgium has 2 columns
                max_cols = 3 if site_name.lower() == "germany" else 2
                x_margin = 40
                col_width = (site_width - (x_margin * 2) - 85) // max(1, max_cols - 1)
                
                px = sx + x_margin + (stage * col_width)
                
                # Calculate Y positioning based on tier rows
                # Tier 0 sits at the top, Tier 1 sits at the bottom
                py = sy + 75 if tier == 0 else sy + 355
                
                tank_positions[key] = (int(px), int(py), 85, 120)
                
        return site_bounds, tank_positions