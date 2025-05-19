"""
Interactive Dashboard for Construction Materials Simulation Results
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List

from ..core.market import MarketTransformationModel, MarketScenario
from ..core.steel import SteelIndustryModel, SteelScenario
from ..core.cement import CementIndustryModel, CementScenario
from ..core.carbon_pricing import CarbonPricingModel, CarbonPriceScenario
from .analysis import SimulationAnalysis

class SimulationDashboard:
    """Interactive dashboard for simulation results visualization"""
    
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Construction Materials Transformation Dashboard"),
                    html.P("Interactive visualization of industry transformation scenarios (2025-2040)")
                ])
            ]),
            
            dbc.Tabs([
                dbc.Tab(label="Overview", children=[
                    dbc.Row([
                        dbc.Col([
                            html.H3("Scenario Configuration"),
                            dbc.Card([
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label("Carbon Price Start (EUR/tCO2)"),
                                            dcc.Input(
                                                id="carbon-price-start",
                                                type="number",
                                                value=80.0,
                                                min=0,
                                                max=200
                                            )
                                        ]),
                                        dbc.Col([
                                            html.Label("Carbon Price Growth (%)"),
                                            dcc.Input(
                                                id="carbon-price-growth",
                                                type="number",
                                                value=8.0,
                                                min=0,
                                                max=20
                                            )
                                        ])
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label("Green Premium Start (%)"),
                                            dcc.Input(
                                                id="green-premium-start",
                                                type="number",
                                                value=15.0,
                                                min=0,
                                                max=50
                                            )
                                        ]),
                                        dbc.Col([
                                            html.Label("Customer Adoption Rate (%)"),
                                            dcc.Input(
                                                id="customer-adoption-rate",
                                                type="number",
                                                value=8.0,
                                                min=0,
                                                max=20
                                            )
                                        ])
                                    ])
                                ])
                            ])
                        ], width=4),
                        
                        dbc.Col([
                            html.H3("Market Adoption"),
                            dcc.Graph(id="market-adoption-chart")
                        ], width=8)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H3("Emissions Evolution"),
                            dcc.Graph(id="emissions-chart")
                        ], width=6),
                        
                        dbc.Col([
                            html.H3("Market Value"),
                            dcc.Graph(id="market-value-chart")
                        ], width=6)
                    ])
                ]),
                
                dbc.Tab(label="Technology Analysis", children=[
                    dbc.Row([
                        dbc.Col([
                            html.H3("Technology Mix"),
                            dcc.Graph(id="technology-mix-chart")
                        ], width=12)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H3("Technology Transitions"),
                            dcc.Graph(id="technology-transition-chart")
                        ], width=12)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H3("Cost Analysis"),
                            dcc.Graph(id="cost-analysis-chart")
                        ], width=12)
                    ])
                ]),
                
                dbc.Tab(label="Regional Analysis", children=[
                    dbc.Row([
                        dbc.Col([
                            html.H3("Regional Market Performance"),
                            dcc.Graph(id="regional-comparison-chart")
                        ], width=12)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H3("Regional Emissions"),
                            dcc.Graph(id="regional-emissions-chart")
                        ], width=6),
                        
                        dbc.Col([
                            html.H3("Regional Adoption"),
                            dcc.Graph(id="regional-adoption-chart")
                        ], width=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H3("Regional Market Evolution"),
                            dcc.Graph(id="regional-evolution-chart")
                        ], width=12)
                    ])
                ]),
                
                dbc.Tab(label="Analysis", children=[
                    dbc.Row([
                        dbc.Col([
                            html.H3("Emissions Analysis"),
                            dcc.Graph(id="emissions-heatmap")
                        ], width=6),
                        
                        dbc.Col([
                            html.H3("Adoption Forecast"),
                            dcc.Graph(id="adoption-forecast-chart")
                        ], width=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H3("Sensitivity Analysis"),
                            dcc.Graph(id="sensitivity-analysis-chart")
                        ], width=12)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H3("Detailed Summary Report"),
                            html.Div(id="detailed-summary-report")
                        ], width=12)
                    ])
                ])
            ])
        ], fluid=True)
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        @self.app.callback(
            [
                Output("market-adoption-chart", "figure"),
                Output("emissions-chart", "figure"),
                Output("market-value-chart", "figure"),
                Output("technology-mix-chart", "figure"),
                Output("technology-transition-chart", "figure"),
                Output("cost-analysis-chart", "figure"),
                Output("regional-comparison-chart", "figure"),
                Output("regional-emissions-chart", "figure"),
                Output("regional-adoption-chart", "figure"),
                Output("regional-evolution-chart", "figure"),
                Output("emissions-heatmap", "figure"),
                Output("adoption-forecast-chart", "figure"),
                Output("sensitivity-analysis-chart", "figure"),
                Output("detailed-summary-report", "children")
            ],
            [
                Input("carbon-price-start", "value"),
                Input("carbon-price-growth", "value"),
                Input("green-premium-start", "value"),
                Input("customer-adoption-rate", "value")
            ]
        )
        def update_charts(
            carbon_price_start,
            carbon_price_growth,
            green_premium_start,
            customer_adoption_rate
        ):
            # Create and run simulation
            scenario = MarketScenario(
                name="Interactive",
                carbon_price_start=carbon_price_start,
                carbon_price_growth=carbon_price_growth / 100,
                steel_hydrogen_cost_start=4.0,
                steel_hydrogen_cost_growth=-0.05,
                steel_electricity_cost_start=60.0,
                steel_electricity_cost_growth=0.02,
                cement_electricity_cost_start=60.0,
                cement_electricity_cost_growth=0.02,
                cement_alternative_fuel_cost_start=30.0,
                cement_alternative_fuel_cost_growth=-0.03,
                green_premium_start=green_premium_start / 100,
                green_premium_growth=0.05,
                customer_adoption_rate=customer_adoption_rate / 100,
                regulatory_pressure_growth=0.10
            )
            
            model = MarketTransformationModel()
            results = model.simulate_scenario(scenario)
            
            # Create analysis object
            analysis = SimulationAnalysis(results)
            
            # Generate all visualizations
            adoption_fig = px.line(
                results['market_adoption'].reset_index(),
                x='index',
                y=results['market_adoption'].columns,
                title="Market Adoption by Segment and Region",
                labels={'index': 'Year', 'value': 'Adoption Rate'}
            )
            
            emissions_fig = px.line(
                results['steel_industry']['emissions']['total'].reset_index(),
                x='index',
                y='total',
                title="Steel Industry Emissions",
                labels={'index': 'Year', 'total': 'Emissions (MtCO2)'}
            )
            
            value_fig = px.line(
                results['market_value'].reset_index(),
                x='index',
                y=results['market_value'].columns,
                title="Market Value by Segment and Region",
                labels={'index': 'Year', 'value': 'Value (billion EUR)'}
            )
            
            mix_fig = px.area(
                results['steel_industry']['technology_mix'].reset_index(),
                x='index',
                y=results['steel_industry']['technology_mix'].columns,
                title="Steel Technology Mix",
                labels={'index': 'Year', 'value': 'Share'}
            )
            
            # Generate analysis visualizations
            transition_fig = analysis.create_technology_transition_plot()
            cost_fig = analysis.create_cost_analysis()
            regional_fig = analysis.create_regional_comparison()
            heatmap_fig = analysis.create_emissions_heatmap()
            forecast_fig = analysis.create_adoption_forecast()
            
            # Generate regional evolution visualization
            evolution_fig = px.line(
                results['regional_evolution'].reset_index(),
                x='index',
                y=results['regional_evolution'].columns,
                title="Regional Market Evolution",
                labels={'index': 'Year', 'value': 'Evolution Metric'}
            )
            
            # Generate sensitivity analysis
            sensitivity_variations = {
                'carbon_price_growth': [0.05, 0.08, 0.12],
                'customer_adoption_rate': [0.05, 0.08, 0.12],
                'green_premium_start': [0.10, 0.15, 0.20]
            }
            sensitivity_results = analysis.perform_sensitivity_analysis(scenario, sensitivity_variations)
            
            sensitivity_fig = go.Figure()
            for param, results_df in sensitivity_results.items():
                sensitivity_fig.add_trace(go.Scatter(
                    x=results_df['parameter_value'],
                    y=results_df['market_value_2040'],
                    name=param,
                    mode='lines+markers'
                ))
            
            sensitivity_fig.update_layout(
                title="Sensitivity Analysis",
                xaxis_title="Parameter Value",
                yaxis_title="Market Value in 2040 (billion EUR)",
                showlegend=True
            )
            
            # Generate detailed summary report
            summary = analysis.generate_detailed_report()
            summary_html = [
                html.H4("Emissions Reduction (2040)"),
                html.P(f"Total: {summary['emissions']['total_reduction_2040']:.1f}%"),
                html.P(f"Steel: {summary['emissions']['steel_reduction_2040']:.1f}%"),
                html.P(f"Cement: {summary['emissions']['cement_reduction_2040']:.1f}%"),
                
                html.H4("Market Metrics (2040)"),
                html.P(f"Total Value: {summary['market']['total_value_2040']:.1f} billion EUR"),
                html.P(f"Average Adoption: {summary['market']['avg_adoption_2040']:.1%}"),
                html.P(f"Value Growth Rate: {summary['market']['value_growth_rate']:.1f}%"),
                html.P(f"Adoption Growth Rate: {summary['market']['adoption_growth_rate']:.1f}%"),
                
                html.H4("Technology Transitions"),
                html.P(f"Steel Peak Transition: {summary['transitions']['steel_peak_transition']:.1%}"),
                html.P(f"Cement Peak Transition: {summary['transitions']['cement_peak_transition']:.1%}"),
                html.P(f"Steel Transition Year: {summary['transitions']['steel_transition_year']}"),
                html.P(f"Cement Transition Year: {summary['transitions']['cement_transition_year']}"),
                
                html.H4("Regional Analysis"),
                *[
                    html.Div([
                        html.H5(region),
                        html.P(f"Market Value: {data['market_value_2040']:.1f} billion EUR"),
                        html.P(f"Adoption Rate: {data['adoption_rate_2040']:.1%}"),
                        html.P(f"Value Growth: {data['value_growth_rate']:.1f}%"),
                        html.P(f"Adoption Growth: {data['adoption_growth_rate']:.1f}%")
                    ])
                    for region, data in summary['regional'].items()
                ]
            ]
            
            return (
                adoption_fig,
                emissions_fig,
                value_fig,
                mix_fig,
                transition_fig,
                cost_fig,
                regional_fig,
                heatmap_fig,
                forecast_fig,
                evolution_fig,
                sensitivity_fig,
                summary_html
            )
    
    def run_server(self, debug: bool = True, port: int = 8050):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port)

# Example usage
if __name__ == "__main__":
    dashboard = SimulationDashboard()
    dashboard.run_server() 