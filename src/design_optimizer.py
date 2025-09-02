"""
Aircraft Design Optimization Module

This module provides optimization algorithms for aircraft design parameters
to meet specific performance requirements.
"""

import numpy as np
from scipy.optimize import minimize, differential_evolution
from typing import Dict, List, Tuple, Callable, Optional

# Handle imports for both package and direct execution
try:
    from .aircraft import Aircraft, AircraftGeometry, AircraftMass
    from .performance_analysis import PerformanceAnalyzer
except ImportError:
    from aircraft import Aircraft, AircraftGeometry, AircraftMass
    from performance_analysis import PerformanceAnalyzer


class DesignObjective:
    """Base class for design objectives"""
    
    def __init__(self, name: str, weight: float = 1.0, target: Optional[float] = None):
        self.name = name
        self.weight = weight
        self.target = target
    
    def evaluate(self, aircraft: Aircraft) -> float:
        """Evaluate objective function for given aircraft"""
        raise NotImplementedError


class MaximizeRange(DesignObjective):
    """Objective to maximize aircraft range"""
    
    def __init__(self, cruise_altitude: float = 10000, cruise_speed: float = 200, 
                 fuel_fraction: float = 0.3, weight: float = 1.0):
        super().__init__("Maximize Range", weight)
        self.cruise_altitude = cruise_altitude
        self.cruise_speed = cruise_speed
        self.fuel_fraction = fuel_fraction
    
    def evaluate(self, aircraft: Aircraft) -> float:
        analyzer = PerformanceAnalyzer(aircraft)
        fuel_weight = aircraft.mass.max_takeoff_weight * self.fuel_fraction
        range_km = analyzer.calculate_range(self.cruise_altitude, self.cruise_speed, fuel_weight)
        return -range_km  # Negative because we minimize


class MinimizeFuelConsumption(DesignObjective):
    """Objective to minimize fuel consumption for given mission"""
    
    def __init__(self, mission_range: float = 1000, cruise_altitude: float = 10000, weight: float = 1.0):
        super().__init__("Minimize Fuel Consumption", weight)
        self.mission_range = mission_range
        self.cruise_altitude = cruise_altitude
    
    def evaluate(self, aircraft: Aircraft) -> float:
        analyzer = PerformanceAnalyzer(aircraft)
        
        # Find optimal cruise conditions
        best_aoa = analyzer.find_optimal_angle_of_attack()
        cl = aircraft.calculate_lift_coefficient(best_aoa)
        cd = aircraft.calculate_drag_coefficient(cl)
        ld_ratio = cl / cd
        
        # Estimate fuel consumption (simplified)
        sfc = 0.5e-4  # Specific fuel consumption
        weight_n = aircraft.mass.max_takeoff_weight * 9.81
        
        # Fuel required for mission (Breguet equation rearranged)
        fuel_fraction = 1 - np.exp(-self.mission_range * 1000 * sfc / (200 * ld_ratio))  # Assuming 200 m/s cruise
        fuel_weight = aircraft.mass.max_takeoff_weight * fuel_fraction
        
        return fuel_weight


class MaximizeLiftToDrag(DesignObjective):
    """Objective to maximize lift-to-drag ratio"""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("Maximize L/D", weight)
    
    def evaluate(self, aircraft: Aircraft) -> float:
        analyzer = PerformanceAnalyzer(aircraft)
        best_aoa = analyzer.find_optimal_angle_of_attack()
        max_ld = aircraft.calculate_lift_drag_ratio(best_aoa)
        return -max_ld  # Negative because we minimize


class DesignConstraint:
    """Base class for design constraints"""
    
    def __init__(self, name: str):
        self.name = name
    
    def evaluate(self, aircraft: Aircraft) -> float:
        """
        Evaluate constraint. Return 0 if satisfied, positive if violated.
        """
        raise NotImplementedError


class StallSpeedConstraint(DesignConstraint):
    """Constraint on maximum stall speed"""
    
    def __init__(self, max_stall_speed: float, altitude: float = 0):
        super().__init__(f"Stall Speed <= {max_stall_speed} m/s")
        self.max_stall_speed = max_stall_speed
        self.altitude = altitude
    
    def evaluate(self, aircraft: Aircraft) -> float:
        try:
            from .flight_conditions import AtmosphericConditions
        except ImportError:
            from flight_conditions import AtmosphericConditions
        
        atm = AtmosphericConditions.standard_atmosphere(self.altitude)
        weight = aircraft.mass.max_takeoff_weight * 9.81
        
        v_stall = np.sqrt(2 * weight / (atm.density * aircraft.geometry.wing_area * aircraft.cl_max))
        return max(0, v_stall - self.max_stall_speed)


class TakeoffDistanceConstraint(DesignConstraint):
    """Constraint on takeoff distance"""
    
    def __init__(self, max_takeoff_distance: float):
        super().__init__(f"Takeoff Distance <= {max_takeoff_distance} m")
        self.max_takeoff_distance = max_takeoff_distance
    
    def evaluate(self, aircraft: Aircraft) -> float:
        analyzer = PerformanceAnalyzer(aircraft)
        takeoff_data = analyzer.analyze_takeoff_performance(self.max_takeoff_distance * 2)  # Give extra runway for calculation
        return max(0, takeoff_data['total_distance'] - self.max_takeoff_distance)


class WingLoadingConstraint(DesignConstraint):
    """Constraint on wing loading"""
    
    def __init__(self, max_wing_loading: float):
        super().__init__(f"Wing Loading <= {max_wing_loading} N/m²")
        self.max_wing_loading = max_wing_loading
    
    def evaluate(self, aircraft: Aircraft) -> float:
        wing_loading = aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area
        return max(0, wing_loading - self.max_wing_loading)


class DesignOptimizer:
    """
    Multi-objective aircraft design optimizer
    """
    
    def __init__(self):
        self.objectives: List[DesignObjective] = []
        self.constraints: List[DesignConstraint] = []
        self.design_variables = {}
        self.bounds = {}
    
    def add_objective(self, objective: DesignObjective):
        """Add optimization objective"""
        self.objectives.append(objective)
    
    def add_constraint(self, constraint: DesignConstraint):
        """Add design constraint"""
        self.constraints.append(constraint)
    
    def set_design_variables(self, variables: Dict[str, Tuple[float, float]]):
        """
        Set design variables and their bounds
        
        Args:
            variables: Dictionary of {variable_name: (min_value, max_value)}
        """
        self.design_variables = variables
        self.bounds = list(variables.values())
    
    def create_aircraft_from_variables(self, x: np.ndarray, base_aircraft: Aircraft) -> Aircraft:
        """
        Create aircraft from design variables
        
        Args:
            x: Array of design variable values
            base_aircraft: Base aircraft to modify
            
        Returns:
            Modified aircraft
        """
        # Create copies of geometry and mass
        geom = base_aircraft.geometry
        mass = base_aircraft.mass
        
        # Map variables to aircraft parameters
        var_names = list(self.design_variables.keys())
        
        # Create new geometry with modified parameters
        geom_dict = {
            'wing_span': geom.wing_span,
            'wing_area': geom.wing_area,
            'wing_chord': geom.wing_chord,
            'aspect_ratio': geom.aspect_ratio,
            'sweep_angle': geom.sweep_angle,
            'dihedral_angle': geom.dihedral_angle,
            'taper_ratio': geom.taper_ratio,
            'thickness_ratio': geom.thickness_ratio,
            'fuselage_length': geom.fuselage_length,
            'fuselage_diameter': geom.fuselage_diameter
        }
        
        mass_dict = {
            'empty_weight': mass.empty_weight,
            'fuel_capacity': mass.fuel_capacity,
            'payload_capacity': mass.payload_capacity,
            'max_takeoff_weight': mass.max_takeoff_weight
        }
        
        # Update parameters based on design variables
        for i, var_name in enumerate(var_names):
            if var_name in geom_dict:
                geom_dict[var_name] = x[i]
            elif var_name in mass_dict:
                mass_dict[var_name] = x[i]
        
        # Ensure consistency in geometry
        if 'wing_span' in geom_dict and 'wing_area' in geom_dict:
            geom_dict['aspect_ratio'] = geom_dict['wing_span']**2 / geom_dict['wing_area']
            geom_dict['wing_chord'] = geom_dict['wing_area'] / geom_dict['wing_span']
        
        new_geom = AircraftGeometry(**geom_dict)
        new_mass = AircraftMass(**mass_dict)
        
        return Aircraft(base_aircraft.name + "_optimized", new_geom, new_mass)
    
    def objective_function(self, x: np.ndarray, base_aircraft: Aircraft) -> float:
        """
        Combined objective function
        
        Args:
            x: Design variable values
            base_aircraft: Base aircraft design
            
        Returns:
            Objective function value
        """
        try:
            aircraft = self.create_aircraft_from_variables(x, base_aircraft)
            
            # Calculate weighted sum of objectives
            total_objective = 0
            for obj in self.objectives:
                total_objective += obj.weight * obj.evaluate(aircraft)
            
            # Add penalty for constraint violations
            penalty = 0
            for constraint in self.constraints:
                violation = constraint.evaluate(aircraft)
                penalty += 1000 * violation**2  # Quadratic penalty
            
            return total_objective + penalty
            
        except Exception as e:
            # Return large penalty for invalid designs
            return 1e6
    
    def optimize(self, base_aircraft: Aircraft, method: str = 'differential_evolution') -> Dict:
        """
        Perform design optimization
        
        Args:
            base_aircraft: Starting aircraft design
            method: Optimization method ('differential_evolution' or 'minimize')
            
        Returns:
            Optimization results
        """
        if not self.design_variables:
            raise ValueError("No design variables specified")
        
        if method == 'differential_evolution':
            result = differential_evolution(
                self.objective_function,
                self.bounds,
                args=(base_aircraft,),
                maxiter=100,
                popsize=15,
                seed=42
            )
        else:
            # Use initial guess as midpoint of bounds
            x0 = [(b[0] + b[1]) / 2 for b in self.bounds]
            result = minimize(
                self.objective_function,
                x0,
                args=(base_aircraft,),
                bounds=self.bounds,
                method='L-BFGS-B'
            )
        
        # Create optimized aircraft
        optimized_aircraft = self.create_aircraft_from_variables(result.x, base_aircraft)
        
        # Evaluate final performance
        final_objectives = {}
        for obj in self.objectives:
            final_objectives[obj.name] = obj.evaluate(optimized_aircraft)
        
        final_constraints = {}
        for constraint in self.constraints:
            final_constraints[constraint.name] = constraint.evaluate(optimized_aircraft)
        
        return {
            'success': result.success,
            'optimized_aircraft': optimized_aircraft,
            'design_variables': dict(zip(self.design_variables.keys(), result.x)),
            'objective_value': result.fun,
            'objectives': final_objectives,
            'constraints': final_constraints,
            'optimization_result': result
        }
