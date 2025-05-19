"""
Main script for running the Construction Materials Transformation Simulation
"""

import argparse
from typing import Dict, List
import pandas as pd
import json
from pathlib import Path

from .core.market import MarketTransformationModel, MarketScenario
from .visualization.dashboard import SimulationDashboard

def run_simulation(scenario_config: Dict) -> Dict:
    """
    Run the simulation with given scenario configuration
    
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
    
    # Run simulation
    model = MarketTransformationModel()
    results = model.simulate_scenario(scenario)
    
    return results

def save_results(results: Dict, output_dir: str):
    """
    Save simulation results to files
    
    Args:
        results: Dictionary containing simulation results
        output_dir: Directory to save results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save each result component
    for key, data in results.items():
        if isinstance(data, pd.DataFrame):
            data.to_csv(output_path / f"{key}.csv")
        elif isinstance(data, dict):
            with open(output_path / f"{key}.json", 'w') as f:
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
        print(f"Total Emissions: {results['steel_industry']['emissions']['total'].iloc[-1]:.1f} MtCO2")

if __name__ == "__main__":
    main() 