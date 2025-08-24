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
    """
    Aircraft geometric parameters that define the physical shape and dimensions.
    
    These parameters are fundamental to aircraft design and directly affect
    aerodynamic performance, structural requirements, and operational characteristics.
    
    Attributes:
        wing_span (float): Total wingspan from tip to tip in meters.
            - Larger wingspan generally improves lift efficiency and reduces induced drag
            - Affects ground handling, hangar requirements, and structural weight
            - Typical values: GA aircraft 8-15m, Airliners 30-80m, Fighters 8-15m
            
        wing_area (float): Total wing planform area in square meters.
            - Determines lift capability and stall speed for given weight
            - Affects wing loading (weight/area) which influences performance
            - Includes area of wing extensions but not control surfaces
            - Typical values: GA 10-20m², Airliners 100-500m², Fighters 25-80m²
            
        wing_chord (float): Average wing chord (front-to-back dimension) in meters.
            - Affects Reynolds number and boundary layer characteristics
            - Influences structural depth and fuel storage capacity
            - Related to wing area and span: Area ≈ Span × Chord (for rectangular wing)
            - Typical values: GA 1-2m, Airliners 3-8m, Fighters 2-5m
            
        aspect_ratio (float): Wing span squared divided by wing area (dimensionless).
            - Higher aspect ratio = better lift efficiency, lower induced drag
            - Lower aspect ratio = better roll rate, structural simplicity
            - Formula: AR = span²/area = span/average_chord
            - Typical values: Gliders 15-40, Airliners 8-12, Fighters 2-4
            
        sweep_angle (float): Wing leading edge sweep angle in degrees.
            - Positive sweep delays compressibility effects at high speed
            - Reduces effective aspect ratio and lift curve slope
            - Affects lateral stability and stall characteristics
            - Typical values: GA 0-5°, Airliners 20-35°, Fighters 20-60°
            
        dihedral_angle (float): Upward angle of wings from horizontal in degrees.
            - Positive dihedral improves lateral stability (roll stability)
            - Excessive dihedral can cause Dutch roll oscillations
            - Often combined with sweep for stability in high-speed aircraft
            - Typical values: GA 1-7°, Airliners 5-7°, Fighters 0-5°
            
        taper_ratio (float): Ratio of tip chord to root chord (dimensionless).
            - Affects lift distribution and induced drag
            - Lower taper ratio concentrates lift inboard, reducing bending moments
            - Optimal taper ratio for elliptical lift distribution ≈ 0.45
            - Typical values: 0.2-0.8, with 0.4-0.6 being common
            
        thickness_ratio (float): Maximum airfoil thickness as fraction of chord.
            - Thicker airfoils provide more structural depth and fuel volume
            - Thinner airfoils have lower drag at high speeds
            - Affects critical Mach number and compressibility drag rise
            - Typical values: GA 0.12-0.18, Airliners 0.10-0.14, Fighters 0.03-0.08
            
        fuselage_length (float): Total fuselage length in meters.
            - Affects passenger/cargo capacity and longitudinal stability
            - Longer fuselage provides more moment arm for tail effectiveness
            - Influences ground handling and airport gate compatibility
            - Typical values: GA 6-12m, Airliners 30-80m, Fighters 12-20m
            
        fuselage_diameter (float): Maximum fuselage diameter in meters.
            - Determines passenger cabin width and cargo volume
            - Affects drag due to frontal area and fineness ratio
            - Influences structural weight and pressurization loads
            - Typical values: GA 1-1.5m, Airliners 3-6m, Fighters 1-2m
    """
    wing_span: float
    wing_area: float
    wing_chord: float
    aspect_ratio: float
    sweep_angle: float
    dihedral_angle: float
    taper_ratio: float
    thickness_ratio: float
    fuselage_length: float
    fuselage_diameter: float


@dataclass
class AircraftMass:
    """
    Aircraft mass properties that define weight and balance characteristics.
    
    Mass properties are critical for performance calculations, structural design,
    and operational limitations. They directly affect takeoff/landing distances,
    climb performance, range, and handling characteristics.
    
    Attributes:
        empty_weight (float): Basic empty weight of the aircraft in kilograms.
            - Includes structure, engines, fixed equipment, and unusable fluids
            - Does not include crew, passengers, cargo, or usable fuel
            - Also called "Basic Empty Weight" (BEW) or "Manufacturer's Empty Weight"
            - Typical percentages of MTOW: GA 60-70%, Airliners 45-55%, Fighters 50-60%
            - Example values: GA 800-1200kg, Airliners 40,000-180,000kg, Fighters 8,000-15,000kg
            
        fuel_capacity (float): Maximum usable fuel weight in kilograms.
            - Determines maximum range and endurance capability
            - Includes fuel in wing tanks, fuselage tanks, and external tanks
            - Usable fuel is typically 95-98% of total tank capacity
            - Fuel density: Jet fuel ≈ 0.8 kg/L, Avgas ≈ 0.72 kg/L
            - Typical percentages of MTOW: GA 20-30%, Airliners 25-45%, Fighters 25-35%
            - Example values: GA 200-400kg, Airliners 20,000-150,000kg, Fighters 3,000-8,000kg
            
        payload_capacity (float): Maximum payload weight in kilograms.
            - Includes passengers, baggage, cargo, and crew
            - Limited by either volume or weight constraints
            - For passenger aircraft: ~75-100kg per passenger (including baggage)
            - Trade-off with fuel: more payload = less fuel = shorter range
            - Typical percentages of MTOW: GA 25-35%, Airliners 15-25%, Fighters 15-25%
            - Example values: GA 300-600kg, Airliners 15,000-50,000kg, Fighters 2,000-8,000kg
            
        max_takeoff_weight (float): Maximum certified takeoff weight in kilograms.
            - Also called Maximum Takeoff Mass (MTOM) or Gross Weight
            - Structural limit for takeoff operations
            - Sum of empty weight + fuel + payload cannot exceed this value
            - Determines runway length requirements and climb performance
            - Certified limit that cannot be exceeded for safety/legal reasons
            - Example values: GA 1,000-2,500kg, Airliners 50,000-600,000kg, Fighters 15,000-35,000kg
    
    Properties:
        operating_empty_weight: Same as empty_weight (standard terminology).
        max_landing_weight: Maximum weight for landing operations.
            - Typically 85-90% of MTOW due to structural landing loads
            - Aircraft may need to burn fuel or dump fuel before landing if overweight
    
    Design Relationships:
        - Wing Loading = MTOW / Wing Area (affects stall speed and maneuverability)
        - Power Loading = MTOW / Engine Power (affects climb performance)
        - Fuel Fraction = Fuel Weight / MTOW (affects range capability)
        - Payload Fraction = Payload / MTOW (affects mission utility)
    """
    empty_weight: float
    fuel_capacity: float
    payload_capacity: float
    max_takeoff_weight: float
    
    @property
    def operating_empty_weight(self) -> float:
        """Operating empty weight (same as empty weight in this simplified model)."""
        return self.empty_weight
    
    @property
    def max_landing_weight(self) -> float:
        """
        Maximum landing weight (typically 85% of MTOW).
        
        Landing weight is limited by structural loads during touchdown.
        Aircraft may need to burn fuel or dump fuel if landing overweight.
        """
        return self.max_takeoff_weight * 0.85  # Typical assumption


class Aircraft:
    """
    Main aircraft class for design exploration and aerodynamic analysis.
    
    This class combines geometric and mass properties with aerodynamic models
    to enable comprehensive aircraft performance analysis, design optimization,
    and flight condition testing.
    
    The aerodynamic model uses simplified but physically-based relationships
    suitable for conceptual design and educational purposes.
    
    Attributes:
        name (str): Aircraft designation or model name.
        geometry (AircraftGeometry): Physical dimensions and shape parameters.
        mass (AircraftMass): Weight and balance properties.
        
    Aerodynamic Coefficients:
        cd0 (float): Zero-lift drag coefficient (parasitic drag).
            - Represents drag when lift = 0 (form drag + skin friction)
            - Depends on aircraft cleanliness, surface roughness, and shape
            - Typical values: Clean GA 0.025-0.035, Airliners 0.015-0.025, Fighters 0.015-0.025
            - Lower values indicate more aerodynamically efficient design
            
        k (float): Induced drag factor (dimensionless).
            - Relates induced drag to lift: CD_induced = k × CL²
            - Inversely related to aspect ratio and span efficiency
            - Formula: k = 1/(π × AR × e), where e is span efficiency (≈0.8)
            - Typical values: 0.03-0.08 (lower is better)
            
        cl_max (float): Maximum lift coefficient before stall.
            - Determines minimum speed for sustained flight
            - Depends on airfoil shape, flaps, and flow conditions
            - Higher values allow lower stall speeds
            - Typical values: GA 1.4-1.8, Airliners 1.6-2.5 (with flaps), Fighters 1.2-1.8
            
        cl_alpha (float): Lift curve slope (per radian).
            - Rate of lift coefficient change with angle of attack
            - Theoretical maximum: 2π ≈ 6.28 per radian
            - Reduced by finite aspect ratio, sweep, and compressibility
            - Formula: cl_α = 2π / (1 + 2/AR) for unswept wings
            - Typical values: 4-6 per radian
    
    Methods:
        calculate_lift_coefficient: Compute CL for given angle of attack
        calculate_drag_coefficient: Compute CD using drag polar
        calculate_lift_drag_ratio: Compute L/D ratio for performance analysis
        get_design_summary: Return key design parameters and ratios
    
    Design Philosophy:
        This class uses simplified aerodynamic models that capture the essential
        physics while remaining computationally efficient. The models are based on:
        - Classical thin airfoil theory for lift
        - Drag polar representation (CD = CD0 + k×CL²)
        - Empirical corrections for finite wing effects
        
    These approximations are suitable for:
        - Conceptual design studies
        - Educational purposes
        - Comparative analysis between designs
        - Optimization studies
        
    For detailed design, more sophisticated CFD or wind tunnel data would be needed.
    """
    
    def __init__(self, name: str, geometry: AircraftGeometry, mass: AircraftMass):
        """
        Initialize aircraft with geometry, mass, and aerodynamic properties.
        
        Args:
            name: Aircraft designation or model name
            geometry: Physical dimensions and shape parameters
            mass: Weight and balance properties
        """
        self.name = name
        self.geometry = geometry
        self.mass = mass
        
        # Aerodynamic coefficients (estimated from geometry)
        self.cd0 = 0.025  # Zero-lift drag coefficient
        self.k = 1 / (np.pi * geometry.aspect_ratio * 0.8)  # Induced drag factor
        self.cl_max = 1.6  # Maximum lift coefficient
        self.cl_alpha = 2 * np.pi / (1 + 2/geometry.aspect_ratio)  # Lift curve slope
        
    def calculate_lift_coefficient(self, angle_of_attack: float) -> float:
        """
        Calculate lift coefficient based on angle of attack using linear theory.
        
        Uses the lift curve slope to relate angle of attack to lift coefficient,
        with a maximum limit to represent stall conditions.
        
        Physics:
            - Based on thin airfoil theory: CL = cl_α × α
            - Valid for attached flow (before stall)
            - Assumes small angle approximation
            - Stall occurs when CL exceeds cl_max
        
        Args:
            angle_of_attack (float): Angle of attack in degrees.
                - Positive values increase lift
                - Typical operating range: -5° to +15°
                - Stall typically occurs at 12-18° for most airfoils
        
        Returns:
            float: Lift coefficient (dimensionless).
                - Positive values indicate upward lift
                - Limited to cl_max to represent stall
                - Typical cruise values: 0.2-0.8
        
        Note:
            This is a simplified model. Real aircraft have:
            - Non-linear behavior near stall
            - Hysteresis effects
            - Reynolds number dependencies
            - Compressibility effects at high speed
        """
        alpha_rad = np.radians(angle_of_attack)
        cl = self.cl_alpha * alpha_rad
        return min(cl, self.cl_max)
    
    def calculate_drag_coefficient(self, lift_coefficient: float) -> float:
        """
        Calculate total drag coefficient using the drag polar equation.
        
        The drag polar represents total drag as the sum of:
        - Parasitic drag (independent of lift)
        - Induced drag (proportional to lift squared)
        
        Physics:
            - CD = CD0 + k×CL²
            - CD0: zero-lift drag (form drag + skin friction)
            - k×CL²: induced drag from lift generation
            - Minimum drag occurs at CL = 0
            - Drag increases quadratically with lift
        
        Args:
            lift_coefficient (float): Current lift coefficient.
                - Should be positive for normal flight
                - Higher values increase induced drag
                - Typical range: 0.1-1.5
        
        Returns:
            float: Total drag coefficient (dimensionless).
                - Always positive
                - Minimum value is cd0
                - Increases with lift coefficient squared
        
        Applications:
            - Performance analysis (range, endurance)
            - Optimization (finding best L/D ratio)
            - Power/thrust requirement calculations
        """
        return self.cd0 + self.k * lift_coefficient**2
    
    def calculate_lift_drag_ratio(self, angle_of_attack: float) -> float:
        """
        Calculate lift-to-drag ratio (L/D), a key measure of aerodynamic efficiency.
        
        L/D ratio indicates how much lift is generated per unit of drag,
        directly affecting aircraft performance in all flight phases.
        
        Significance:
            - Higher L/D = better fuel efficiency
            - Maximum L/D occurs at optimal angle of attack
            - Critical for range and endurance calculations
            - Determines glide ratio in unpowered flight
        
        Physics:
            - L/D = CL/CD = CL/(CD0 + k×CL²)
            - Maximum L/D occurs when CL = √(CD0/k)
            - At max L/D: induced drag = parasitic drag
        
        Args:
            angle_of_attack (float): Angle of attack in degrees.
                - Optimal AoA typically 4-8° for most aircraft
                - Too low: high parasitic drag dominance
                - Too high: high induced drag dominance
        
        Returns:
            float: Lift-to-drag ratio (dimensionless).
                - Higher values indicate better efficiency
                - Typical max values: Gliders 40-60, Airliners 15-20, Fighters 8-15
                - Zero if drag coefficient is zero (theoretical only)
        
        Applications:
            - Cruise performance optimization
            - Glide distance calculations
            - Fuel consumption analysis
            - Aircraft design comparison
        """
        cl = self.calculate_lift_coefficient(angle_of_attack)
        cd = self.calculate_drag_coefficient(cl)
        return cl / cd if cd > 0 else 0
    
    def get_design_summary(self) -> Dict:
        """
        Get a comprehensive summary of key aircraft design parameters and ratios.
        
        Returns important design metrics that characterize aircraft performance
        and provide insight into design trade-offs and operational characteristics.
        
        Returns:
            Dict: Dictionary containing key design parameters:
                - name: Aircraft designation
                - wing_span: Wingspan in meters
                - wing_area: Wing planform area in m²
                - aspect_ratio: Span²/Area ratio
                - max_takeoff_weight: MTOW in kg
                - wing_loading: Weight per unit wing area (N/m²)
                - cd0: Zero-lift drag coefficient
                - k_factor: Induced drag factor
        
        Design Insights:
            - wing_loading: Higher values → higher stall speed, better penetration
            - aspect_ratio: Higher values → better efficiency, lower maneuverability
            - cd0: Lower values → cleaner design, less parasitic drag
            - k_factor: Lower values → more efficient lift generation
        """
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
    """
    Create three representative aircraft designs for comparison and analysis.
    
    This function generates aircraft representing different design philosophies
    and mission requirements, demonstrating the trade-offs in aircraft design.
    
    Returns:
        List[Aircraft]: Three aircraft representing different categories:
            1. Commercial Airliner - Efficiency and passenger capacity focused
            2. General Aviation - Versatility and cost-effectiveness focused  
            3. Fighter Jet - Performance and maneuverability focused
    
    Design Philosophy Comparison:
        Commercial Airliner:
            - High aspect ratio for fuel efficiency
            - Moderate sweep for cruise speed
            - Large size for passenger capacity
            - Conservative design for safety and economics
            
        General Aviation:
            - Balanced design for versatility
            - Straight wing for simplicity and low-speed handling
            - Smaller size for cost-effectiveness
            - Robust design for varied operating conditions
            
        Fighter Jet:
            - Low aspect ratio for maneuverability
            - High sweep for supersonic capability
            - Thin airfoils for high-speed performance
            - Optimized for performance over efficiency
    """
    
    # Commercial airliner (Boeing 737-like design)
    # Design priorities: fuel efficiency, passenger capacity, operational economics
    airliner_geom = AircraftGeometry(
        wing_span=35.8,        # Large span for high aspect ratio and efficiency
        wing_area=125.0,       # Sized for cruise lift requirements
        wing_chord=3.5,        # Moderate chord for structural depth
        aspect_ratio=10.2,     # High AR for low induced drag
        sweep_angle=25.0,      # Moderate sweep for cruise Mach 0.8
        dihedral_angle=6.0,    # Positive dihedral for lateral stability
        taper_ratio=0.3,       # Tapered wing for structural efficiency
        thickness_ratio=0.12,  # Thick enough for fuel storage and structure
        fuselage_length=39.5,  # Long for passenger capacity
        fuselage_diameter=3.8  # Wide for twin-aisle comfort
    )
    airliner_mass = AircraftMass(
        empty_weight=41000,      # Typical for 150-seat aircraft
        fuel_capacity=20000,     # ~25% of MTOW for medium-haul range
        payload_capacity=18000,  # ~120 passengers + baggage
        max_takeoff_weight=79000 # Balanced for performance and economics
    )
    airliner = Aircraft("Commercial Airliner", airliner_geom, airliner_mass)
    # Default aerodynamic coefficients are appropriate for clean airliner design
    
    # General aviation aircraft (Cessna 172-like design)
    # Design priorities: versatility, cost-effectiveness, ease of handling
    ga_geom = AircraftGeometry(
        wing_span=11.0,        # Moderate span for hangar compatibility
        wing_area=16.2,        # Sized for low stall speed
        wing_chord=1.5,        # Simple rectangular-like planform
        aspect_ratio=7.5,      # Good compromise between efficiency and cost
        sweep_angle=0.0,       # Straight wing for simplicity and low-speed handling
        dihedral_angle=1.0,    # Minimal dihedral for basic stability
        taper_ratio=0.6,       # Slight taper for efficiency without complexity
        thickness_ratio=0.15,  # Thick airfoil for structure and docile stall
        fuselage_length=8.3,   # Compact for 4-seat configuration
        fuselage_diameter=1.2  # Narrow but adequate for small cabin
    )
    ga_mass = AircraftMass(
        empty_weight=760,        # Light structure for cost and performance
        fuel_capacity=200,       # ~17% of MTOW for local/regional flights
        payload_capacity=400,    # 4 people + baggage
        max_takeoff_weight=1157  # Light sport/utility category
    )
    ga_aircraft = Aircraft("General Aviation", ga_geom, ga_mass)
    # Default coefficients appropriate for typical GA aircraft
    
    # Fighter jet (F-16-like design)
    # Design priorities: performance, maneuverability, speed capability
    fighter_geom = AircraftGeometry(
        wing_span=9.96,        # Compact span for high roll rate
        wing_area=27.9,        # Moderate area for balanced wing loading
        wing_chord=3.2,        # Large chord for thin airfoil
        aspect_ratio=3.6,      # Low AR for maneuverability and strength
        sweep_angle=40.0,      # High sweep for supersonic capability
        dihedral_angle=0.0,    # No dihedral (anhedral on real F-16)
        taper_ratio=0.2,       # Highly tapered for supersonic efficiency
        thickness_ratio=0.04,  # Very thin for high-speed performance
        fuselage_length=15.0,  # Compact but houses large engine
        fuselage_diameter=1.2  # Narrow for low drag
    )
    fighter_mass = AircraftMass(
        empty_weight=8570,       # Heavy due to structure and systems
        fuel_capacity=3200,      # ~17% of MTOW for combat radius
        payload_capacity=2400,   # Weapons and equipment
        max_takeoff_weight=19200 # High thrust-to-weight ratio capability
    )
    fighter = Aircraft("Fighter Jet", fighter_geom, fighter_mass)
    
    # Specialized aerodynamic coefficients for fighter performance
    fighter.cd0 = 0.018      # Lower parasitic drag due to clean design
    fighter.cl_max = 1.8     # Higher max lift due to advanced high-lift devices
    
    return [airliner, ga_aircraft, fighter]
