"""
Main script for running the Construction Materials Transformation Simulation
"""

import argparse
from typing import Dict, List
import pandas as pd
import json
from pathlib import Path
import os

from .core.market import MarketTransformationModel, MarketScenario
from .visualization.dashboard import SimulationDashboard
from construction_materials_sim.core.steel import SteelIndustryModel, SteelScenario
from construction_materials_sim.core.cement import CementIndustryModel, CementScenario

def run_simulation(scenario_config: Dict) -> Dict:
    """
    Run the full simulation for a given scenario configuration
    
    Args:
        scenario_config: Dictionary containing scenario parameters
        
    Returns:
        Dictionary containing simulation results
    """
    # Create scenario
    scenario = MarketScenario(
        name=scenario_config.get('name', 'Custom'),
        carbon_price_start=scenario_config.get('carbon_price_start', 80.0),
        carbon_price_growth=scenario_config.get('carbon_price_growth', 0.08),
        steel_hydrogen_cost_start=scenario_config.get('steel_hydrogen_cost_start', 4.0),
        steel_hydrogen_cost_growth=scenario_config.get('steel_hydrogen_cost_growth', -0.05),
        steel_electricity_cost_start=scenario_config.get('steel_electricity_cost_start', 60.0),
        steel_electricity_cost_growth=scenario_config.get('steel_electricity_cost_growth', 0.02),
        cement_electricity_cost_start=scenario_config.get('cement_electricity_cost_start', 60.0),
        cement_electricity_cost_growth=scenario_config.get('cement_electricity_cost_growth', 0.02),
        cement_alternative_fuel_cost_start=scenario_config.get('cement_alternative_fuel_cost_start', 30.0),
        cement_alternative_fuel_cost_growth=scenario_config.get('cement_alternative_fuel_cost_growth', -0.03),
        green_premium_start=scenario_config.get('green_premium_start', 0.15),
        green_premium_growth=scenario_config.get('green_premium_growth', 0.05),
        customer_adoption_rate=scenario_config.get('customer_adoption_rate', 0.08),
        regulatory_pressure_growth=scenario_config.get('regulatory_pressure_growth', 0.10)
    )
    
    # Run market model
    market_model = MarketTransformationModel()
    market_results = market_model.simulate_scenario(scenario)

    # Run steel model
    steel_scenario = SteelScenario(
        name=scenario.name,
        carbon_price_start=scenario.carbon_price_start,
        carbon_price_growth=scenario.carbon_price_growth,
        hydrogen_cost_start=scenario.steel_hydrogen_cost_start,
        hydrogen_cost_growth=scenario.steel_hydrogen_cost_growth,
        electricity_cost_start=scenario.steel_electricity_cost_start,
        electricity_cost_growth=scenario.steel_electricity_cost_growth,
        scrap_availability_growth=0.03,
        technology_adoption_rate=0.05
    )
    steel_model = SteelIndustryModel()
    steel_results = steel_model.simulate_scenario(steel_scenario)

    # Run cement model
    cement_scenario = CementScenario(
        name=scenario.name,
        carbon_price_start=scenario.carbon_price_start,
        carbon_price_growth=scenario.carbon_price_growth,
        electricity_cost_start=scenario.cement_electricity_cost_start,
        electricity_cost_growth=scenario.cement_electricity_cost_growth,
        alternative_fuel_cost_start=scenario.cement_alternative_fuel_cost_start,
        alternative_fuel_cost_growth=scenario.cement_alternative_fuel_cost_growth,
        clinker_substitution_rate=0.05,
        technology_adoption_rate=0.04
    )
    cement_model = CementIndustryModel()
    cement_results = cement_model.simulate_scenario(cement_scenario)

    # Merge all results
    results = {
        'market_adoption': market_results['market_adoption'],
        'market_value': market_results['market_value'],
        'regional_evolution': market_results['regional_evolution'],
        'steel_industry': steel_results,
        'cement_industry': cement_results
    }
    return results

def save_results(results: dict, output_dir: str):
    """Save simulation results to output directory"""
    os.makedirs(output_dir, exist_ok=True)
    for key, data in results.items():
        if isinstance(data, dict):
            # Nested dict (e.g., steel_industry, cement_industry)
            for subkey, subdata in data.items():
                if hasattr(subdata, 'to_csv'):
                    subdata.to_csv(os.path.join(output_dir, f"{key}_{subkey}.csv"))
                # Save as JSON-serializable
                if hasattr(subdata, 'to_dict'):
                    data[subkey] = subdata.to_dict(orient='split')
            # Save the dict as JSON
            with open(os.path.join(output_dir, f"{key}.json"), 'w') as f:
                json.dump(data, f, indent=2)
        elif hasattr(data, 'to_csv'):
            data.to_csv(os.path.join(output_dir, f"{key}.csv"))
            # Save as JSON-serializable
            if hasattr(data, 'to_dict'):
                data_json = data.to_dict(orient='split')
                with open(os.path.join(output_dir, f"{key}.json"), 'w') as f:
                    json.dump(data_json, f, indent=2)
        else:
            # Save as JSON
            with open(os.path.join(output_dir, f"{key}.json"), 'w') as f:
                json.dump(data, f, indent=2)

def main():
    """Main function to run the simulation"""
    parser = argparse.ArgumentParser(description="Construction Materials Transformation Simulation")
    parser.add_argument("--config", type=str, help="Path to scenario configuration file")
    parser.add_argument("--output", type=str, default="results", help="Output directory for results")
    parser.add_argument("--dashboard", action="store_true", help="Launch interactive dashboard")
    args = parser.parse_args()
    
    if args.dashboard:
        # Launch dashboard
        dashboard = SimulationDashboard()
        dashboard.run_server()
    else:
        # Load scenario configuration
        if args.config:
            with open(args.config, 'r') as f:
                scenario_config = json.load(f)
        else:
            # Use default configuration
            scenario_config = {
                'name': 'Baseline',
                'carbon_price_start': 80.0,
                'carbon_price_growth': 0.08,
                'steel_hydrogen_cost_start': 4.0,
                'steel_hydrogen_cost_growth': -0.05,
                'steel_electricity_cost_start': 60.0,
                'steel_electricity_cost_growth': 0.02,
                'cement_electricity_cost_start': 60.0,
                'cement_electricity_cost_growth': 0.02,
                'cement_alternative_fuel_cost_start': 30.0,
                'cement_alternative_fuel_cost_growth': -0.03,
                'green_premium_start': 0.15,
                'green_premium_growth': 0.05,
                'customer_adoption_rate': 0.08,
                'regulatory_pressure_growth': 0.10
            }
        
        # Run simulation
        results = run_simulation(scenario_config)
        
        # Save results
        save_results(results, args.output)
        
        # Print summary
        print("\nSimulation completed successfully!")
        print(f"Results saved to: {args.output}")
        
        # Print key metrics
        print("\nKey Metrics (2040):")
        print(f"Total Market Value: {results['market_value'].iloc[-1].sum():.1f} billion EUR")
        print(f"Average Market Adoption: {results['market_adoption'].iloc[-1].mean():.1%}")
        # Robustly handle DataFrame or dict for emissions['total']
        steel_emissions = results['steel_industry']['emissions']
        if hasattr(steel_emissions, 'iloc') and 'total' in steel_emissions.columns:
            total_emissions_2040 = steel_emissions['total'].iloc[-1]
        elif isinstance(steel_emissions, dict) and 'columns' in steel_emissions and 'data' in steel_emissions:
            # Find index of 'total' column
            try:
                total_idx = steel_emissions['columns'].index('total')
                total_emissions_2040 = steel_emissions['data'][-1][total_idx]
            except Exception:
                total_emissions_2040 = 'N/A'
        else:
            total_emissions_2040 = 'N/A'
        print(f"Total Emissions: {total_emissions_2040:.1f} MtCO2")

if __name__ == "__main__":
    main() 