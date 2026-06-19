import pygame
import sys
import simpy
from typing import Any
from .layout_engine import TopologyLayoutEngine
from .widgets import SiteWidget, TankWidget, ProcessWidget, TransportWidget
from simulation.registry import SimulationRegistry
from simulation.telemetry import TelemetryEngine

class PygameVisualizer:
    def __init__(self, env: simpy.Environment, registry: SimulationRegistry, telemetry: TelemetryEngine, duration: int = 8765):
        self.env = env
        self.registry = registry
        self.telemetry = telemetry
        self.duration = duration
        
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 700))
        pygame.display.set_caption("Graph-Driven Supply Chain Engine Framework")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Segoe UI", 12)
        self.font_bold = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
        
        self.layout_engine = TopologyLayoutEngine(self.registry)
        self.site_bounds, self.tank_positions = self.layout_engine.compute_layout()

    def run(self):
        running = True
        simulation_active = True
        
        # Locate terminal consumption node for dashboard reporting updates
        purified_tank_key = next((k for k, v in self.registry.assets.items() if "Purified" in k or "Final" in v.name), None)

        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if simulation_active:
                if self.env.now < self.duration:
                    try:
                        self.env.run(until=self.env.now + 1)
                    except Exception as e:
                        print(f"Simulation Runtime Exception: {e}")
                        break
                else:
                    simulation_active = False
                    self.telemetry.export_to_csv('enhanced_supply_chain_logbook.csv')
                    print(f"\n[Framework Finished] Exported data. Viewport locked.")

            self.screen.fill((244, 246, 249))

            # 1. Render Dynamic Structural Site Zones
            for site_name, bounds in self.site_bounds.items():
                SiteWidget.draw(self.screen, bounds, site_name, self.font_title)

            # 2. Render Process Pipelines via Discovered Registry Topology Graph
            # Look up internal asset string keys to obtain positions
            asset_to_key = {v: k for k, v in self.registry.assets.items()}
            for proc in self.registry.processes:
                src_key = asset_to_key.get(proc.source)
                dest_key = asset_to_key.get(proc.dest)
                if src_key and dest_key:
                    ProcessWidget.draw(self.screen, self.tank_positions[src_key], self.tank_positions[dest_key], proc.name, proc.status, self.font, self.font_bold)

            # 3. Render Logistics Bridge Flows
            for link in self.registry.logistics:
                src_key = asset_to_key.get(link.source)
                dest_key = asset_to_key.get(link.dest)
                if src_key and dest_key:
                    TransportWidget.draw(self.screen, self.tank_positions[src_key], self.tank_positions[dest_key], link.name, link.active_trucks_in_transit, self.font, self.font_bold)

            # 4. Render Nodes Storage Asset Cards
            for key, asset in self.registry.assets.items():
                TankWidget.draw(self.screen, self.tank_positions[key], self.registry.metadata[key]["name"], asset.level, asset.max_tons, self.font, self.font_bold)

            # 5. Render Core Standardized Dashboards Panels
            pygame.draw.rect(self.screen, (44, 62, 80), (0, 0, 1200, 60))
            self.screen.blit(self.font_title.render("Supply Chain Engine Framework v2.0", True, (255, 255, 255)), (25, 18))
            status_txt = f"Time: {self.env.now} / {self.duration} Hrs" if simulation_active else "SIMULATION RUN COMPLETION"
            self.screen.blit(self.font_title.render(status_txt, True, (241, 196, 15)), (850, 18))

            # Footer panels
            pygame.draw.rect(self.screen, (222, 226, 233), (25, 625, 1155, 60), border_radius=8)
            if purified_tank_key:
                final_stock = self.registry.assets[purified_tank_key].level
                self.screen.blit(self.font_title.render(f"Output Stock Volume ({self.registry.metadata[purified_tank_key]['name']}): {final_stock:.2f} Tons", True, (39, 174, 96)), (650, 642))

            pygame.display.flip()

        pygame.quit()