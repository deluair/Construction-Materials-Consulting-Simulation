"""
Steel Industry Transformation Simulation (2025-2040)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TechnologyParameters:
    """Technology-specific parameters for steel production"""
    name: str
    capex_base: float  # Base CAPEX in EUR/tonne
    opex_base: float  # Base OPEX in EUR/tonne
    carbon_intensity: float  # tCO2/tonne
    learning_rate: float  # Annual cost reduction rate
    min_scale: float  # Minimum economic scale in tonnes/year
    max_scale: float  # Maximum practical scale in tonnes/year

@dataclass
class SteelScenario:
    """Steel industry transformation scenario configuration"""
    name: str
    carbon_price_start: float
    carbon_price_growth: float
    hydrogen_cost_start: float  # EUR/kg
    hydrogen_cost_growth: float
    electricity_cost_start: float  # EUR/MWh
    electricity_cost_growth: float
    scrap_availability_growth: float
    technology_adoption_rate: float

class SteelIndustryModel:
    """Simulates steel industry transformation and decarbonization pathways"""
    
    def __init__(self, start_year: int = 2025, end_year: int = 2040):
        self.start_year = start_year
        self.end_year = end_year
        self.years = np.arange(start_year, end_year + 1)
        
        # Initialize technology parameters
        self._init_technologies()
        
        # Initialize market data
        self._init_market_data()
    
    def _init_technologies(self):
        """Initialize technology parameters with realistic values"""
        self.technologies = {
            'BF-BOF': TechnologyParameters(
                name='Blast Furnace - Basic Oxygen Furnace',
                capex_base=800.0,
                opex_base=400.0,
                carbon_intensity=1.8,
                learning_rate=0.01,
                min_scale=2_000_000,
                max_scale=5_000_000
            ),
            'EAF': TechnologyParameters(
                name='Electric Arc Furnace',
                capex_base=600.0,
                opex_base=300.0,
                carbon_intensity=0.3,
                learning_rate=0.02,
                min_scale=500_000,
                max_scale=2_000_000
            ),
            'H2-DRI': TechnologyParameters(
                name='Hydrogen-based Direct Reduced Iron',
                capex_base=1200.0,
                opex_base=500.0,
                carbon_intensity=0.1,
                learning_rate=0.05,
                min_scale=1_000_000,
                max_scale=3_000_000
            )
        }
    
    def _init_market_data(self):
        """Initialize market data with realistic values"""
        # Global steel production (million tonnes)
        self.base_production = 1_900.0
        
        # Technology mix in 2025
        self.initial_mix = {
            'BF-BOF': 0.70,
            'EAF': 0.25,
            'H2-DRI': 0.05
        }
        
        # Scrap availability (million tonnes)
        self.base_scrap = 600.0
        
        # Regional production shares
        self.regional_shares = {
            'Asia': 0.70,
            'Europe': 0.15,
            'North America': 0.10,
            'Other': 0.05
        }
    
    def simulate_scenario(self, scenario: SteelScenario) -> Dict[str, pd.DataFrame]:
        """
        Simulate steel industry transformation under given scenario
        
        Args:
            scenario: SteelScenario configuration
            
        Returns:
            Dictionary containing simulation results
        """
        # Calculate cost evolution
        costs = self._calculate_cost_evolution(scenario)
        
        # Calculate technology adoption
        adoption = self._calculate_technology_adoption(scenario, costs)
        
        # Calculate production and emissions
        production = self._calculate_production_evolution(adoption)
        emissions = self._calculate_emissions(production, adoption)
        
        return {
            'costs': costs,
            'technology_mix': adoption,
            'production': production,
            'emissions': emissions
        }
    
    def _calculate_cost_evolution(self, scenario: SteelScenario) -> pd.DataFrame:
        """Calculate technology cost evolution over time"""
        costs = pd.DataFrame(index=self.years)
        
        # Calculate carbon price evolution
        carbon_prices = scenario.carbon_price_start * (1 + scenario.carbon_price_growth) ** (self.years - self.start_year)
        
        # Calculate hydrogen cost evolution
        hydrogen_costs = scenario.hydrogen_cost_start * (1 + scenario.hydrogen_cost_growth) ** (self.years - self.start_year)
        
        # Calculate electricity cost evolution
        electricity_costs = scenario.electricity_cost_start * (1 + scenario.electricity_cost_growth) ** (self.years - self.start_year)
        
        # Calculate technology-specific costs
        for tech_name, tech in self.technologies.items():
            # Base cost reduction through learning
            base_capex = tech.capex_base * (1 - tech.learning_rate) ** (self.years - self.start_year)
            base_opex = tech.opex_base * (1 - tech.learning_rate) ** (self.years - self.start_year)
            
            # Add carbon cost
            carbon_cost = tech.carbon_intensity * carbon_prices
            
            # Add energy costs
            if tech_name == 'H2-DRI':
                energy_cost = 50 * hydrogen_costs  # kg H2 per tonne of steel
            elif tech_name == 'EAF':
                energy_cost = 0.5 * electricity_costs  # MWh per tonne of steel
            else:
                energy_cost = 0.2 * electricity_costs  # MWh per tonne of steel
            
            costs[f'{tech_name}_total_cost'] = base_capex + base_opex + carbon_cost + energy_cost
        
        return costs
    
    def _calculate_technology_adoption(
        self,
        scenario: SteelScenario,
        costs: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate technology adoption rates over time"""
        adoption = pd.DataFrame(index=self.years)
        
        # Initial technology mix
        for tech_name in self.technologies:
            adoption[tech_name] = self.initial_mix[tech_name]
        
        # Calculate adoption evolution
        for year in self.years[1:]:
            prev_year = year - 1
            
            # Calculate cost differentials
            cost_diffs = {}
            for tech_name in self.technologies:
                cost_diffs[tech_name] = costs.loc[year, f'{tech_name}_total_cost']
            
            # Calculate adoption shifts based on cost differentials
            total_cost = sum(cost_diffs.values())
            for tech_name in self.technologies:
                cost_share = cost_diffs[tech_name] / total_cost
                adoption.loc[year, tech_name] = (
                    adoption.loc[prev_year, tech_name] * (1 - scenario.technology_adoption_rate) +
                    (1 - cost_share) * scenario.technology_adoption_rate
                )
        
        return adoption
    
    def _calculate_production_evolution(self, adoption: pd.DataFrame) -> pd.DataFrame:
        """Calculate production evolution by technology"""
        production = pd.DataFrame(index=self.years)
        
        # Calculate total production growth
        production_growth = 0.02  # 2% annual growth
        total_production = self.base_production * (1 + production_growth) ** (self.years - self.start_year)
        
        # Calculate production by technology
        for tech_name in self.technologies:
            production[tech_name] = total_production * adoption[tech_name]
        
        return production
    
    def _calculate_emissions(
        self,
        production: pd.DataFrame,
        adoption: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate emissions evolution"""
        emissions = pd.DataFrame(index=self.years)
        
        # Calculate emissions by technology
        for tech_name, tech in self.technologies.items():
            emissions[tech_name] = production[tech_name] * tech.carbon_intensity
        
        # Calculate total emissions
        emissions['total'] = emissions.sum(axis=1)
        
        return emissions

# Example usage
if __name__ == "__main__":
    # Create a baseline scenario
    baseline_scenario = SteelScenario(
        name="Baseline",
        carbon_price_start=80.0,
        carbon_price_growth=0.08,
        hydrogen_cost_start=4.0,
        hydrogen_cost_growth=-0.05,
        electricity_cost_start=60.0,
        electricity_cost_growth=0.02,
        scrap_availability_growth=0.03,
        technology_adoption_rate=0.05
    )
    
    # Initialize and run simulation
    model = SteelIndustryModel()
    results = model.simulate_scenario(baseline_scenario)
    
    # Print summary of results
    print("\nTechnology Mix Evolution:")
    print(results['technology_mix'].tail())
    
    print("\nEmissions Evolution (million tonnes CO2):")
    print(results['emissions']['total'].tail()) 