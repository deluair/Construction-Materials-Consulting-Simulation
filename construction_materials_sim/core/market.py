"""
Market Transformation and Customer Adoption Simulation (2025-2040)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class MarketScenario:
    """Market scenario parameters"""
    name: str
    carbon_price_start: float
    carbon_price_growth: float
    steel_hydrogen_cost_start: float
    steel_hydrogen_cost_growth: float
    steel_electricity_cost_start: float
    steel_electricity_cost_growth: float
    cement_electricity_cost_start: float
    cement_electricity_cost_growth: float
    cement_alternative_fuel_cost_start: float
    cement_alternative_fuel_cost_growth: float
    green_premium_start: float
    green_premium_growth: float
    customer_adoption_rate: float
    regulatory_pressure_growth: float
    regional_variations: Dict[str, Dict[str, float]] = None

class MarketTransformationModel:
    """Market transformation and customer adoption model"""
    
    def __init__(self):
        self.start_year = 2025
        self.end_year = 2040
        self.years = range(self.start_year, self.end_year + 1)
        
        # Initialize regional market characteristics
        self.regional_markets = {
            'Europe': {
                'market_maturity': 0.8,
                'regulatory_pressure': 0.9,
                'price_sensitivity': 0.7
            },
            'North_America': {
                'market_maturity': 0.7,
                'regulatory_pressure': 0.8,
                'price_sensitivity': 0.8
            },
            'Asia': {
                'market_maturity': 0.6,
                'regulatory_pressure': 0.6,
                'price_sensitivity': 0.9
            },
            'Other': {
                'market_maturity': 0.5,
                'regulatory_pressure': 0.5,
                'price_sensitivity': 0.95
            }
        }
        
        # Initialize customer segments
        self.customer_segments = {
            'Early_Adopters': {
                'size': 0.2,
                'price_sensitivity': 0.5,
                'adoption_rate': 0.15
            },
            'Mainstream': {
                'size': 0.6,
                'price_sensitivity': 0.8,
                'adoption_rate': 0.08
            },
            'Late_Adopters': {
                'size': 0.2,
                'price_sensitivity': 0.9,
                'adoption_rate': 0.04
            }
        }
    
    def simulate_scenario(self, scenario: MarketScenario) -> Dict[str, pd.DataFrame]:
        """Simulate market transformation for a given scenario"""
        
        # Initialize results DataFrames
        market_adoption = pd.DataFrame(index=self.years)
        market_value = pd.DataFrame(index=self.years)
        regional_evolution = pd.DataFrame(index=self.years)
        
        # Initialize regional market characteristics
        for region in self.regional_markets:
            market_adoption[f'{region}_Early_Adopters'] = 0.0
            market_adoption[f'{region}_Mainstream'] = 0.0
            market_adoption[f'{region}_Late_Adopters'] = 0.0
            market_value[f'{region}_Value'] = 0.0
            regional_evolution[f'{region}_Maturity'] = self.regional_markets[region]['market_maturity']
            regional_evolution[f'{region}_Regulatory'] = self.regional_markets[region]['regulatory_pressure']
            regional_evolution[f'{region}_Price_Sensitivity'] = self.regional_markets[region]['price_sensitivity']
        
        # Simulate market evolution
        for year in self.years:
            year_idx = year - self.start_year
            
            # Calculate regional market evolution
            for region in self.regional_markets:
                # Update market characteristics
                regional_evolution.loc[year, f'{region}_Maturity'] = min(
                    1.0,
                    self.regional_markets[region]['market_maturity'] * (1 + scenario.customer_adoption_rate) ** year_idx
                )
                regional_evolution.loc[year, f'{region}_Regulatory'] = min(
                    1.0,
                    self.regional_markets[region]['regulatory_pressure'] * (1 + scenario.regulatory_pressure_growth) ** year_idx
                )
                regional_evolution.loc[year, f'{region}_Price_Sensitivity'] = max(
                    0.3,
                    self.regional_markets[region]['price_sensitivity'] * (1 - 0.02) ** year_idx
                )
                
                # Calculate adoption for each segment
                for segment, params in self.customer_segments.items():
                    # Calculate segment-specific adoption rate
                    base_adoption_rate = params['adoption_rate']
                    regional_factor = regional_evolution.loc[year, f'{region}_Maturity']
                    regulatory_factor = regional_evolution.loc[year, f'{region}_Regulatory']
                    
                    adoption_rate = base_adoption_rate * regional_factor * regulatory_factor
                    
                    # Calculate adoption
                    if year_idx == 0:
                        market_adoption.loc[year, f'{region}_{segment}'] = adoption_rate
                    else:
                        prev_adoption = market_adoption.loc[year-1, f'{region}_{segment}']
                        market_adoption.loc[year, f'{region}_{segment}'] = min(
                            1.0,
                            prev_adoption + adoption_rate * (1 - prev_adoption)
                        )
                
                # Calculate market value
                total_adoption = sum(
                    market_adoption.loc[year, f'{region}_{segment}'] * params['size']
                    for segment, params in self.customer_segments.items()
                )
                
                # Calculate green premium
                green_premium = scenario.green_premium_start * (1 + scenario.green_premium_growth) ** year_idx
                
                # Calculate regional market value
                base_value = 100  # Base market value in billion EUR
                regional_value = base_value * total_adoption * (1 + green_premium)
                market_value.loc[year, f'{region}_Value'] = regional_value
        
        return {
            'market_adoption': market_adoption,
            'market_value': market_value,
            'regional_evolution': regional_evolution
        }

# Example usage
if __name__ == "__main__":
    # Create baseline scenario
    scenario = MarketScenario(
        name="Baseline",
        carbon_price_start=80.0,
        carbon_price_growth=0.08,
        steel_hydrogen_cost_start=4.0,
        steel_hydrogen_cost_growth=-0.05,
        steel_electricity_cost_start=60.0,
        steel_electricity_cost_growth=0.02,
        cement_electricity_cost_start=60.0,
        cement_electricity_cost_growth=0.02,
        cement_alternative_fuel_cost_start=30.0,
        cement_alternative_fuel_cost_growth=-0.03,
        green_premium_start=0.15,
        green_premium_growth=0.05,
        customer_adoption_rate=0.08,
        regulatory_pressure_growth=0.10
    )
    
    # Create and run simulation
    model = MarketTransformationModel()
    results = model.simulate_scenario(scenario)
    
    # Print results
    print("\nMarket Adoption by Region and Segment (2040):")
    print(results['market_adoption'].iloc[-1])
    
    print("\nMarket Value by Region (2040):")
    print(results['market_value'].iloc[-1])
    
    print("\nRegional Market Evolution (2040):")
    print(results['regional_evolution'].iloc[-1]) 