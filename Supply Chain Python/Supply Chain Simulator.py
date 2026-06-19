import simpy
from simulation.registry import SimulationRegistry
from simulation.assets import StorageTank
from simulation.processes import ProductionProcess, BatchProductionProcess
from simulation.logistics import TransportLink
from simulation.controllers import PeriodicMaintenanceController, ThresholdPlantController
from simulation.telemetry import TelemetryEngine
from visualization.renderer import PygameVisualizer

# ==============================================================================
# 🎯 UNIFIED PROCESS CONTROL DASHBOARD
# ==============================================================================
REACTOR_FLOW_RATE = 0.50     # Processing speed (Tons per hour)
REACTOR_UPTIME    = 0.80     # Total target operational fraction (0.80 = 80%)
SHUTDOWN_COUNT    = 4        # Planned shutdown blocks across the timeline
SIM_DURATION      = 8760     # Run timeline (Hours)


def build_and_run_isostearic_scenario():
    env = simpy.Environment()
    registry = SimulationRegistry()

    # Calculate dynamic raw material inventory scale
    yearly_tons_needed = REACTOR_FLOW_RATE * SIM_DURATION
    calculated_raw_capacity = (yearly_tons_needed / 0.9) / 0.95

    # ==========================================================================
    # 🏢 SITE LAYOUT CONFIGURATION
    # ==========================================================================
    # Germany Site (Top Row: tier=0)
    registry.register_asset('Tank0_RawProduct',   StorageTank(env, 'Raw Product', calculated_raw_capacity, 0.9, 1.0), site='Germany', display_name='Raw Product')
    registry.metadata['Tank0_RawProduct'].update({"stage": 0, "tier": 0})
    
    registry.register_asset('Tank1_CrudeIso',     StorageTank(env, 'Crude Product', 180, 0.9, 0.0), site='Germany', display_name='Crude Product')
    registry.metadata['Tank1_CrudeIso'].update({"stage": 1, "tier": 0})
    
    registry.register_asset('Tank2_Monomer_Em',   StorageTank(env, 'Distillate EM', 60, 0.9, 0.0),  site='Germany', display_name='Distillate EM')
    registry.metadata['Tank2_Monomer_Em'].update({"stage": 2, "tier": 0})
    
    # Belgium Site (Top Row: tier=0)
    registry.register_asset('Tank3_Monomer_Ert',  StorageTank(env, 'Distillate ERT', 360, 0.9, 0.0), site='Belgium', display_name='Distillate ERT')
    registry.metadata['Tank3_Monomer_Ert'].update({"stage": 0, "tier": 0})
    
    registry.register_asset('Tank4_Hydro_Buffer', StorageTank(env, 'Hydrogenated ERT', 292.4, 0.9, 0.0), site='Belgium', display_name='Hydro Buffer')
    registry.metadata['Tank4_Hydro_Buffer'].update({"stage": 1, "tier": 0})
    
    # Return Logistics Line (Bottom Row: tier=1)
    registry.register_asset('Tank5_Ert_Buffer',   StorageTank(env, 'Cold Product ERT', 290, 0.9, 0.0), site='Belgium', display_name='Cold Buffer')
    registry.metadata['Tank5_Ert_Buffer'].update({"stage": 1, "tier": 1})
    
    registry.register_asset('Tank7_Em_Return',    StorageTank(env, 'Cold Product EMM', 82, 0.9, 0.0), site='Germany', display_name='EMM Return')
    registry.metadata['Tank7_Em_Return'].update({"stage": 2, "tier": 1})
    
    registry.register_asset('Tank6_Purified',     StorageTank(env, 'Final ISA', 5000, 0.9, 0.0),    site='Germany', display_name='Final Purified ISA')
    registry.metadata['Tank6_Purified'].update({"stage": 1, "tier": 1})

    # ==========================================================================
    # ⚙️ INDUSTRY OPERATIONS LINKAGE
    # ==========================================================================
    proc_reactor = ProductionProcess(env, 'Reactor', registry.assets['Tank0_RawProduct'], registry.assets['Tank1_CrudeIso'], flow_rate=REACTOR_FLOW_RATE, process_yield=0.90)
    
    # Triggered by Threshold Controller
    proc_em_dist = ProductionProcess(env, 'Monomer_Dist', registry.assets['Tank1_CrudeIso'], registry.assets['Tank2_Monomer_Em'], flow_rate=2.5, process_yield=0.86, active_by_default=False)
    
    # Outbound link uses trigger_pct=0.10 to move fluid over as soon as it's distilled
    logistics_outbound = TransportLink(env, 'Outbound_Link', registry.assets['Tank2_Monomer_Em'], registry.assets['Tank3_Monomer_Ert'], batch_size=24, transit_hours=3, trigger_pct=0.10, upstream_process=proc_reactor)
    
    # Triggered by Threshold Controller
    proc_hydrogenation = BatchProductionProcess(env, 'Hydrogenation', registry.assets['Tank3_Monomer_Ert'], registry.assets['Tank4_Hydro_Buffer'], batch_size=16.5, processing_hours=6.0, process_yield=0.99, active_by_default=False)
    
    proc_cold_frac = ProductionProcess(env, 'Cold_Fractionation', registry.assets['Tank4_Hydro_Buffer'], registry.assets['Tank5_Ert_Buffer'], flow_rate=2.5, process_yield=0.743, active_by_default=True)
    
    # Triggered by Threshold Controller
    logistics_inbound = TransportLink(env, 'Inbound_Return_Link', registry.assets['Tank5_Ert_Buffer'], registry.assets['Tank7_Em_Return'], batch_size=24, transit_hours=3, trigger_pct=0.0, upstream_process=proc_reactor)
    
    # Triggered by Threshold Controller
    proc_em_frac = ProductionProcess(env, 'Final_Frac_Dist', registry.assets['Tank7_Em_Return'], registry.assets['Tank6_Purified'], flow_rate=2.5, process_yield=0.96, active_by_default=False)

    # Register components inside graph mappings
    registry.register_process(proc_reactor)
    registry.register_process(proc_em_dist)
    registry.register_process(proc_hydrogenation)
    registry.register_process(proc_cold_frac)
    registry.register_process(proc_em_frac)
    registry.register_logistics(logistics_outbound)
    registry.register_logistics(logistics_inbound)

    # ==========================================================================
    # 🕹️ PLUG AUTOMATED SYSTEM CONTROLLERS TO CENTRAL REGISTRY
    # ==========================================================================
    registry.register_controller(
        PeriodicMaintenanceController(env, proc_reactor, REACTOR_UPTIME, SHUTDOWN_COUNT, SIM_DURATION)
    )
    
    # The New Unified Control Center
    registry.register_controller(
        ThresholdPlantController(env, registry, proc_em_dist, proc_hydrogenation, logistics_inbound, proc_em_frac)
    )

    # Fire Telemetry Log Collector and Visual Renderer
    telemetry = TelemetryEngine(env, registry)
    visualizer = PygameVisualizer(env, registry, telemetry, duration=SIM_DURATION)
    visualizer.run()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 RUNNING AUTOMATED THRESHOLD INDUSTRIAL SYSTEM...")
    print("="*50 + "\n")
    build_and_run_isostearic_scenario()