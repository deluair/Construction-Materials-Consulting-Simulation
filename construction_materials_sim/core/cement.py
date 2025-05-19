"""
Cement Industry Transformation Simulation (2025-2040)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CementTechnology:
    """Cement production technology parameters"""
    name: str
    capex_base: float  # Base CAPEX in EUR/tonne
    opex_base: float  # Base OPEX in EUR/tonne
    carbon_intensity: float  # tCO2/tonne
    learning_rate: float  # Annual cost reduction rate
    min_scale: float  # Minimum economic scale in tonnes/year
    max_scale: float  # Maximum practical scale in tonnes/year
    clinker_ratio: float  # Clinker to cement ratio
    alternative_fuel_share: float  # Share of alternative fuels

@dataclass
class CementScenario:
    """Cement industry transformation scenario configuration"""
    name: str
    carbon_price_start: float
    carbon_price_growth: float
    electricity_cost_start: float  # EUR/MWh
    electricity_cost_growth: float
    alternative_fuel_cost_start: float  # EUR/tonne
    alternative_fuel_cost_growth: float
    clinker_substitution_rate: float
    technology_adoption_rate: float

class CementIndustryModel:
    """Simulates cement industry transformation and decarbonization pathways"""
    
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
            'Conventional': CementTechnology(
                name='Conventional Kiln',
                capex_base=150.0,
                opex_base=40.0,
                carbon_intensity=0.85,
                learning_rate=0.01,
                min_scale=500_000,
                max_scale=2_000_000,
                clinker_ratio=0.95,
                alternative_fuel_share=0.10
            ),
            'Efficient': CementTechnology(
                name='High-Efficiency Kiln',
                capex_base=200.0,
                opex_base=35.0,
                carbon_intensity=0.75,
                learning_rate=0.02,
                min_scale=750_000,
                max_scale=2_500_000,
                clinker_ratio=0.90,
                alternative_fuel_share=0.25
            ),
            'Alternative': CementTechnology(
                name='Alternative Binder',
                capex_base=250.0,
                opex_base=45.0,
                carbon_intensity=0.40,
                learning_rate=0.05,
                min_scale=300_000,
                max_scale=1_000_000,
                clinker_ratio=0.50,
                alternative_fuel_share=0.40
            )
        }
    
    def _init_market_data(self):
        """Initialize market data with realistic values"""
        # Global cement production (million tonnes)
        self.base_production = 4_200.0
        
        # Technology mix in 2025
        self.initial_mix = {
            'Conventional': 0.60,
            'Efficient': 0.35,
            'Alternative': 0.05
        }
        
        # Regional production shares
        self.regional_shares = {
            'Asia': 0.75,
            'Europe': 0.10,
            'North America': 0.08,
            'Other': 0.07
        }
        
        # Supplementary cementitious materials availability (million tonnes)
        self.scm_availability = {
            'Fly Ash': 800.0,
            'Slag': 400.0,
            'Calcined Clay': 200.0
        }
    
    def simulate_scenario(self, scenario: CementScenario) -> Dict[str, pd.DataFrame]:
        """
        Simulate cement industry transformation under given scenario
        
        Args:
            scenario: CementScenario configuration
            
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
    
    def _calculate_cost_evolution(self, scenario: CementScenario) -> pd.DataFrame:
        """Calculate technology cost evolution over time"""
        costs = pd.DataFrame(index=self.years)
        
        # Calculate carbon price evolution
        carbon_prices = scenario.carbon_price_start * (1 + scenario.carbon_price_growth) ** (self.years - self.start_year)
        
        # Calculate electricity cost evolution
        electricity_costs = scenario.electricity_cost_start * (1 + scenario.electricity_cost_growth) ** (self.years - self.start_year)
        
        # Calculate alternative fuel cost evolution
        alt_fuel_costs = scenario.alternative_fuel_cost_start * (1 + scenario.alternative_fuel_cost_growth) ** (self.years - self.start_year)
        
        # Calculate technology-specific costs
        for tech_name, tech in self.technologies.items():
            # Base cost reduction through learning
            base_capex = tech.capex_base * (1 - tech.learning_rate) ** (self.years - self.start_year)
            base_opex = tech.opex_base * (1 - tech.learning_rate) ** (self.years - self.start_year)
            
            # Add carbon cost
            carbon_cost = tech.carbon_intensity * carbon_prices
            
            # Add energy costs
            energy_cost = (
                (1 - tech.alternative_fuel_share) * 0.1 * electricity_costs +  # Electricity
                tech.alternative_fuel_share * 0.2 * alt_fuel_costs  # Alternative fuels
            )
            
            costs[f'{tech_name}_total_cost'] = base_capex + base_opex + carbon_cost + energy_cost
        
        return costs
    
    def _calculate_technology_adoption(
        self,
        scenario: CementScenario,
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
        production_growth = 0.015  # 1.5% annual growth
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
            # Calculate process emissions
            process_emissions = production[tech_name] * tech.carbon_intensity
            
            # Calculate fuel emissions
            fuel_emissions = production[tech_name] * 0.1 * (1 - tech.alternative_fuel_share)
            
            emissions[tech_name] = process_emissions + fuel_emissions
        
        # Calculate total emissions
        emissions['total'] = emissions.sum(axis=1)
        
        return emissions

# Example usage
if __name__ == "__main__":
    # Create a baseline scenario
    baseline_scenario = CementScenario(
        name="Baseline",
        carbon_price_start=80.0,
        carbon_price_growth=0.08,
        electricity_cost_start=60.0,
        electricity_cost_growth=0.02,
        alternative_fuel_cost_start=30.0,
        alternative_fuel_cost_growth=-0.03,
        clinker_substitution_rate=0.05,
        technology_adoption_rate=0.04
    )
    
    # Initialize and run simulation
    model = CementIndustryModel()
    results = model.simulate_scenario(baseline_scenario)
    
    # Print summary of results
    print("\nTechnology Mix Evolution:")
    print(results['technology_mix'].tail())
    
    print("\nEmissions Evolution (million tonnes CO2):")
    print(results['emissions']['total'].tail()) 