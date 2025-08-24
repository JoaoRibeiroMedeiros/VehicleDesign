"""
Aircraft Design System - Core Modules

This package contains the core modules for aircraft design exploration,
performance analysis, and optimization.
"""

from .aircraft import Aircraft, AircraftGeometry, AircraftMass, create_sample_aircraft
from .flight_conditions import (
    AtmosphericConditions, 
    FlightConditions, 
    FlightEnvelope,
    create_test_conditions
)
from .performance_analysis import PerformanceAnalyzer
from .design_optimizer import (
    DesignOptimizer,
    MaximizeRange,
    MinimizeFuelConsumption,
    MaximizeLiftToDrag,
    StallSpeedConstraint,
    TakeoffDistanceConstraint,
    WingLoadingConstraint
)
from .visualization import AircraftVisualizer, compare_aircraft_designs, create_interactive_dashboard
from .aircraft_3d import Aircraft3DVisualizer, create_aircraft_comparison_3d, create_interactive_aircraft_gallery

__version__ = "1.0.0"
__author__ = "Aircraft Design System"

__all__ = [
    # Aircraft classes
    'Aircraft', 'AircraftGeometry', 'AircraftMass', 'create_sample_aircraft',
    
    # Flight conditions
    'AtmosphericConditions', 'FlightConditions', 'FlightEnvelope', 'create_test_conditions',
    
    # Performance analysis
    'PerformanceAnalyzer',
    
    # Design optimization
    'DesignOptimizer', 'MaximizeRange', 'MinimizeFuelConsumption', 'MaximizeLiftToDrag',
    'StallSpeedConstraint', 'TakeoffDistanceConstraint', 'WingLoadingConstraint',
    
    # Visualization
    'AircraftVisualizer', 'compare_aircraft_designs', 'create_interactive_dashboard',
    
    # 3D Visualization
    'Aircraft3DVisualizer', 'create_aircraft_comparison_3d', 'create_interactive_aircraft_gallery'
]
