"""
Aircraft Performance Analysis Module

This module provides comprehensive performance analysis capabilities
including range, endurance, climb performance, and optimization.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from .aircraft import Aircraft
from .flight_conditions import FlightConditions, AtmosphericConditions


class PerformanceAnalyzer:
    """
    Comprehensive aircraft performance analysis
    """
    
    def __init__(self, aircraft: Aircraft):
        self.aircraft = aircraft
        
    def calculate_range(self, cruise_altitude: float, cruise_speed: float, 
                       fuel_weight: float, sfc: float = 0.5e-4) -> float:
        """
        Calculate aircraft range using Breguet range equation
        
        Args:
            cruise_altitude: Cruise altitude in meters
            cruise_speed: Cruise speed in m/s
            fuel_weight: Available fuel weight in kg
            sfc: Specific fuel consumption in kg/N/s
            
        Returns:
            Range in kilometers
        """
        # Initial and final weights
        w_initial = self.aircraft.mass.max_takeoff_weight * 9.81  # N
        w_final = w_initial - fuel_weight * 9.81  # N
        
        # Flight conditions at cruise
        atm = AtmosphericConditions.standard_atmosphere(cruise_altitude)
        
        # Find optimal angle of attack for cruise (max L/D)
        best_aoa = self.find_optimal_angle_of_attack()
        cl = self.aircraft.calculate_lift_coefficient(best_aoa)
        cd = self.aircraft.calculate_drag_coefficient(cl)
        ld_ratio = cl / cd
        
        # Breguet range equation
        range_m = (cruise_speed / sfc) * ld_ratio * np.log(w_initial / w_final)
        return range_m / 1000  # Convert to km
    
    def calculate_endurance(self, altitude: float, fuel_weight: float, 
                          sfc: float = 0.5e-4) -> float:
        """
        Calculate maximum endurance
        
        Args:
            altitude: Flight altitude in meters
            fuel_weight: Available fuel weight in kg
            sfc: Specific fuel consumption in kg/N/s
            
        Returns:
            Endurance in hours
        """
        # Find conditions for maximum endurance (minimum power required)
        atm = AtmosphericConditions.standard_atmosphere(altitude)
        
        # For maximum endurance, fly at speed for minimum drag
        # This occurs at CL = sqrt(3 * CD0 / k)
        cl_endurance = np.sqrt(3 * self.aircraft.cd0 / self.aircraft.k)
        cd_endurance = self.aircraft.calculate_drag_coefficient(cl_endurance)
        
        # Calculate corresponding speed
        weight = self.aircraft.mass.max_takeoff_weight * 9.81
        v_endurance = np.sqrt(2 * weight / (atm.density * self.aircraft.geometry.wing_area * cl_endurance))
        
        # Power required
        power_required = weight * cd_endurance / cl_endurance * v_endurance
        
        # Endurance calculation (simplified)
        fuel_energy = fuel_weight * 43e6  # J (assuming jet fuel)
        engine_efficiency = 0.35  # Typical jet engine efficiency
        
        endurance_seconds = fuel_energy * engine_efficiency / power_required
        return endurance_seconds / 3600  # Convert to hours
    
    def find_optimal_angle_of_attack(self) -> float:
        """
        Find angle of attack for maximum L/D ratio
        
        Returns:
            Optimal angle of attack in degrees
        """
        angles = np.linspace(-5, 20, 100)
        best_ld = 0
        best_angle = 0
        
        for angle in angles:
            ld_ratio = self.aircraft.calculate_lift_drag_ratio(angle)
            if ld_ratio > best_ld:
                best_ld = ld_ratio
                best_angle = angle
                
        return best_angle
    
    def calculate_climb_performance(self, altitude_range: Tuple[float, float], 
                                  weight: float, thrust_available: float) -> Dict:
        """
        Calculate climb performance over altitude range
        
        Args:
            altitude_range: (min_alt, max_alt) in meters
            weight: Aircraft weight in kg
            thrust_available: Available thrust in N
            
        Returns:
            Dictionary with climb performance data
        """
        altitudes = np.linspace(altitude_range[0], altitude_range[1], 50)
        climb_rates = []
        climb_angles = []
        
        for alt in altitudes:
            atm = AtmosphericConditions.standard_atmosphere(alt)
            
            # Find best climb speed (typically 1.3 * V_stall)
            v_stall = np.sqrt(2 * weight * 9.81 / (atm.density * self.aircraft.geometry.wing_area * self.aircraft.cl_max))
            v_climb = 1.3 * v_stall
            
            # Calculate required thrust for level flight
            cl = 2 * weight * 9.81 / (atm.density * v_climb**2 * self.aircraft.geometry.wing_area)
            cd = self.aircraft.calculate_drag_coefficient(cl)
            thrust_required = 0.5 * atm.density * v_climb**2 * self.aircraft.geometry.wing_area * cd
            
            # Excess thrust and climb performance
            excess_thrust = thrust_available - thrust_required
            if excess_thrust > 0:
                climb_rate = excess_thrust * v_climb / (weight * 9.81)  # m/s
                climb_angle = np.degrees(np.arcsin(excess_thrust / (weight * 9.81)))
            else:
                climb_rate = 0
                climb_angle = 0
                
            climb_rates.append(climb_rate)
            climb_angles.append(climb_angle)
        
        return {
            'altitudes': altitudes,
            'climb_rates': np.array(climb_rates),
            'climb_angles': np.array(climb_angles),
            'service_ceiling': altitudes[np.where(np.array(climb_rates) <= 0.508)[0][0]] if any(np.array(climb_rates) <= 0.508) else max(altitudes)
        }
    
    def analyze_takeoff_performance(self, runway_length: float, obstacle_height: float = 15.24) -> Dict:
        """
        Analyze takeoff performance
        
        Args:
            runway_length: Available runway length in meters
            obstacle_height: Obstacle clearance height in meters (default 50 ft)
            
        Returns:
            Dictionary with takeoff performance data
        """
        # Simplified takeoff analysis
        atm = AtmosphericConditions.standard_atmosphere(0)  # Sea level
        weight = self.aircraft.mass.max_takeoff_weight * 9.81
        
        # Estimate takeoff speed (1.2 * V_stall)
        v_stall = np.sqrt(2 * weight / (atm.density * self.aircraft.geometry.wing_area * self.aircraft.cl_max))
        v_takeoff = 1.2 * v_stall
        
        # Ground roll distance (simplified)
        # Assuming constant acceleration and average thrust
        wing_loading = weight / self.aircraft.geometry.wing_area
        
        # Empirical relationship for ground roll
        if wing_loading < 2000:  # Light aircraft
            ground_roll = wing_loading * 0.05
        else:  # Heavy aircraft
            ground_roll = wing_loading * 0.08
            
        # Total takeoff distance (ground roll + climb to obstacle)
        climb_gradient = 0.06  # 6% climb gradient assumption
        climb_distance = obstacle_height / climb_gradient
        total_distance = ground_roll + climb_distance
        
        return {
            'v_stall': v_stall,
            'v_takeoff': v_takeoff,
            'ground_roll': ground_roll,
            'climb_distance': climb_distance,
            'total_distance': total_distance,
            'runway_adequate': total_distance <= runway_length
        }
    
    def generate_performance_envelope(self) -> Dict:
        """
        Generate comprehensive performance envelope
        
        Returns:
            Dictionary with performance envelope data
        """
        altitudes = np.linspace(0, 15000, 30)
        speeds = np.linspace(50, 300, 50)
        
        performance_map = {
            'altitudes': altitudes,
            'speeds': speeds,
            'power_required': np.zeros((len(altitudes), len(speeds))),
            'ld_ratios': np.zeros((len(altitudes), len(speeds))),
            'stall_speeds': np.zeros(len(altitudes))
        }
        
        weight = self.aircraft.mass.max_takeoff_weight * 9.81
        
        for i, alt in enumerate(altitudes):
            atm = AtmosphericConditions.standard_atmosphere(alt)
            
            # Stall speed at this altitude
            v_stall = np.sqrt(2 * weight / (atm.density * self.aircraft.geometry.wing_area * self.aircraft.cl_max))
            performance_map['stall_speeds'][i] = v_stall
            
            for j, speed in enumerate(speeds):
                if speed >= v_stall:
                    # Calculate lift coefficient required for level flight
                    cl_required = 2 * weight / (atm.density * speed**2 * self.aircraft.geometry.wing_area)
                    
                    if cl_required <= self.aircraft.cl_max:
                        cd = self.aircraft.calculate_drag_coefficient(cl_required)
                        ld_ratio = cl_required / cd
                        
                        # Power required for level flight
                        drag = 0.5 * atm.density * speed**2 * self.aircraft.geometry.wing_area * cd
                        power_required = drag * speed
                        
                        performance_map['ld_ratios'][i, j] = ld_ratio
                        performance_map['power_required'][i, j] = power_required
                    else:
                        performance_map['ld_ratios'][i, j] = 0
                        performance_map['power_required'][i, j] = np.inf
                else:
                    performance_map['ld_ratios'][i, j] = 0
                    performance_map['power_required'][i, j] = np.inf
        
        return performance_map
