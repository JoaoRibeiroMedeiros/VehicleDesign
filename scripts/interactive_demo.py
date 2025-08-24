#!/usr/bin/env python3
"""
Interactive Aircraft Design Demo Script

This script creates interactive visualizations that open in your web browser
using Plotly for dynamic exploration of aircraft performance.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from src import (
    create_sample_aircraft, FlightEnvelope, PerformanceAnalyzer,
    create_interactive_dashboard
)


def create_interactive_comparison():
    """Create an interactive comparison of all three aircraft types"""
    
    aircraft_list = create_sample_aircraft()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Drag Polar Comparison', 'L/D Ratio vs Angle of Attack', 
                       'Performance Summary', 'V-n Diagram Comparison'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    colors = ['blue', 'red', 'green']
    
    # Drag polar comparison
    for i, aircraft in enumerate(aircraft_list):
        angles = np.linspace(-5, 20, 100)
        cl_values = []
        cd_values = []
        
        for angle in angles:
            cl = aircraft.calculate_lift_coefficient(angle)
            cd = aircraft.calculate_drag_coefficient(cl)
            cl_values.append(cl)
            cd_values.append(cd)
        
        fig.add_trace(
            go.Scatter(x=cd_values, y=cl_values, mode='lines', 
                      name=f'{aircraft.name} - Drag Polar',
                      line=dict(color=colors[i], width=3)),
            row=1, col=1
        )
    
    # L/D ratio comparison
    for i, aircraft in enumerate(aircraft_list):
        angles = np.linspace(-5, 20, 100)
        ld_ratios = []
        
        for angle in angles:
            ld = aircraft.calculate_lift_drag_ratio(angle)
            ld_ratios.append(ld)
        
        fig.add_trace(
            go.Scatter(x=angles, y=ld_ratios, mode='lines',
                      name=f'{aircraft.name} - L/D',
                      line=dict(color=colors[i], width=3)),
            row=1, col=2
        )
    
    # Performance summary bar chart
    aircraft_names = [aircraft.name for aircraft in aircraft_list]
    wing_loadings = [aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area 
                    for aircraft in aircraft_list]
    aspect_ratios = [aircraft.geometry.aspect_ratio for aircraft in aircraft_list]
    
    fig.add_trace(
        go.Bar(x=aircraft_names, y=wing_loadings, name='Wing Loading (N/m²)',
               marker_color=colors),
        row=2, col=1
    )
    
    # V-n diagram comparison
    for i, aircraft in enumerate(aircraft_list):
        envelope = FlightEnvelope(aircraft)
        velocities, load_factors = envelope.generate_v_n_diagram()
        
        fig.add_trace(
            go.Scatter(x=velocities, y=load_factors, mode='lines',
                      name=f'{aircraft.name} - Flight Envelope',
                      line=dict(color=colors[i], width=3),
                      fill='tonexty' if i == 0 else None),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        title='Interactive Aircraft Design Comparison Dashboard',
        height=800,
        showlegend=True
    )
    
    # Update axis labels
    fig.update_xaxes(title_text="Drag Coefficient (CD)", row=1, col=1)
    fig.update_yaxes(title_text="Lift Coefficient (CL)", row=1, col=1)
    
    fig.update_xaxes(title_text="Angle of Attack (degrees)", row=1, col=2)
    fig.update_yaxes(title_text="L/D Ratio", row=1, col=2)
    
    fig.update_xaxes(title_text="Aircraft Type", row=2, col=1)
    fig.update_yaxes(title_text="Wing Loading (N/m²)", row=2, col=1)
    
    fig.update_xaxes(title_text="Velocity (m/s)", row=2, col=2)
    fig.update_yaxes(title_text="Load Factor (g)", row=2, col=2)
    
    return fig


def create_3d_performance_surface():
    """Create a 3D surface plot of aircraft performance"""
    
    # Use the commercial airliner for this demo
    aircraft_list = create_sample_aircraft()
    airliner = aircraft_list[0]
    
    analyzer = PerformanceAnalyzer(airliner)
    performance_data = analyzer.generate_performance_envelope()
    
    # Create 3D surface plot
    fig = go.Figure(data=[go.Surface(
        z=performance_data['ld_ratios'],
        x=performance_data['speeds'],
        y=performance_data['altitudes'],
        colorscale='Viridis',
        name='L/D Ratio'
    )])
    
    fig.update_layout(
        title='3D Performance Envelope - L/D Ratio vs Speed and Altitude',
        scene=dict(
            xaxis_title='Speed (m/s)',
            yaxis_title='Altitude (m)',
            zaxis_title='L/D Ratio'
        ),
        width=800,
        height=600
    )
    
    return fig


def main():
    """Run the interactive demo"""
    
    print("🛩️  Aircraft Design Interactive Demo")
    print("=" * 50)
    print("Generating interactive visualizations...")
    
    # Create organized folder structure
    visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
    comparisons_dir = os.path.join(visualizations_dir, 'comparisons')
    examples_dir = os.path.join(visualizations_dir, 'examples')
    reference_dir = os.path.join(visualizations_dir, 'reference_aircraft')
    
    os.makedirs(comparisons_dir, exist_ok=True)
    os.makedirs(examples_dir, exist_ok=True)
    
    # Create comparison dashboard
    print("1. Creating aircraft comparison dashboard...")
    comparison_fig = create_interactive_comparison()
    comparison_path = os.path.join(comparisons_dir, "aircraft_comparison_interactive.html")
    comparison_fig.write_html(comparison_path)
    print("   ✓ Saved in 'comparisons/'")
    
    # Create 3D performance surface
    print("2. Creating 3D performance surface...")
    surface_fig = create_3d_performance_surface()
    surface_path = os.path.join(examples_dir, "performance_3d_interactive.html")
    surface_fig.write_html(surface_path)
    print("   ✓ Saved in 'examples/'")
    
    # Create individual aircraft dashboards
    aircraft_list = create_sample_aircraft()
    aircraft_folder_names = ['commercial_airliner', 'general_aviation', 'fighter_jet']
    
    for aircraft, folder_name in zip(aircraft_list, aircraft_folder_names):
        print(f"3. Creating dashboard for {aircraft.name}...")
        
        # Create aircraft-specific folder
        aircraft_folder = os.path.join(reference_dir, folder_name)
        os.makedirs(aircraft_folder, exist_ok=True)
        
        dashboard_fig = create_interactive_dashboard(aircraft)
        dashboard_path = os.path.join(aircraft_folder, "dashboard_interactive.html")
        dashboard_fig.write_html(dashboard_path)
        print(f"   ✓ Saved in 'reference_aircraft/{folder_name}/'")
    
    print("\n" + "=" * 50)
    print("✅ Interactive visualizations created!")
    print("\nGenerated files in organized folders:")
    print("- comparisons/aircraft_comparison_interactive.html")
    print("- examples/performance_3d_interactive.html")
    print("- reference_aircraft/commercial_airliner/dashboard_interactive.html")
    print("- reference_aircraft/general_aviation/dashboard_interactive.html")
    print("- reference_aircraft/fighter_jet/dashboard_interactive.html")
    print("\n📖 Open any of these HTML files in your web browser")
    print("   to explore the interactive visualizations!")
    
    # Try to open the main comparison in browser
    try:
        import webbrowser
        print("\n🌐 Opening main comparison dashboard in your browser...")
        webbrowser.open(comparison_path)
    except:
        print(f"\n💡 Manually open the comparison file in your browser")


if __name__ == "__main__":
    main()
