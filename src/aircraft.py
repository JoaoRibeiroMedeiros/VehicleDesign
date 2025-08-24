"""
Aircraft Design and Analysis Module

This module provides classes and functions for aircraft design exploration
and flight condition testing.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AircraftGeometry:
    """Aircraft geometric parameters"""
    wing_span: float  # meters
    wing_area: float  # square meters
    wing_chord: float  # meters
    aspect_ratio: float  # dimensionless
    sweep_angle: float  # degrees
    dihedral_angle: float  # degrees
    taper_ratio: float  # dimensionless
    thickness_ratio: float  # dimensionless
    fuselage_length: float  # meters
    fuselage_diameter: float  # meters


@dataclass
class AircraftMass:
    """Aircraft mass properties"""
    empty_weight: float  # kg
    fuel_capacity: float  # kg
    payload_capacity: float  # kg
    max_takeoff_weight: float  # kg
    
    @property
    def operating_empty_weight(self) -> float:
        return self.empty_weight
    
    @property
    def max_landing_weight(self) -> float:
        return self.max_takeoff_weight * 0.85  # Typical assumption


class Aircraft:
    """
    Main aircraft class for design exploration and analysis
    """
    
    def __init__(self, name: str, geometry: AircraftGeometry, mass: AircraftMass):
        self.name = name
        self.geometry = geometry
        self.mass = mass
        
        # Aerodynamic coefficients (can be refined based on geometry)
        self.cd0 = 0.025  # Zero-lift drag coefficient
        self.k = 1 / (np.pi * geometry.aspect_ratio * 0.8)  # Induced drag factor
        self.cl_max = 1.6  # Maximum lift coefficient
        self.cl_alpha = 2 * np.pi / (1 + 2/geometry.aspect_ratio)  # Lift curve slope
        
    def calculate_lift_coefficient(self, angle_of_attack: float) -> float:
        """
        Calculate lift coefficient based on angle of attack
        
        Args:
            angle_of_attack: Angle of attack in degrees
            
        Returns:
            Lift coefficient
        """
        alpha_rad = np.radians(angle_of_attack)
        cl = self.cl_alpha * alpha_rad
        return min(cl, self.cl_max)
    
    def calculate_drag_coefficient(self, lift_coefficient: float) -> float:
        """
        Calculate drag coefficient using drag polar
        
        Args:
            lift_coefficient: Current lift coefficient
            
        Returns:
            Drag coefficient
        """
        return self.cd0 + self.k * lift_coefficient**2
    
    def calculate_lift_drag_ratio(self, angle_of_attack: float) -> float:
        """
        Calculate lift-to-drag ratio
        
        Args:
            angle_of_attack: Angle of attack in degrees
            
        Returns:
            Lift-to-drag ratio
        """
        cl = self.calculate_lift_coefficient(angle_of_attack)
        cd = self.calculate_drag_coefficient(cl)
        return cl / cd if cd > 0 else 0
    
    def get_design_summary(self) -> Dict:
        """Get a summary of aircraft design parameters"""
        return {
            'name': self.name,
            'wing_span': self.geometry.wing_span,
            'wing_area': self.geometry.wing_area,
            'aspect_ratio': self.geometry.aspect_ratio,
            'max_takeoff_weight': self.mass.max_takeoff_weight,
            'wing_loading': self.mass.max_takeoff_weight * 9.81 / self.geometry.wing_area,
            'cd0': self.cd0,
            'k_factor': self.k
        }


def create_sample_aircraft() -> List[Aircraft]:
    """Create sample aircraft designs for comparison"""
    
    # Commercial airliner (Boeing 737-like)
    airliner_geom = AircraftGeometry(
        wing_span=35.8, wing_area=125.0, wing_chord=3.5, aspect_ratio=10.2,
        sweep_angle=25.0, dihedral_angle=6.0, taper_ratio=0.3, thickness_ratio=0.12,
        fuselage_length=39.5, fuselage_diameter=3.8
    )
    airliner_mass = AircraftMass(
        empty_weight=41000, fuel_capacity=20000, payload_capacity=18000, max_takeoff_weight=79000
    )
    airliner = Aircraft("Commercial Airliner", airliner_geom, airliner_mass)
    
    # General aviation aircraft (Cessna 172-like)
    ga_geom = AircraftGeometry(
        wing_span=11.0, wing_area=16.2, wing_chord=1.5, aspect_ratio=7.5,
        sweep_angle=0.0, dihedral_angle=1.0, taper_ratio=0.6, thickness_ratio=0.15,
        fuselage_length=8.3, fuselage_diameter=1.2
    )
    ga_mass = AircraftMass(
        empty_weight=760, fuel_capacity=200, payload_capacity=400, max_takeoff_weight=1157
    )
    ga_aircraft = Aircraft("General Aviation", ga_geom, ga_mass)
    
    # Fighter jet (F-16-like)
    fighter_geom = AircraftGeometry(
        wing_span=9.96, wing_area=27.9, wing_chord=3.2, aspect_ratio=3.6,
        sweep_angle=40.0, dihedral_angle=0.0, taper_ratio=0.2, thickness_ratio=0.04,
        fuselage_length=15.0, fuselage_diameter=1.2
    )
    fighter_mass = AircraftMass(
        empty_weight=8570, fuel_capacity=3200, payload_capacity=2400, max_takeoff_weight=19200
    )
    fighter = Aircraft("Fighter Jet", fighter_geom, fighter_mass)
    fighter.cd0 = 0.018  # Lower drag for fighter
    fighter.cl_max = 1.8  # Higher max lift
    
    return [airliner, ga_aircraft, fighter]
