"""
Flight Conditions Module

This module defines atmospheric conditions and flight parameters
for aircraft performance analysis.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class AtmosphericConditions:
    """Standard atmospheric conditions at different altitudes"""
    altitude: float  # meters
    temperature: float  # Kelvin
    pressure: float  # Pa
    density: float  # kg/m³
    speed_of_sound: float  # m/s
    
    @classmethod
    def standard_atmosphere(cls, altitude: float) -> 'AtmosphericConditions':
        """
        Calculate standard atmospheric conditions using ISA model
        
        Args:
            altitude: Altitude in meters
            
        Returns:
            AtmosphericConditions object
        """
        # Sea level conditions
        T0 = 288.15  # K
        P0 = 101325  # Pa
        rho0 = 1.225  # kg/m³
        a0 = 340.3  # m/s
        
        # Temperature lapse rate (troposphere)
        lapse_rate = -0.0065  # K/m
        
        if altitude <= 11000:  # Troposphere
            temperature = T0 + lapse_rate * altitude
            pressure = P0 * (temperature / T0) ** (-9.80665 / (287.0 * lapse_rate))
        else:  # Stratosphere (simplified)
            temp_11km = T0 + lapse_rate * 11000
            pressure_11km = P0 * (temp_11km / T0) ** (-9.80665 / (287.0 * lapse_rate))
            temperature = temp_11km  # Isothermal
            pressure = pressure_11km * np.exp(-9.80665 * (altitude - 11000) / (287.0 * temperature))
        
        density = pressure / (287.0 * temperature)
        speed_of_sound = np.sqrt(1.4 * 287.0 * temperature)
        
        return cls(altitude, temperature, pressure, density, speed_of_sound)


@dataclass
class FlightConditions:
    """Complete flight condition specification"""
    atmospheric: AtmosphericConditions
    airspeed: float  # m/s (true airspeed)
    angle_of_attack: float  # degrees
    bank_angle: float  # degrees
    load_factor: float  # g's
    
    @property
    def mach_number(self) -> float:
        """Calculate Mach number"""
        return self.airspeed / self.atmospheric.speed_of_sound
    
    @property
    def dynamic_pressure(self) -> float:
        """Calculate dynamic pressure (q)"""
        return 0.5 * self.atmospheric.density * self.airspeed**2
    
    @property
    def equivalent_airspeed(self) -> float:
        """Calculate equivalent airspeed"""
        rho_sl = 1.225  # Sea level density
        return self.airspeed * np.sqrt(self.atmospheric.density / rho_sl)
    
    @property
    def reynolds_number(self, characteristic_length: float = 1.0) -> float:
        """Calculate Reynolds number"""
        # Dynamic viscosity approximation
        mu = 1.458e-6 * self.atmospheric.temperature**1.5 / (self.atmospheric.temperature + 110.4)
        return self.atmospheric.density * self.airspeed * characteristic_length / mu


class FlightEnvelope:
    """
    Flight envelope analysis for aircraft performance limits
    """
    
    def __init__(self, aircraft):
        self.aircraft = aircraft
        
    def calculate_stall_speed(self, altitude: float, weight: float, load_factor: float = 1.0) -> float:
        """
        Calculate stall speed at given conditions
        
        Args:
            altitude: Altitude in meters
            weight: Aircraft weight in kg
            load_factor: Load factor (g's)
            
        Returns:
            Stall speed in m/s
        """
        atm = AtmosphericConditions.standard_atmosphere(altitude)
        weight_force = weight * 9.81  # Convert to Newtons
        
        # V_stall = sqrt(2 * W * n / (rho * S * CL_max))
        v_stall = np.sqrt(2 * weight_force * load_factor / 
                         (atm.density * self.aircraft.geometry.wing_area * self.aircraft.cl_max))
        return v_stall
    
    def calculate_service_ceiling(self, weight: float, min_climb_rate: float = 0.508) -> float:
        """
        Calculate service ceiling (altitude where climb rate drops to 100 ft/min)
        
        Args:
            weight: Aircraft weight in kg
            min_climb_rate: Minimum climb rate in m/s
            
        Returns:
            Service ceiling in meters
        """
        # Simplified calculation - would need engine model for accuracy
        # This is a rough approximation
        wing_loading = weight * 9.81 / self.aircraft.geometry.wing_area
        
        # Empirical relationship (very simplified)
        if wing_loading < 1000:  # Light aircraft
            ceiling = 4000 + (1000 - wing_loading) * 10
        else:  # Heavier aircraft
            ceiling = 4000 + (5000 - wing_loading) * 2
            
        return max(ceiling, 1000)  # Minimum 1000m ceiling
    
    def generate_v_n_diagram(self, altitude: float = 0, weight: float = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate V-n (velocity-load factor) diagram
        
        Args:
            altitude: Altitude in meters
            weight: Aircraft weight in kg (uses MTOW if None)
            
        Returns:
            Tuple of (velocities, load_factors) arrays
        """
        if weight is None:
            weight = self.aircraft.mass.max_takeoff_weight
            
        atm = AtmosphericConditions.standard_atmosphere(altitude)
        
        # Calculate key speeds
        v_stall = self.calculate_stall_speed(altitude, weight, 1.0)
        v_a = v_stall * np.sqrt(6.0)  # Maneuvering speed (assuming +6g limit)
        v_d = v_a * 1.4  # Dive speed (simplified)
        
        # Load factor limits (typical for transport category)
        n_pos_limit = 2.5
        n_neg_limit = -1.0
        
        # Generate envelope points
        velocities = []
        load_factors = []
        
        # Positive stall curve
        v_range = np.linspace(0, v_a, 50)
        for v in v_range:
            if v >= v_stall:
                n_max = (0.5 * atm.density * v**2 * self.aircraft.geometry.wing_area * 
                        self.aircraft.cl_max) / (weight * 9.81)
                n_max = min(n_max, n_pos_limit)
                velocities.append(v)
                load_factors.append(n_max)
        
        # Structural limit line
        velocities.extend([v_a, v_d])
        load_factors.extend([n_pos_limit, n_pos_limit])
        
        # Negative stall curve (simplified)
        v_stall_neg = v_stall * np.sqrt(abs(n_neg_limit))
        velocities.extend([v_d, v_stall_neg, 0])
        load_factors.extend([n_neg_limit, n_neg_limit, 0])
        
        return np.array(velocities), np.array(load_factors)


def create_test_conditions() -> List[FlightConditions]:
    """Create various test flight conditions"""
    
    conditions = []
    
    # Sea level conditions
    atm_sl = AtmosphericConditions.standard_atmosphere(0)
    conditions.append(FlightConditions(atm_sl, 100, 5.0, 0, 1.0))  # Cruise
    conditions.append(FlightConditions(atm_sl, 60, 15.0, 0, 1.0))   # Approach
    conditions.append(FlightConditions(atm_sl, 150, 0, 30, 2.0))    # Turn
    
    # High altitude conditions
    atm_high = AtmosphericConditions.standard_atmosphere(10000)
    conditions.append(FlightConditions(atm_high, 200, 2.0, 0, 1.0))  # High cruise
    conditions.append(FlightConditions(atm_high, 80, 10.0, 0, 1.0))  # Climb
    
    # Extreme conditions
    atm_extreme = AtmosphericConditions.standard_atmosphere(15000)
    conditions.append(FlightConditions(atm_extreme, 250, 0, 0, 1.0))  # High speed
    
    return conditions
