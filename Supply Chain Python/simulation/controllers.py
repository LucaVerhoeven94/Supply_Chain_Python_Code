class PeriodicMaintenanceController:
    """Handles scheduled plant shutdowns based on uptime ratios."""
    def __init__(self, env, controlled_process, uptime_pct: float, shutdown_count: int, total_hours: float):
        self.env = env
        self.process = controlled_process
        
        total_downtime = total_hours * (1.0 - uptime_pct)
        total_uptime = total_hours * uptime_pct
        
        self.shutdown_duration = total_downtime / max(1, shutdown_count)
        self.run_duration = total_uptime / max(1, shutdown_count)
        
        self.env.process(self._maintenance_loop())

    def _maintenance_loop(self):
        while True:
            self.process.is_under_maintenance = False
            self.process.is_running = True
            yield self.env.timeout(self.run_duration)
            
            self.process.is_under_maintenance = True
            self.process.is_running = False
            yield self.env.timeout(self.shutdown_duration)


class ThresholdPlantController:
    """
    Coordinates the automated step-by-step triggers across the entire plant:
    1. Crude Distillation starts when Crude Tank hits 90%.
    2. Hydrogenation starts when Distillate ERT hits 90%.
    3. Return Trucks activate when Cold Buffer ERT hits 90%.
    4. Final Emmerich Distillation runs immediately when the first cistern (24T) arrives.
    """
    def __init__(self, env, registry, em_dist, hydro, return_link, final_dist):
        self.env = env
        self.registry = registry
        self.em_dist = em_dist
        self.hydro = hydro
        self.return_link = return_link
        self.final_dist = final_dist
        
        # Start targeted units as False (waiting for their triggers)
        self.em_dist.is_running = False
        self.hydro.is_running = False
        self.return_link.shipping_allowed = False
        self.final_dist.is_running = False

        self.env.process(self._control_loop())

    def _control_loop(self):
        while True:
            yield self.env.timeout(1.0) # Check status every single hour

            # --- 1. GERMANY CRUDE DISTILLATION TRIGGER (90%) ---
            crude_tank = self.registry.assets['Tank1_CrudeIso']
            crude_pct = crude_tank.level / crude_tank.container.capacity
            if not self.em_dist.is_running and crude_pct >= 0.90:
                self.em_dist.is_running = True
            elif self.em_dist.is_running and crude_tank.level <= 1.0:
                self.em_dist.is_running = False # Turn off when empty

            # --- 2. BELGIUM HYDROGENATION TRIGGER (90%) ---
            ert_tank = self.registry.assets['Tank3_Monomer_Ert']
            ert_pct = ert_tank.level / ert_tank.container.capacity
            if not self.hydro.is_running and ert_pct >= 0.90:
                self.hydro.is_running = True
            elif self.hydro.is_running and ert_tank.level < self.hydro.batch_size:
                self.hydro.is_running = False # Turn off when it can't feed a batch

            # --- 3. ERTVELDE RETURN TRUCKS TRIGGER (90%) ---
            cold_buffer = self.registry.assets['Tank5_Ert_Buffer']
            cold_pct = cold_buffer.level / cold_buffer.container.capacity
            if not self.return_link.shipping_allowed and cold_pct >= 0.90:
                self.return_link.shipping_allowed = True
            elif self.return_link.shipping_allowed and cold_buffer.level <= 1.0:
                self.return_link.shipping_allowed = False

            # --- 4. EMMERICH FINAL DISTILLATION TRIGGER (First Cistern Arrival) ---
            return_tank = self.registry.assets['Tank7_Em_Return']
            # Starts running as soon as the first full truck delivery (24 Tons) lands in Germany
            if not self.final_dist.is_running and return_tank.level >= 24.0:
                self.final_dist.is_running = True
            elif self.final_dist.is_running and return_tank.level <= 1.0:
                self.final_dist.is_running = False