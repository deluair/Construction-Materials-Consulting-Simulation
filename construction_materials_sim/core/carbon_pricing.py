"""
Carbon Pricing and Regulatory Mechanism Evolution Simulation (2025-2040)
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
    global_south_adoption_rate: float = 0.03  # Added parameter

class CarbonPricingModel:
    """Simulates carbon pricing evolution and its impact on trade flows"""
    
    def __init__(self, start_year: int = 2025, end_year: int = 2040):  # Updated end year
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
        
        # Regional market characteristics
        self.regional_markets = {
            'EU': {
                'regulatory_pressure': 0.9,
                'market_maturity': 0.8,
                'price_sensitivity': 0.7
            },
            'US': {
                'regulatory_pressure': 0.7,
                'market_maturity': 0.6,
                'price_sensitivity': 0.8
            },
            'Asia': {
                'regulatory_pressure': 0.5,
                'market_maturity': 0.4,
                'price_sensitivity': 0.9
            },
            'Global South': {
                'regulatory_pressure': 0.3,
                'market_maturity': 0.2,
                'price_sensitivity': 0.95
            }
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
        global_south_prices = self._calculate_global_south_prices(scenario)
        
        # Calculate CBAM impact
        cbam_impact = self._calculate_cbam_impact(scenario, eu_prices)
        
        # Calculate trade flow shifts
        trade_shifts = self._calculate_trade_shifts(
            eu_prices, us_prices, asian_prices, global_south_prices, cbam_impact
        )
        
        # Calculate regional market evolution
        market_evolution = self._calculate_market_evolution(
            eu_prices, us_prices, asian_prices, global_south_prices
        )
        
        return {
            'carbon_prices': pd.DataFrame({
                'year': self.years,
                'eu_ets': eu_prices,
                'us_price': us_prices,
                'asian_price': asian_prices,
                'global_south_price': global_south_prices
            }),
            'trade_flows': trade_shifts,
            'cbam_impact': cbam_impact,
            'market_evolution': market_evolution
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
    
    def _calculate_global_south_prices(self, scenario: CarbonPriceScenario) -> np.ndarray:
        """Calculate Global South carbon price evolution"""
        base = self.base_prices['Global South']
        return base * (1 + scenario.global_south_adoption_rate) ** (self.years - self.start_year)
    
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
        global_south_prices: np.ndarray,
        cbam_impact: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate trade flow shifts based on carbon price differentials"""
        trade_shifts = pd.DataFrame(index=self.years)
        
        # Calculate price differentials
        eu_us_diff = eu_prices - us_prices
        eu_asia_diff = eu_prices - asian_prices
        eu_global_south_diff = eu_prices - global_south_prices
        
        # Calculate trade flow adjustments
        trade_shifts['eu_us_shift'] = self.base_trade_flows['US_imports'] * (1 - 0.1 * eu_us_diff / 100)
        trade_shifts['eu_asia_shift'] = self.base_trade_flows['Asia_exports'] * (1 - 0.15 * eu_asia_diff / 100)
        trade_shifts['eu_global_south_shift'] = self.base_trade_flows['Global_South_exports'] * (1 - 0.15 * eu_global_south_diff / 100)
        
        # Apply CBAM impact
        trade_shifts['asia_cbam_impact'] = -0.2 * cbam_impact['Asia_cbam_charge']
        trade_shifts['global_south_cbam_impact'] = -0.2 * cbam_impact['Global_South_cbam_charge']
        
        return trade_shifts
    
    def _calculate_market_evolution(
        self,
        eu_prices: np.ndarray,
        us_prices: np.ndarray,
        asian_prices: np.ndarray,
        global_south_prices: np.ndarray
    ) -> pd.DataFrame:
        """Calculate regional market evolution"""
        market_evolution = pd.DataFrame(index=self.years)
        
        # Calculate market evolution for each region
        for region, characteristics in self.regional_markets.items():
            # Get price evolution for the region
            if region == 'EU':
                prices = eu_prices
            elif region == 'US':
                prices = us_prices
            elif region == 'Asia':
                prices = asian_prices
            else:
                prices = global_south_prices
            
            # Calculate market maturity evolution
            maturity = characteristics['market_maturity'] * (1 + 0.02) ** (self.years - self.start_year)
            maturity = np.minimum(maturity, 1.0)  # Cap at 1.0
            
            # Calculate regulatory pressure evolution
            pressure = characteristics['regulatory_pressure'] * (1 + 0.03) ** (self.years - self.start_year)
            pressure = np.minimum(pressure, 1.0)  # Cap at 1.0
            
            # Calculate price sensitivity evolution
            sensitivity = characteristics['price_sensitivity'] * (1 - 0.01) ** (self.years - self.start_year)
            sensitivity = np.maximum(sensitivity, 0.5)  # Floor at 0.5
            
            # Store results
            market_evolution[f'{region}_maturity'] = maturity
            market_evolution[f'{region}_pressure'] = pressure
            market_evolution[f'{region}_sensitivity'] = sensitivity
        
        return market_evolution

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
        asian_market_adoption_rate=0.05,
        global_south_adoption_rate=0.03
    )
    
    # Initialize and run simulation
    model = CarbonPricingModel()
    results = model.simulate_scenario(baseline_scenario)
    
    # Print summary of results
    print("\nCarbon Price Evolution (EUR/tCO2):")
    print(results['carbon_prices'].tail())
    
    print("\nTrade Flow Shifts (million tonnes):")
    print(results['trade_flows'].tail())
    
    print("\nMarket Evolution:")
    print(results['market_evolution'].tail()) 