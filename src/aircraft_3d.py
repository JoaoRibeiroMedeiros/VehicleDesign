"""
3D Aircraft Visualization Module

This module provides 3D visualization capabilities for aircraft geometries,
allowing users to see the actual shape and proportions of different designs.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from typing import Dict, List, Tuple, Optional
from .aircraft import Aircraft


class Aircraft3DVisualizer:
    """
    3D visualization tools for aircraft geometry and shape representation.
    
    This class generates 3D models of aircraft based on their geometric parameters,
    providing intuitive visual understanding of design differences.
    """
    
    def __init__(self, aircraft: Aircraft):
        """
        Initialize 3D visualizer for an aircraft.
        
        Args:
            aircraft: Aircraft object to visualize
        """
        self.aircraft = aircraft
        self.geom = aircraft.geometry
        
    def generate_wing_geometry(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate 3D coordinates for the wing surface.
        
        Creates a realistic wing shape based on geometric parameters including
        span, chord, taper ratio, sweep angle, and dihedral.
        Wing is positioned at realistic location along fuselage.
        
        Returns:
            Tuple of (X, Y, Z) coordinate arrays for wing surface
        """
        # Wing parameters
        span = self.geom.wing_span
        root_chord = self.geom.wing_chord / (1 + self.geom.taper_ratio) * 2  # Estimate root chord
        tip_chord = root_chord * self.geom.taper_ratio
        sweep_rad = np.radians(self.geom.sweep_angle)
        dihedral_rad = np.radians(self.geom.dihedral_angle)
        
        # Calculate realistic wing position along fuselage
        # Wings are typically positioned at 25-40% of fuselage length from nose
        wing_position_factor = self._calculate_wing_position_factor()
        wing_root_x_position = self.geom.fuselage_length * wing_position_factor
        
        # Create wing sections along span
        n_sections = 20
        y_positions = np.linspace(0, span/2, n_sections)
        
        # Calculate chord length at each section (linear taper)
        chord_lengths = root_chord - (root_chord - tip_chord) * (y_positions / (span/2))
        
        # Calculate sweep offset at each section
        sweep_offsets = y_positions * np.tan(sweep_rad)
        
        # Calculate dihedral height at each section
        dihedral_heights = y_positions * np.tan(dihedral_rad)
        
        # Create wing surface points
        n_chord = 15
        chord_positions = np.linspace(0, 1, n_chord)
        
        # Initialize coordinate arrays
        X = np.zeros((n_sections, n_chord))
        Y = np.zeros((n_sections, n_chord))
        Z = np.zeros((n_sections, n_chord))
        
        for i, y_pos in enumerate(y_positions):
            chord_len = chord_lengths[i]
            sweep_offset = sweep_offsets[i]
            dihedral_height = dihedral_heights[i]
            
            # Generate airfoil shape (simplified)
            x_coords = chord_positions * chord_len + sweep_offset + wing_root_x_position
            z_coords = self._generate_airfoil_shape(chord_positions, chord_len) + dihedral_height
            
            X[i, :] = x_coords
            Y[i, :] = y_pos
            Z[i, :] = z_coords
        
        # Create full wing (both sides)
        X_full = np.concatenate([X, X], axis=0)
        Y_full = np.concatenate([Y, -Y], axis=0)
        Z_full = np.concatenate([Z, Z], axis=0)
        
        return X_full, Y_full, Z_full
    
    def _calculate_wing_position_factor(self) -> float:
        """
        Calculate realistic wing position along fuselage based on aircraft type.
        
        Returns:
            Factor (0-1) representing wing position from nose to tail
        """
        # Determine aircraft type based on characteristics
        aspect_ratio = self.geom.aspect_ratio
        sweep_angle = self.geom.sweep_angle
        wing_loading = self.aircraft.mass.max_takeoff_weight * 9.81 / self.geom.wing_area
        
        # Fighter-like aircraft (low AR, high sweep, high wing loading)
        if aspect_ratio < 5 and sweep_angle > 30 and wing_loading > 4000:
            return 0.45  # Wings further back for stability and CG
        
        # Airliner-like aircraft (high AR, moderate sweep)
        elif aspect_ratio > 8 and sweep_angle > 15:
            return 0.35  # Wings forward for passenger cabin space
        
        # General aviation (moderate AR, low sweep, low wing loading)
        elif aspect_ratio > 6 and sweep_angle < 10 and wing_loading < 2000:
            return 0.30  # Wings forward for CG with cabin loading
        
        # Default position
        else:
            return 0.35
    
    def _generate_airfoil_shape(self, chord_positions: np.ndarray, chord_length: float) -> np.ndarray:
        """
        Generate simplified airfoil cross-section shape.
        
        Args:
            chord_positions: Normalized positions along chord (0 to 1)
            chord_length: Actual chord length
            
        Returns:
            Z coordinates for airfoil upper surface
        """
        # Simplified airfoil using thickness ratio
        thickness = self.geom.thickness_ratio * chord_length
        
        # NACA-like airfoil approximation
        x = chord_positions
        z_upper = thickness * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 
                              0.2843 * x**3 - 0.1015 * x**4)
        
        return z_upper
    
    def generate_fuselage_geometry(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate 3D coordinates for the fuselage.
        
        Returns:
            Tuple of (X, Y, Z) coordinate arrays for fuselage surface
        """
        length = self.geom.fuselage_length
        diameter = self.geom.fuselage_diameter
        radius = diameter / 2
        
        # Create fuselage sections along length
        n_sections = 30
        x_positions = np.linspace(0, length, n_sections)
        
        # Create circular cross-sections with varying radius
        n_circle = 20
        theta = np.linspace(0, 2*np.pi, n_circle)
        
        X = np.zeros((n_sections, n_circle))
        Y = np.zeros((n_sections, n_circle))
        Z = np.zeros((n_sections, n_circle))
        
        for i, x_pos in enumerate(x_positions):
            # Vary radius along fuselage (tapered ends)
            if x_pos < length * 0.1:  # Nose taper
                r = radius * (x_pos / (length * 0.1))
            elif x_pos > length * 0.8:  # Tail taper
                r = radius * (1 - (x_pos - length * 0.8) / (length * 0.2))
            else:  # Constant section
                r = radius
            
            # Generate circular cross-section
            y_coords = r * np.cos(theta)
            z_coords = r * np.sin(theta)
            
            X[i, :] = x_pos
            Y[i, :] = y_coords
            Z[i, :] = z_coords
        
        return X, Y, Z
    
    def generate_tail_geometry(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate 3D coordinates for the tail (vertical and horizontal stabilizers).
        
        Returns:
            Tuple of (X, Y, Z) coordinate arrays for tail surfaces
        """
        # Tail sizing based on fuselage length and wing area (typical ratios)
        tail_position = self.geom.fuselage_length * 0.85  # Near the back
        
        # Horizontal stabilizer (simplified)
        h_tail_span = self.geom.wing_span * 0.3  # Typical ratio
        h_tail_chord = self.geom.wing_chord * 0.4
        
        # Vertical stabilizer
        v_tail_height = self.geom.fuselage_length * 0.15
        v_tail_chord = h_tail_chord
        
        # Generate horizontal stabilizer
        h_tail_y = np.array([[-h_tail_span/2, h_tail_span/2, h_tail_span/2, -h_tail_span/2, -h_tail_span/2]])
        h_tail_x = np.array([[tail_position, tail_position, tail_position + h_tail_chord, 
                             tail_position + h_tail_chord, tail_position]])
        h_tail_z = np.array([[0, 0, 0, 0, 0]])
        
        # Generate vertical stabilizer
        v_tail_x = np.array([[tail_position, tail_position + v_tail_chord, tail_position + v_tail_chord, 
                             tail_position, tail_position]])
        v_tail_y = np.array([[0, 0, 0, 0, 0]])
        v_tail_z = np.array([[0, 0, v_tail_height, v_tail_height, 0]])
        
        # Combine horizontal and vertical stabilizers
        X_tail = np.concatenate([h_tail_x, v_tail_x], axis=0)
        Y_tail = np.concatenate([h_tail_y, v_tail_y], axis=0)
        Z_tail = np.concatenate([h_tail_z, v_tail_z], axis=0)
        
        return X_tail, Y_tail, Z_tail
    
    def plot_3d_aircraft_matplotlib(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Create 3D aircraft visualization using matplotlib.
        
        Args:
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure object
        """
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Generate aircraft components
        X_wing, Y_wing, Z_wing = self.generate_wing_geometry()
        X_fus, Y_fus, Z_fus = self.generate_fuselage_geometry()
        X_tail, Y_tail, Z_tail = self.generate_tail_geometry()
        
        # Plot wing
        ax.plot_surface(X_wing, Y_wing, Z_wing, alpha=0.7, color='lightblue', 
                       edgecolor='darkblue', linewidth=0.5, label='Wing')
        
        # Plot fuselage
        ax.plot_surface(X_fus, Y_fus, Z_fus, alpha=0.8, color='lightgray', 
                       edgecolor='darkgray', linewidth=0.5, label='Fuselage')
        
        # Plot tail surfaces
        for i in range(X_tail.shape[0]):
            ax.plot(X_tail[i], Y_tail[i], Z_tail[i], 'r-', linewidth=2, alpha=0.8)
        
        # Set labels and title
        ax.set_xlabel('X (Length) [m]', fontsize=12)
        ax.set_ylabel('Y (Span) [m]', fontsize=12)
        ax.set_zlabel('Z (Height) [m]', fontsize=12)
        ax.set_title(f'3D Aircraft Geometry - {self.aircraft.name}', fontsize=14, fontweight='bold')
        
        # Set equal aspect ratio with 1:1:1 scaling
        max_range = max(self.geom.fuselage_length, self.geom.wing_span) / 2
        
        # Calculate proper bounds for 1:1 aspect ratio
        x_center = self.geom.fuselage_length / 2
        y_center = 0
        z_center = 0
        
        # Use the same range for all axes to ensure 1:1:1 scaling
        ax.set_xlim([x_center - max_range*1.2, x_center + max_range*1.2])
        ax.set_ylim([y_center - max_range*1.2, y_center + max_range*1.2])
        ax.set_zlim([z_center - max_range*0.6, z_center + max_range*0.6])
        
        # Force equal aspect ratio
        ax.set_box_aspect([2.4, 2.4, 1.2])  # Maintain proportional box but equal scaling
        
        # Add parameter annotations
        wing_pos_factor = self._calculate_wing_position_factor()
        wing_pos_meters = self.geom.fuselage_length * wing_pos_factor
        
        info_text = (f"Span: {self.geom.wing_span:.1f}m\n"
                    f"Length: {self.geom.fuselage_length:.1f}m\n"
                    f"Aspect Ratio: {self.geom.aspect_ratio:.1f}\n"
                    f"Sweep: {self.geom.sweep_angle:.1f}°\n"
                    f"Wing Position: {wing_pos_meters:.1f}m ({wing_pos_factor:.0%})\n"
                    f"MTOW: {self.aircraft.mass.max_takeoff_weight:.0f}kg")
        
        ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
            full_path = os.path.join(visualizations_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_interactive_3d_plotly(self) -> go.Figure:
        """
        Create interactive 3D aircraft visualization using Plotly.
        
        Returns:
            Plotly figure object with interactive 3D model
        """
        # Generate geometries
        X_wing, Y_wing, Z_wing = self.generate_wing_geometry()
        X_fus, Y_fus, Z_fus = self.generate_fuselage_geometry()
        X_tail, Y_tail, Z_tail = self.generate_tail_geometry()
        
        fig = go.Figure()
        
        # Add wing surface
        fig.add_trace(go.Surface(
            x=X_wing, y=Y_wing, z=Z_wing,
            colorscale='Blues',
            opacity=0.8,
            name='Wing',
            showscale=False,
            hovertemplate='Wing<br>X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m<extra></extra>'
        ))
        
        # Add fuselage surface
        fig.add_trace(go.Surface(
            x=X_fus, y=Y_fus, z=Z_fus,
            colorscale='Greys',
            opacity=0.9,
            name='Fuselage',
            showscale=False,
            hovertemplate='Fuselage<br>X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m<extra></extra>'
        ))
        
        # Add tail surfaces as lines
        for i in range(X_tail.shape[0]):
            fig.add_trace(go.Scatter3d(
                x=X_tail[i], y=Y_tail[i], z=Z_tail[i],
                mode='lines',
                line=dict(color='red', width=4),
                name='Tail' if i == 0 else None,
                showlegend=(i == 0),
                hovertemplate='Tail<br>X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m<extra></extra>'
            ))
        
        # Update layout with proper 1:1:1 scaling
        max_range = max(self.geom.fuselage_length, self.geom.wing_span) / 2
        
        # Calculate proper bounds for 1:1 aspect ratio
        x_center = self.geom.fuselage_length / 2
        y_center = 0
        z_center = 0
        
        fig.update_layout(
            title=f'Interactive 3D Aircraft Model - {self.aircraft.name}',
            scene=dict(
                xaxis_title='X - Length (m)',
                yaxis_title='Y - Span (m)',
                zaxis_title='Z - Height (m)',
                xaxis=dict(range=[x_center - max_range*1.2, x_center + max_range*1.2]),
                yaxis=dict(range=[y_center - max_range*1.2, y_center + max_range*1.2]),
                zaxis=dict(range=[z_center - max_range*0.6, z_center + max_range*0.6]),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.5)  # True 1:1 scaling for X:Y, Z compressed for better view
            ),
            width=800,
            height=600
        )
        
        return fig


def create_aircraft_comparison_3d(aircraft_list: List[Aircraft], save_path: Optional[str] = None) -> plt.Figure:
    """
    Create side-by-side 3D comparison of multiple aircraft.
    
    Args:
        aircraft_list: List of aircraft to compare
        save_path: Optional path to save the plot
        
    Returns:
        Matplotlib figure with multiple 3D subplots
    """
    n_aircraft = len(aircraft_list)
    fig = plt.figure(figsize=(5*n_aircraft, 8))
    
    for i, aircraft in enumerate(aircraft_list):
        ax = fig.add_subplot(1, n_aircraft, i+1, projection='3d')
        
        visualizer = Aircraft3DVisualizer(aircraft)
        
        # Generate geometries
        X_wing, Y_wing, Z_wing = visualizer.generate_wing_geometry()
        X_fus, Y_fus, Z_fus = visualizer.generate_fuselage_geometry()
        X_tail, Y_tail, Z_tail = visualizer.generate_tail_geometry()
        
        # Plot surfaces
        ax.plot_surface(X_wing, Y_wing, Z_wing, alpha=0.7, color='lightblue', 
                       edgecolor='darkblue', linewidth=0.3)
        ax.plot_surface(X_fus, Y_fus, Z_fus, alpha=0.8, color='lightgray', 
                       edgecolor='darkgray', linewidth=0.3)
        
        # Plot tail surfaces
        for j in range(X_tail.shape[0]):
            ax.plot(X_tail[j], Y_tail[j], Z_tail[j], 'r-', linewidth=1.5, alpha=0.8)
        
        # Set labels and title
        ax.set_title(f'{aircraft.name}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Length (m)')
        ax.set_ylabel('Span (m)')
        ax.set_zlabel('Height (m)')
        
        # Set consistent scale for comparison with 1:1:1 scaling
        max_span = max([a.geometry.wing_span for a in aircraft_list])
        max_length = max([a.geometry.fuselage_length for a in aircraft_list])
        max_range = max(max_span, max_length) / 2
        
        # Calculate proper bounds for 1:1 aspect ratio
        x_center = aircraft.geometry.fuselage_length / 2
        y_center = 0
        z_center = 0
        
        # Use the same range for all axes to ensure 1:1:1 scaling
        ax.set_xlim([x_center - max_range*1.2, x_center + max_range*1.2])
        ax.set_ylim([y_center - max_range*1.2, y_center + max_range*1.2])
        ax.set_zlim([z_center - max_range*0.6, z_center + max_range*0.6])
        
        # Force equal aspect ratio
        try:
            ax.set_box_aspect([2.4, 2.4, 1.2])  # Maintain proportional box but equal scaling
        except AttributeError:
            # Fallback for older matplotlib versions
            ax.set_aspect('equal')
        
        # Add key parameters
        info_text = (f"Span: {aircraft.geometry.wing_span:.1f}m\n"
                    f"AR: {aircraft.geometry.aspect_ratio:.1f}\n"
                    f"Sweep: {aircraft.geometry.sweep_angle:.1f}°")
        ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.suptitle('Aircraft 3D Geometry Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
        full_path = os.path.join(visualizations_dir, save_path)
        plt.savefig(full_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_interactive_aircraft_gallery(aircraft_list: List[Aircraft]) -> go.Figure:
    """
    Create an interactive gallery of 3D aircraft models.
    
    Args:
        aircraft_list: List of aircraft to display
        
    Returns:
        Plotly figure with dropdown selection for different aircraft
    """
    # Create initial figure with first aircraft
    initial_visualizer = Aircraft3DVisualizer(aircraft_list[0])
    fig = initial_visualizer.create_interactive_3d_plotly()
    
    # Create dropdown buttons for aircraft selection
    buttons = []
    
    for i, aircraft in enumerate(aircraft_list):
        visualizer = Aircraft3DVisualizer(aircraft)
        X_wing, Y_wing, Z_wing = visualizer.generate_wing_geometry()
        X_fus, Y_fus, Z_fus = visualizer.generate_fuselage_geometry()
        
        # Create visibility array (only show current aircraft)
        visible = [False] * (len(aircraft_list) * 2)  # 2 surfaces per aircraft
        visible[i*2] = True      # Wing
        visible[i*2 + 1] = True  # Fuselage
        
        button = dict(
            label=aircraft.name,
            method="update",
            args=[{"visible": visible},
                  {"title": f"Interactive 3D Aircraft Model - {aircraft.name}"}]
        )
        buttons.append(button)
    
    # Add all aircraft surfaces to figure (initially hidden except first)
    fig.data = []  # Clear initial data
    
    for i, aircraft in enumerate(aircraft_list):
        visualizer = Aircraft3DVisualizer(aircraft)
        X_wing, Y_wing, Z_wing = visualizer.generate_wing_geometry()
        X_fus, Y_fus, Z_fus = visualizer.generate_fuselage_geometry()
        
        # Wing surface
        fig.add_trace(go.Surface(
            x=X_wing, y=Y_wing, z=Z_wing,
            colorscale='Blues',
            opacity=0.8,
            name=f'{aircraft.name} Wing',
            showscale=False,
            visible=(i == 0),  # Only first aircraft visible initially
            hovertemplate=f'{aircraft.name} Wing<br>X: %{{x:.1f}}m<br>Y: %{{y:.1f}}m<br>Z: %{{z:.1f}}m<extra></extra>'
        ))
        
        # Fuselage surface
        fig.add_trace(go.Surface(
            x=X_fus, y=Y_fus, z=Z_fus,
            colorscale='Greys',
            opacity=0.9,
            name=f'{aircraft.name} Fuselage',
            showscale=False,
            visible=(i == 0),  # Only first aircraft visible initially
            hovertemplate=f'{aircraft.name} Fuselage<br>X: %{{x:.1f}}m<br>Y: %{{y:.1f}}m<br>Z: %{{z:.1f}}m<extra></extra>'
        ))
    
    # Update layout with dropdown
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.02,
                yanchor="top"
            ),
        ],
        annotations=[
            dict(text="Select Aircraft:", showarrow=False,
                 x=0.02, y=1.08, xref="paper", yref="paper", align="left")
        ]
    )
    
    return fig
