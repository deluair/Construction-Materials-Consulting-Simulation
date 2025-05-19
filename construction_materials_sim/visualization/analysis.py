"""
Advanced Analysis and Visualization Tools for Construction Materials Simulation
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
from scipy import stats

class SimulationAnalysis:
    """Advanced analysis tools for simulation results"""
    
    def __init__(self, results: Dict[str, pd.DataFrame]):
        self.results = results
    
    def calculate_emissions_reduction(self) -> pd.DataFrame:
        """Calculate emissions reduction metrics"""
        steel_emissions = self.results['steel_industry']['emissions']['total']
        cement_emissions = self.results['cement_industry']['emissions']['total']
        
        total_emissions = steel_emissions + cement_emissions
        baseline = total_emissions.iloc[0]
        
        reduction = pd.DataFrame({
            'year': total_emissions.index,
            'total_emissions': total_emissions,
            'reduction_pct': (baseline - total_emissions) / baseline * 100,
            'steel_emissions': steel_emissions,
            'cement_emissions': cement_emissions
        })
        
        return reduction
    
    def calculate_market_metrics(self) -> pd.DataFrame:
        """Calculate key market metrics"""
        market_value = self.results['market_value']
        market_adoption = self.results['market_adoption']
        
        metrics = pd.DataFrame({
            'year': market_value.index,
            'total_value': market_value.sum(axis=1),
            'avg_adoption': market_adoption.mean(axis=1),
            'value_growth': market_value.sum(axis=1).pct_change() * 100,
            'adoption_growth': market_adoption.mean(axis=1).pct_change() * 100
        })
        
        return metrics
    
    def create_emissions_heatmap(self) -> go.Figure:
        """Create emissions heatmap by region and technology"""
        steel_emissions = self.results['steel_industry']['emissions']
        cement_emissions = self.results['cement_industry']['emissions']
        
        # Combine emissions data
        emissions_data = pd.DataFrame({
            'year': steel_emissions.index,
            'steel_bf_bof': steel_emissions['BF-BOF'],
            'steel_eaf': steel_emissions['EAF'],
            'steel_h2_dri': steel_emissions['H2-DRI'],
            'cement_conventional': cement_emissions['Conventional'],
            'cement_efficient': cement_emissions['Efficient'],
            'cement_alternative': cement_emissions['Alternative']
        })
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=emissions_data.corr(),
            x=emissions_data.columns,
            y=emissions_data.columns,
            colorscale='RdBu'
        ))
        
        fig.update_layout(
            title='Emissions Correlation Heatmap',
            xaxis_title='Technology',
            yaxis_title='Technology'
        )
        
        return fig
    
    def create_adoption_forecast(self) -> go.Figure:
        """Create adoption forecast with confidence intervals"""
        adoption = self.results['market_adoption']
        
        # Calculate trend and confidence intervals
        x = np.arange(len(adoption))
        y = adoption.mean(axis=1)
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        line = slope * x + intercept
        
        # Calculate confidence intervals
        y_err = std_err * np.sqrt(1/len(x) + (x - np.mean(x))**2 / np.sum((x - np.mean(x))**2))
        
        fig = go.Figure()
        
        # Add actual adoption
        fig.add_trace(go.Scatter(
            x=adoption.index,
            y=y,
            name='Actual Adoption',
            line=dict(color='blue')
        ))
        
        # Add trend line
        fig.add_trace(go.Scatter(
            x=adoption.index,
            y=line,
            name='Trend',
            line=dict(color='red', dash='dash')
        ))
        
        # Add confidence intervals
        fig.add_trace(go.Scatter(
            x=adoption.index,
            y=line + 1.96 * y_err,
            fill=None,
            mode='lines',
            line=dict(color='rgba(0,100,80,0.2)'),
            name='95% Confidence Interval'
        ))
        
        fig.add_trace(go.Scatter(
            x=adoption.index,
            y=line - 1.96 * y_err,
            fill='tonexty',
            mode='lines',
            line=dict(color='rgba(0,100,80,0.2)'),
            name='95% Confidence Interval'
        ))
        
        fig.update_layout(
            title='Market Adoption Forecast',
            xaxis_title='Year',
            yaxis_title='Adoption Rate',
            showlegend=True
        )
        
        return fig
    
    def create_cost_analysis(self) -> go.Figure:
        """Create cost analysis visualization"""
        steel_costs = self.results['steel_industry']['costs']
        cement_costs = self.results['cement_industry']['costs']
        
        # Combine cost data
        costs = pd.DataFrame({
            'year': steel_costs.index,
            'steel_bf_bof': steel_costs['BF-BOF_total_cost'],
            'steel_eaf': steel_costs['EAF_total_cost'],
            'steel_h2_dri': steel_costs['H2-DRI_total_cost'],
            'cement_conventional': cement_costs['Conventional_total_cost'],
            'cement_efficient': cement_costs['Efficient_total_cost'],
            'cement_alternative': cement_costs['Alternative_total_cost']
        })
        
        # Create cost comparison
        fig = go.Figure()
        
        for col in costs.columns[1:]:
            fig.add_trace(go.Scatter(
                x=costs['year'],
                y=costs[col],
                name=col.replace('_', ' ').title(),
                mode='lines'
            ))
        
        fig.update_layout(
            title='Technology Cost Evolution',
            xaxis_title='Year',
            yaxis_title='Cost (EUR/tonne)',
            showlegend=True
        )
        
        return fig
    
    def generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report"""
        emissions_reduction = self.calculate_emissions_reduction()
        market_metrics = self.calculate_market_metrics()
        
        summary = {
            'emissions': {
                'total_reduction_2040': emissions_reduction['reduction_pct'].iloc[-1],
                'steel_reduction_2040': (emissions_reduction['steel_emissions'].iloc[0] - 
                                       emissions_reduction['steel_emissions'].iloc[-1]) / 
                                       emissions_reduction['steel_emissions'].iloc[0] * 100,
                'cement_reduction_2040': (emissions_reduction['cement_emissions'].iloc[0] - 
                                        emissions_reduction['cement_emissions'].iloc[-1]) / 
                                        emissions_reduction['cement_emissions'].iloc[0] * 100
            },
            'market': {
                'total_value_2040': market_metrics['total_value'].iloc[-1],
                'avg_adoption_2040': market_metrics['avg_adoption'].iloc[-1],
                'value_growth_rate': market_metrics['value_growth'].mean(),
                'adoption_growth_rate': market_metrics['adoption_growth'].mean()
            }
        }
        
        return summary
    
    def analyze_technology_transition(self) -> pd.DataFrame:
        """Analyze technology transition patterns and tipping points"""
        steel_mix = self.results['steel_industry']['technology_mix']
        cement_mix = self.results['cement_industry']['technology_mix']
        
        # Calculate transition rates
        steel_transition = pd.DataFrame({
            'year': steel_mix.index,
            'bf_bof_to_eaf': steel_mix['EAF'].pct_change(),
            'eaf_to_h2_dri': steel_mix['H2-DRI'].pct_change(),
            'total_transition': steel_mix.sum(axis=1).pct_change()
        })
        
        cement_transition = pd.DataFrame({
            'year': cement_mix.index,
            'conventional_to_efficient': cement_mix['Efficient'].pct_change(),
            'efficient_to_alternative': cement_mix['Alternative'].pct_change(),
            'total_transition': cement_mix.sum(axis=1).pct_change()
        })
        
        return {
            'steel': steel_transition,
            'cement': cement_transition
        }
    
    def calculate_regional_metrics(self) -> Dict[str, pd.DataFrame]:
        """Calculate region-specific performance metrics"""
        market_value = self.results['market_value']
        market_adoption = self.results['market_adoption']
        
        regional_metrics = {}
        for region in ['Europe', 'North America', 'Asia', 'Other']:
            metrics = pd.DataFrame({
                'year': market_value.index,
                'market_value': market_value[region],
                'adoption_rate': market_adoption[region],
                'value_growth': market_value[region].pct_change() * 100,
                'adoption_growth': market_adoption[region].pct_change() * 100
            })
            regional_metrics[region] = metrics
        
        return regional_metrics
    
    def perform_sensitivity_analysis(self, base_scenario: Dict, variations: Dict[str, List[float]]) -> Dict[str, pd.DataFrame]:
        """Perform sensitivity analysis on key parameters"""
        sensitivity_results = {}
        
        for param, values in variations.items():
            results = []
            for value in values:
                # Create modified scenario
                modified_scenario = base_scenario.copy()
                modified_scenario[param] = value
                
                # Run simulation with modified scenario
                model = MarketTransformationModel()
                scenario = MarketScenario(**modified_scenario)
                result = model.simulate_scenario(scenario)
                
                # Calculate key metrics
                metrics = {
                    'parameter_value': value,
                    'total_emissions_2040': result['steel_industry']['emissions']['total'].iloc[-1] +
                                         result['cement_industry']['emissions']['total'].iloc[-1],
                    'market_value_2040': result['market_value'].sum(axis=1).iloc[-1],
                    'adoption_rate_2040': result['market_adoption'].mean(axis=1).iloc[-1]
                }
                results.append(metrics)
            
            sensitivity_results[param] = pd.DataFrame(results)
        
        return sensitivity_results
    
    def create_regional_comparison(self) -> go.Figure:
        """Create regional comparison visualization"""
        regional_metrics = self.calculate_regional_metrics()
        
        fig = go.Figure()
        
        for region, metrics in regional_metrics.items():
            fig.add_trace(go.Scatter(
                x=metrics['year'],
                y=metrics['market_value'],
                name=f'{region} Market Value',
                mode='lines'
            ))
            
            fig.add_trace(go.Scatter(
                x=metrics['year'],
                y=metrics['adoption_rate'] * 1000,  # Scale for better visualization
                name=f'{region} Adoption Rate',
                mode='lines',
                line=dict(dash='dash')
            ))
        
        fig.update_layout(
            title='Regional Market Performance Comparison',
            xaxis_title='Year',
            yaxis_title='Value (billion EUR) / Adoption Rate (scaled)',
            showlegend=True
        )
        
        return fig
    
    def create_technology_transition_plot(self) -> go.Figure:
        """Create technology transition visualization"""
        transitions = self.analyze_technology_transition()
        
        fig = go.Figure()
        
        # Add steel transitions
        fig.add_trace(go.Scatter(
            x=transitions['steel']['year'],
            y=transitions['steel']['bf_bof_to_eaf'] * 100,
            name='BF-BOF to EAF',
            mode='lines'
        ))
        
        fig.add_trace(go.Scatter(
            x=transitions['steel']['year'],
            y=transitions['steel']['eaf_to_h2_dri'] * 100,
            name='EAF to H2-DRI',
            mode='lines'
        ))
        
        # Add cement transitions
        fig.add_trace(go.Scatter(
            x=transitions['cement']['year'],
            y=transitions['cement']['conventional_to_efficient'] * 100,
            name='Conventional to Efficient',
            mode='lines'
        ))
        
        fig.add_trace(go.Scatter(
            x=transitions['cement']['year'],
            y=transitions['cement']['efficient_to_alternative'] * 100,
            name='Efficient to Alternative',
            mode='lines'
        ))
        
        fig.update_layout(
            title='Technology Transition Rates',
            xaxis_title='Year',
            yaxis_title='Transition Rate (%)',
            showlegend=True
        )
        
        return fig
    
    def generate_detailed_report(self) -> Dict:
        """Generate detailed analysis report"""
        summary = self.generate_summary_report()
        transitions = self.analyze_technology_transition()
        regional_metrics = self.calculate_regional_metrics()
        
        # Add transition analysis
        summary['transitions'] = {
            'steel_peak_transition': transitions['steel']['total_transition'].max(),
            'cement_peak_transition': transitions['cement']['total_transition'].max(),
            'steel_transition_year': transitions['steel']['total_transition'].idxmax(),
            'cement_transition_year': transitions['cement']['total_transition'].idxmax()
        }
        
        # Add regional analysis
        summary['regional'] = {
            region: {
                'market_value_2040': metrics['market_value'].iloc[-1],
                'adoption_rate_2040': metrics['adoption_rate'].iloc[-1],
                'value_growth_rate': metrics['value_growth'].mean(),
                'adoption_growth_rate': metrics['adoption_growth'].mean()
            }
            for region, metrics in regional_metrics.items()
        }
        
        return summary 