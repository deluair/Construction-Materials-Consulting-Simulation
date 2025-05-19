"""
Market Transformation and Customer Adoption Simulation (2025-2040)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .steel import SteelIndustryModel, SteelScenario
from .cement import CementIndustryModel, CementScenario
from .carbon_pricing import CarbonPricingModel, CarbonPriceScenario

@dataclass
class MarketScenario:
    """Market transformation scenario configuration"""
    name: str
    # Carbon pricing parameters
    carbon_price_start: float
    carbon_price_growth: float
    # Steel industry parameters
    steel_hydrogen_cost_start: float
    steel_hydrogen_cost_growth: float
    steel_electricity_cost_start: float
    steel_electricity_cost_growth: float
    # Cement industry parameters
    cement_electricity_cost_start: float
    cement_electricity_cost_growth: float
    cement_alternative_fuel_cost_start: float
    cement_alternative_fuel_cost_growth: float
    # Market adoption parameters
    green_premium_start: float  # Percentage premium for green products
    green_premium_growth: float
    customer_adoption_rate: float
    regulatory_pressure_growth: float

class MarketTransformationModel:
    """Simulates market transformation and customer adoption patterns"""
    
    def __init__(self, start_year: int = 2025, end_year: int = 2040):
        self.start_year = start_year
        self.end_year = end_year
        self.years = np.arange(start_year, end_year + 1)
        
        # Initialize sub-models
        self.carbon_model = CarbonPricingModel(start_year, end_year)
        self.steel_model = SteelIndustryModel(start_year, end_year)
        self.cement_model = CementIndustryModel(start_year, end_year)
        
        # Initialize market data
        self._init_market_data()
    
    def _init_market_data(self):
        """Initialize market data with realistic values"""
        # Customer segments
        self.customer_segments = {
            'Public Infrastructure': {
                'share': 0.25,
                'green_premium_willingness': 0.15,
                'regulatory_sensitivity': 0.9
            },
            'Commercial Construction': {
                'share': 0.35,
                'green_premium_willingness': 0.10,
                'regulatory_sensitivity': 0.7
            },
            'Residential Construction': {
                'share': 0.20,
                'green_premium_willingness': 0.05,
                'regulatory_sensitivity': 0.5
            },
            'Industrial': {
                'share': 0.20,
                'green_premium_willingness': 0.08,
                'regulatory_sensitivity': 0.6
            }
        }
        
        # Regional market shares
        self.regional_shares = {
            'Europe': 0.25,
            'North America': 0.20,
            'Asia': 0.40,
            'Other': 0.15
        }
        
        # Initial green product adoption
        self.initial_green_adoption = 0.05  # 5% initial adoption
    
    def simulate_scenario(self, scenario: MarketScenario) -> Dict[str, pd.DataFrame]:
        """
        Simulate market transformation under given scenario
        
        Args:
            scenario: MarketScenario configuration
            
        Returns:
            Dictionary containing simulation results
        """
        # Run sub-model simulations
        carbon_results = self._run_carbon_simulation(scenario)
        steel_results = self._run_steel_simulation(scenario)
        cement_results = self._run_cement_simulation(scenario)
        
        # Calculate market adoption
        adoption = self._calculate_market_adoption(scenario)
        
        # Calculate green premium evolution
        premium = self._calculate_green_premium(scenario)
        
        # Calculate market value evolution
        market_value = self._calculate_market_value(adoption, premium)
        
        return {
            'carbon_pricing': carbon_results,
            'steel_industry': steel_results,
            'cement_industry': cement_results,
            'market_adoption': adoption,
            'green_premium': premium,
            'market_value': market_value
        }
    
    def _run_carbon_simulation(self, scenario: MarketScenario) -> Dict[str, pd.DataFrame]:
        """Run carbon pricing simulation"""
        carbon_scenario = CarbonPriceScenario(
            name=scenario.name,
            eu_ets_base=scenario.carbon_price_start,
            eu_ets_growth_rate=scenario.carbon_price_growth,
            cbam_implementation_year=2026,
            us_carbon_price_start=scenario.carbon_price_start * 0.8,
            us_carbon_price_growth=scenario.carbon_price_growth,
            asian_market_adoption_rate=0.05
        )
        return self.carbon_model.simulate_scenario(carbon_scenario)
    
    def _run_steel_simulation(self, scenario: MarketScenario) -> Dict[str, pd.DataFrame]:
        """Run steel industry simulation"""
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
        return self.steel_model.simulate_scenario(steel_scenario)
    
    def _run_cement_simulation(self, scenario: MarketScenario) -> Dict[str, pd.DataFrame]:
        """Run cement industry simulation"""
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
        return self.cement_model.simulate_scenario(cement_scenario)
    
    def _calculate_market_adoption(self, scenario: MarketScenario) -> pd.DataFrame:
        """Calculate market adoption of green products by segment"""
        adoption = pd.DataFrame(index=self.years)
        
        # Calculate regulatory pressure evolution
        regulatory_pressure = (1 + scenario.regulatory_pressure_growth) ** (self.years - self.start_year)
        
        # Calculate adoption by segment
        for segment, params in self.customer_segments.items():
            # Initial adoption
            adoption[segment] = self.initial_green_adoption
            
            # Calculate adoption evolution
            for year in self.years[1:]:
                prev_year = year - 1
                
                # Calculate adoption drivers
                regulatory_driver = params['regulatory_sensitivity'] * regulatory_pressure[year - self.start_year]
                market_driver = scenario.customer_adoption_rate
                
                # Calculate new adoption rate
                adoption.loc[year, segment] = min(
                    1.0,
                    adoption.loc[prev_year, segment] + 
                    (1 - adoption.loc[prev_year, segment]) * (regulatory_driver + market_driver)
                )
        
        return adoption
    
    def _calculate_green_premium(self, scenario: MarketScenario) -> pd.DataFrame:
        """Calculate green premium evolution"""
        premium = pd.DataFrame(index=self.years)
        
        # Calculate base premium evolution
        base_premium = scenario.green_premium_start * (1 + scenario.green_premium_growth) ** (self.years - self.start_year)
        
        # Calculate premium by segment
        for segment, params in self.customer_segments.items():
            premium[segment] = base_premium * params['green_premium_willingness']
        
        return premium
    
    def _calculate_market_value(
        self,
        adoption: pd.DataFrame,
        premium: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate market value evolution"""
        market_value = pd.DataFrame(index=self.years)
        
        # Base market value (billion EUR)
        base_value = 1000.0  # Starting from 2025
        market_growth = 0.03  # 3% annual growth
        
        # Calculate total market value
        total_value = base_value * (1 + market_growth) ** (self.years - self.start_year)
        
        # Calculate value by segment
        for segment in self.customer_segments:
            segment_share = self.customer_segments[segment]['share']
            market_value[segment] = total_value * segment_share * (1 + premium[segment])
        
        return market_value

# Example usage
if __name__ == "__main__":
    # Create a baseline scenario
    baseline_scenario = MarketScenario(
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
    
    # Initialize and run simulation
    model = MarketTransformationModel()
    results = model.simulate_scenario(baseline_scenario)
    
    # Print summary of results
    print("\nMarket Adoption by Segment:")
    print(results['market_adoption'].tail())
    
    print("\nGreen Premium by Segment:")
    print(results['green_premium'].tail())
    
    print("\nMarket Value by Segment (billion EUR):")
    print(results['market_value'].tail()) 