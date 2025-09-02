"""
Aircraft Design Visualization Module

This module provides comprehensive visualization capabilities for aircraft
design analysis, performance data, and optimization results.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from typing import Dict, List, Tuple, Optional

# Handle imports for both package and direct execution
try:
    from .aircraft import Aircraft
    from .flight_conditions import FlightConditions, FlightEnvelope
    from .performance_analysis import PerformanceAnalyzer
except ImportError:
    from aircraft import Aircraft
    from flight_conditions import FlightConditions, FlightEnvelope
    from performance_analysis import PerformanceAnalyzer

# Create visualizations directory if it doesn't exist
VISUALIZATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)

def get_aircraft_folder(aircraft_name: str, is_custom: bool = False) -> str:
    """
    Get or create organized folder structure for aircraft visualizations.
    
    Args:
        aircraft_name: Name of the aircraft
        is_custom: Whether this is a custom designed aircraft
        
    Returns:
        Path to the aircraft's visualization folder
    """
    # Clean aircraft name for folder
    safe_name = aircraft_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    if is_custom:
        # Custom aircraft go in custom_designs folder with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{safe_name}_{timestamp}"
        aircraft_dir = os.path.join(VISUALIZATIONS_DIR, 'custom_designs', folder_name)
    else:
        # Reference aircraft go in reference_aircraft folder
        aircraft_dir = os.path.join(VISUALIZATIONS_DIR, 'reference_aircraft', safe_name)
    
    os.makedirs(aircraft_dir, exist_ok=True)
    return aircraft_dir


class AircraftVisualizer:
    """
    Comprehensive visualization tools for aircraft design and analysis
    """
    
    def __init__(self, aircraft: Aircraft):
        self.aircraft = aircraft
        self.analyzer = PerformanceAnalyzer(aircraft)
        self._aircraft_folder = None
    
    def set_output_folder(self, folder_path: str):
        """Set the output folder for this aircraft's visualizations."""
        self._aircraft_folder = folder_path
        os.makedirs(folder_path, exist_ok=True)
        
    def plot_drag_polar(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot aircraft drag polar (CL vs CD)
        
        Args:
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        angles = np.linspace(-5, 20, 100)
        cl_values = []
        cd_values = []
        
        for angle in angles:
            cl = self.aircraft.calculate_lift_coefficient(angle)
            cd = self.aircraft.calculate_drag_coefficient(cl)
            cl_values.append(cl)
            cd_values.append(cd)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.plot(cd_values, cl_values, 'b-', linewidth=2, label=self.aircraft.name)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Drag Coefficient (CD)', fontsize=12)
        ax.set_ylabel('Lift Coefficient (CL)', fontsize=12)
        ax.set_title(f'Drag Polar - {self.aircraft.name}', fontsize=14, fontweight='bold')
        ax.legend()
        
        # Add annotations for key points
        best_aoa = self.analyzer.find_optimal_angle_of_attack()
        best_cl = self.aircraft.calculate_lift_coefficient(best_aoa)
        best_cd = self.aircraft.calculate_drag_coefficient(best_cl)
        ax.plot(best_cd, best_cl, 'ro', markersize=8, label=f'Max L/D (α={best_aoa:.1f}°)')
        ax.annotate(f'Max L/D\n({best_cd:.3f}, {best_cl:.3f})', 
                   xy=(best_cd, best_cl), xytext=(best_cd+0.005, best_cl+0.1),
                   arrowprops=dict(arrowstyle='->', color='red'))
        
        plt.tight_layout()
        if save_path:
            # Use aircraft-specific folder if available
            if hasattr(self, '_aircraft_folder') and self._aircraft_folder:
                full_path = os.path.join(self._aircraft_folder, save_path)
            else:
                full_path = os.path.join(VISUALIZATIONS_DIR, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_lift_drag_vs_aoa(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot lift and drag coefficients vs angle of attack
        
        Args:
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        angles = np.linspace(-5, 20, 100)
        cl_values = []
        cd_values = []
        ld_ratios = []
        
        for angle in angles:
            cl = self.aircraft.calculate_lift_coefficient(angle)
            cd = self.aircraft.calculate_drag_coefficient(cl)
            ld = cl / cd if cd > 0 else 0
            
            cl_values.append(cl)
            cd_values.append(cd)
            ld_ratios.append(ld)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Top plot: CL and CD vs AoA
        ax1.plot(angles, cl_values, 'b-', linewidth=2, label='CL')
        ax1.plot(angles, cd_values, 'r-', linewidth=2, label='CD')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel('Angle of Attack (degrees)', fontsize=12)
        ax1.set_ylabel('Coefficient', fontsize=12)
        ax1.set_title(f'Lift and Drag Coefficients vs AoA - {self.aircraft.name}', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.set_xlim(-5, 20)
        
        # Bottom plot: L/D ratio vs AoA
        ax2.plot(angles, ld_ratios, 'g-', linewidth=2, label='L/D Ratio')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlabel('Angle of Attack (degrees)', fontsize=12)
        ax2.set_ylabel('L/D Ratio', fontsize=12)
        ax2.set_title('Lift-to-Drag Ratio vs AoA', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.set_xlim(-5, 20)
        
        # Mark optimal point
        best_aoa = self.analyzer.find_optimal_angle_of_attack()
        best_ld = self.aircraft.calculate_lift_drag_ratio(best_aoa)
        ax2.plot(best_aoa, best_ld, 'ro', markersize=8)
        ax2.annotate(f'Max L/D\n({best_aoa:.1f}°, {best_ld:.1f})', 
                    xy=(best_aoa, best_ld), xytext=(best_aoa+2, best_ld+2),
                    arrowprops=dict(arrowstyle='->', color='red'))
        
        plt.tight_layout()
        if save_path:
            # Use aircraft-specific folder if available
            if hasattr(self, '_aircraft_folder') and self._aircraft_folder:
                full_path = os.path.join(self._aircraft_folder, save_path)
            else:
                full_path = os.path.join(VISUALIZATIONS_DIR, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_v_n_diagram(self, altitude: float = 0, weight: float = None, 
                        save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot V-n (velocity-load factor) diagram
        
        Args:
            altitude: Altitude in meters
            weight: Aircraft weight in kg
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        envelope = FlightEnvelope(self.aircraft)
        velocities, load_factors = envelope.generate_v_n_diagram(altitude, weight)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(velocities, load_factors, 'b-', linewidth=2, label='Flight Envelope')
        ax.fill(velocities, load_factors, alpha=0.2, color='blue')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Velocity (m/s)', fontsize=12)
        ax.set_ylabel('Load Factor (g)', fontsize=12)
        ax.set_title(f'V-n Diagram - {self.aircraft.name} (Alt: {altitude}m)', fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Add key speed annotations
        if weight is None:
            weight = self.aircraft.mass.max_takeoff_weight
        v_stall = envelope.calculate_stall_speed(altitude, weight)
        ax.axvline(x=v_stall, color='red', linestyle='--', alpha=0.7, label=f'Stall Speed ({v_stall:.1f} m/s)')
        
        ax.legend()
        plt.tight_layout()
        if save_path:
            # Use aircraft-specific folder if available
            if hasattr(self, '_aircraft_folder') and self._aircraft_folder:
                full_path = os.path.join(self._aircraft_folder, save_path)
            else:
                full_path = os.path.join(VISUALIZATIONS_DIR, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_performance_envelope(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot 3D performance envelope showing altitude, speed, and L/D ratio
        
        Args:
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        performance_data = self.analyzer.generate_performance_envelope()
        
        fig = plt.figure(figsize=(15, 10))
        
        # Create subplots
        ax1 = plt.subplot(2, 2, 1, projection='3d')
        ax2 = plt.subplot(2, 2, 2)
        ax3 = plt.subplot(2, 2, 3)
        ax4 = plt.subplot(2, 2, 4)
        
        # 3D surface plot of L/D ratio
        X, Y = np.meshgrid(performance_data['speeds'], performance_data['altitudes'])
        Z = performance_data['ld_ratios']
        
        # Mask invalid regions
        Z_masked = np.ma.masked_where(Z <= 0, Z)
        
        surf = ax1.plot_surface(X, Y, Z_masked, cmap='viridis', alpha=0.8)
        ax1.set_xlabel('Speed (m/s)')
        ax1.set_ylabel('Altitude (m)')
        ax1.set_zlabel('L/D Ratio')
        ax1.set_title('L/D Ratio vs Speed and Altitude')
        
        # 2D contour plot of L/D ratio
        contour = ax2.contour(X, Y, Z_masked, levels=20)
        ax2.clabel(contour, inline=True, fontsize=8)
        ax2.set_xlabel('Speed (m/s)')
        ax2.set_ylabel('Altitude (m)')
        ax2.set_title('L/D Ratio Contours')
        ax2.grid(True, alpha=0.3)
        
        # Stall speed vs altitude
        ax3.plot(performance_data['stall_speeds'], performance_data['altitudes'], 'r-', linewidth=2)
        ax3.set_xlabel('Stall Speed (m/s)')
        ax3.set_ylabel('Altitude (m)')
        ax3.set_title('Stall Speed vs Altitude')
        ax3.grid(True, alpha=0.3)
        
        # Power required contours
        Z_power = performance_data['power_required']
        Z_power_masked = np.ma.masked_where(Z_power == np.inf, Z_power)
        contour_power = ax4.contour(X, Y, Z_power_masked, levels=15)
        ax4.clabel(contour_power, inline=True, fontsize=8)
        ax4.set_xlabel('Speed (m/s)')
        ax4.set_ylabel('Altitude (m)')
        ax4.set_title('Power Required Contours (W)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            # Use aircraft-specific folder if available
            if hasattr(self, '_aircraft_folder') and self._aircraft_folder:
                full_path = os.path.join(self._aircraft_folder, save_path)
            else:
                full_path = os.path.join(VISUALIZATIONS_DIR, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_climb_performance(self, thrust_available: float = 50000, 
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot climb performance vs altitude
        
        Args:
            thrust_available: Available thrust in N
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        weight = self.aircraft.mass.max_takeoff_weight
        climb_data = self.analyzer.calculate_climb_performance(
            (0, 15000), weight, thrust_available
        )
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Climb rate vs altitude
        ax1.plot(climb_data['climb_rates'], climb_data['altitudes'], 'b-', linewidth=2)
        ax1.axvline(x=0.508, color='r', linestyle='--', alpha=0.7, label='Service Ceiling Limit (100 ft/min)')
        ax1.set_xlabel('Climb Rate (m/s)')
        ax1.set_ylabel('Altitude (m)')
        ax1.set_title(f'Climb Rate vs Altitude - {self.aircraft.name}')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Climb angle vs altitude
        ax2.plot(climb_data['climb_angles'], climb_data['altitudes'], 'g-', linewidth=2)
        ax2.set_xlabel('Climb Angle (degrees)')
        ax2.set_ylabel('Altitude (m)')
        ax2.set_title('Climb Angle vs Altitude')
        ax2.grid(True, alpha=0.3)
        
        # Add service ceiling annotation
        service_ceiling = climb_data['service_ceiling']
        ax1.axhline(y=service_ceiling, color='r', linestyle=':', alpha=0.7)
        ax1.annotate(f'Service Ceiling\n{service_ceiling:.0f} m', 
                    xy=(0.1, service_ceiling), xytext=(2, service_ceiling+1000),
                    arrowprops=dict(arrowstyle='->', color='red'))
        
        plt.tight_layout()
        if save_path:
            # Use aircraft-specific folder if available
            if hasattr(self, '_aircraft_folder') and self._aircraft_folder:
                full_path = os.path.join(self._aircraft_folder, save_path)
            else:
                full_path = os.path.join(VISUALIZATIONS_DIR, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        
        return fig


def compare_aircraft_designs(aircraft_list: List[Aircraft], save_path: Optional[str] = None) -> plt.Figure:
    """
    Compare multiple aircraft designs
    
    Args:
        aircraft_list: List of aircraft to compare
        save_path: Optional path to save the plot
        
    Returns:
        Matplotlib figure
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    # Drag polars comparison
    for i, aircraft in enumerate(aircraft_list):
        angles = np.linspace(-5, 20, 100)
        cl_values = []
        cd_values = []
        
        for angle in angles:
            cl = aircraft.calculate_lift_coefficient(angle)
            cd = aircraft.calculate_drag_coefficient(cl)
            cl_values.append(cl)
            cd_values.append(cd)
        
        ax1.plot(cd_values, cl_values, color=colors[i % len(colors)], 
                linewidth=2, label=aircraft.name)
    
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Drag Coefficient (CD)')
    ax1.set_ylabel('Lift Coefficient (CL)')
    ax1.set_title('Drag Polar Comparison')
    ax1.legend()
    
    # L/D ratio comparison
    for i, aircraft in enumerate(aircraft_list):
        angles = np.linspace(-5, 20, 100)
        ld_ratios = []
        
        for angle in angles:
            ld = aircraft.calculate_lift_drag_ratio(angle)
            ld_ratios.append(ld)
        
        ax2.plot(angles, ld_ratios, color=colors[i % len(colors)], 
                linewidth=2, label=aircraft.name)
    
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Angle of Attack (degrees)')
    ax2.set_ylabel('L/D Ratio')
    ax2.set_title('L/D Ratio Comparison')
    ax2.legend()
    
    # Design parameters comparison
    aircraft_names = [aircraft.name for aircraft in aircraft_list]
    wing_loadings = [aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area 
                    for aircraft in aircraft_list]
    aspect_ratios = [aircraft.geometry.aspect_ratio for aircraft in aircraft_list]
    
    x_pos = np.arange(len(aircraft_names))
    ax3.bar(x_pos, wing_loadings, color=[colors[i % len(colors)] for i in range(len(aircraft_list))])
    ax3.set_xlabel('Aircraft')
    ax3.set_ylabel('Wing Loading (N/m²)')
    ax3.set_title('Wing Loading Comparison')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(aircraft_names, rotation=45)
    ax3.grid(True, alpha=0.3)
    
    ax4.bar(x_pos, aspect_ratios, color=[colors[i % len(colors)] for i in range(len(aircraft_list))])
    ax4.set_xlabel('Aircraft')
    ax4.set_ylabel('Aspect Ratio')
    ax4.set_title('Aspect Ratio Comparison')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(aircraft_names, rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_interactive_dashboard(aircraft: Aircraft) -> go.Figure:
    """
    Create an interactive Plotly dashboard for aircraft analysis
    
    Args:
        aircraft: Aircraft to analyze
        
    Returns:
        Plotly figure
    """
    analyzer = PerformanceAnalyzer(aircraft)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Drag Polar', 'L/D vs AoA', 'Performance Envelope', 'V-n Diagram'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "heatmap"}, {"type": "scatter"}]]
    )
    
    # Drag polar
    angles = np.linspace(-5, 20, 100)
    cl_values = []
    cd_values = []
    
    for angle in angles:
        cl = aircraft.calculate_lift_coefficient(angle)
        cd = aircraft.calculate_drag_coefficient(cl)
        cl_values.append(cl)
        cd_values.append(cd)
    
    fig.add_trace(
        go.Scatter(x=cd_values, y=cl_values, mode='lines', name='Drag Polar'),
        row=1, col=1
    )
    
    # L/D vs AoA
    ld_ratios = [aircraft.calculate_lift_drag_ratio(angle) for angle in angles]
    fig.add_trace(
        go.Scatter(x=angles, y=ld_ratios, mode='lines', name='L/D Ratio'),
        row=1, col=2
    )
    
    # Performance envelope (simplified)
    performance_data = analyzer.generate_performance_envelope()
    fig.add_trace(
        go.Heatmap(
            z=performance_data['ld_ratios'],
            x=performance_data['speeds'],
            y=performance_data['altitudes'],
            colorscale='Viridis',
            name='L/D Heatmap'
        ),
        row=2, col=1
    )
    
    # V-n diagram
    envelope = FlightEnvelope(aircraft)
    velocities, load_factors = envelope.generate_v_n_diagram()
    fig.add_trace(
        go.Scatter(x=velocities, y=load_factors, mode='lines', fill='tozeroy', name='Flight Envelope'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title=f'Aircraft Analysis Dashboard - {aircraft.name}',
        height=800,
        showlegend=False
    )
    
    return fig
