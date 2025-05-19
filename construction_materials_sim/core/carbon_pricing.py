"""
Carbon Pricing and Regulatory Mechanism Evolution Simulation (2025-2035)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CarbonPriceScenario:
    """Carbon price scenario configuration"""
    name: str
    eu_ets_base: float  # Base EU ETS price in EUR/tCO2
    eu_ets_growth_rate: float  # Annual growth rate
    cbam_implementation_year: int
    us_carbon_price_start: float
    us_carbon_price_growth: float
    asian_market_adoption_rate: float

class CarbonPricingModel:
    """Simulates carbon pricing evolution and its impact on trade flows"""
    
    def __init__(self, start_year: int = 2025, end_year: int = 2035):
        self.start_year = start_year
        self.end_year = end_year
        self.years = np.arange(start_year, end_year + 1)
        
        # Initialize realistic base data
        self._init_base_data()
    
    def _init_base_data(self):
        """Initialize base data with realistic values"""
        # Base carbon prices by region (EUR/tCO2)
        self.base_prices = {
            'EU': 80.0,  # Starting from 2025
            'US': 50.0,  # Starting from 2025
            'Asia': 30.0,  # Starting from 2025
            'Global South': 15.0  # Starting from 2025
        }
        
        # Trade flow data (million tonnes)
        self.base_trade_flows = {
            'EU_imports': 45.0,
            'US_imports': 35.0,
            'Asia_exports': 60.0,
            'Global_South_exports': 25.0
        }
        
        # Carbon intensity by region (tCO2/t product)
        self.carbon_intensity = {
            'EU': 1.8,
            'US': 2.0,
            'Asia': 2.3,
            'Global South': 2.5
        }
    
    def simulate_scenario(self, scenario: CarbonPriceScenario) -> Dict[str, pd.DataFrame]:
        """
        Simulate carbon pricing evolution and trade flow impacts
        
        Args:
            scenario: CarbonPriceScenario configuration
            
        Returns:
            Dictionary containing simulation results
        """
        # Calculate carbon price evolution
        eu_prices = self._calculate_eu_prices(scenario)
        us_prices = self._calculate_us_prices(scenario)
        asian_prices = self._calculate_asian_prices(scenario)
        
        # Calculate CBAM impact
        cbam_impact = self._calculate_cbam_impact(scenario, eu_prices)
        
        # Calculate trade flow shifts
        trade_shifts = self._calculate_trade_shifts(
            eu_prices, us_prices, asian_prices, cbam_impact
        )
        
        return {
            'carbon_prices': pd.DataFrame({
                'year': self.years,
                'eu_ets': eu_prices,
                'us_price': us_prices,
                'asian_price': asian_prices
            }),
            'trade_flows': trade_shifts,
            'cbam_impact': cbam_impact
        }
    
    def _calculate_eu_prices(self, scenario: CarbonPriceScenario) -> np.ndarray:
        """Calculate EU ETS price evolution"""
        return scenario.eu_ets_base * (1 + scenario.eu_ets_growth_rate) ** (self.years - self.start_year)
    
    def _calculate_us_prices(self, scenario: CarbonPriceScenario) -> np.ndarray:
        """Calculate US carbon price evolution"""
        return scenario.us_carbon_price_start * (1 + scenario.us_carbon_price_growth) ** (self.years - self.start_year)
    
    def _calculate_asian_prices(self, scenario: CarbonPriceScenario) -> np.ndarray:
        """Calculate Asian market carbon price evolution"""
        base = self.base_prices['Asia']
        return base * (1 + scenario.asian_market_adoption_rate) ** (self.years - self.start_year)
    
    def _calculate_cbam_impact(self, scenario: CarbonPriceScenario, eu_prices: np.ndarray) -> pd.DataFrame:
        """Calculate CBAM impact on trade flows"""
        cbam_years = self.years >= scenario.cbam_implementation_year
        impact = pd.DataFrame(index=self.years)
        
        # Calculate CBAM charges by region
        for region in ['Asia', 'Global South']:
            carbon_diff = self.carbon_intensity[region] - self.carbon_intensity['EU']
            cbam_charge = np.where(cbam_years, carbon_diff * eu_prices, 0)
            impact[f'{region}_cbam_charge'] = cbam_charge
        
        return impact
    
    def _calculate_trade_shifts(
        self,
        eu_prices: np.ndarray,
        us_prices: np.ndarray,
        asian_prices: np.ndarray,
        cbam_impact: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate trade flow shifts based on carbon price differentials"""
        trade_shifts = pd.DataFrame(index=self.years)
        
        # Calculate price differentials
        eu_us_diff = eu_prices - us_prices
        eu_asia_diff = eu_prices - asian_prices
        
        # Calculate trade flow adjustments
        trade_shifts['eu_us_shift'] = self.base_trade_flows['US_imports'] * (1 - 0.1 * eu_us_diff / 100)
        trade_shifts['eu_asia_shift'] = self.base_trade_flows['Asia_exports'] * (1 - 0.15 * eu_asia_diff / 100)
        
        # Apply CBAM impact
        trade_shifts['asia_cbam_impact'] = -0.2 * cbam_impact['Asia_cbam_charge']
        trade_shifts['global_south_cbam_impact'] = -0.2 * cbam_impact['Global_South_cbam_charge']
        
        return trade_shifts

# Example usage
if __name__ == "__main__":
    # Create a baseline scenario
    baseline_scenario = CarbonPriceScenario(
        name="Baseline",
        eu_ets_base=80.0,
        eu_ets_growth_rate=0.08,
        cbam_implementation_year=2026,
        us_carbon_price_start=50.0,
        us_carbon_price_growth=0.06,
        asian_market_adoption_rate=0.05
    )
    
    # Initialize and run simulation
    model = CarbonPricingModel()
    results = model.simulate_scenario(baseline_scenario)
    
    # Print summary of results
    print("\nCarbon Price Evolution (EUR/tCO2):")
    print(results['carbon_prices'].tail())
    
    print("\nTrade Flow Shifts (million tonnes):")
    print(results['trade_flows'].tail()) 