#!/usr/bin/env python3
"""
Aircraft Design Examples Script

This script demonstrates the capabilities of the aircraft design system
including design analysis, performance evaluation, optimization, and visualization.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from src import (
    create_sample_aircraft, create_test_conditions, FlightEnvelope,
    PerformanceAnalyzer, DesignOptimizer, MaximizeRange, MaximizeLiftToDrag,
    StallSpeedConstraint, TakeoffDistanceConstraint, AircraftVisualizer,
    compare_aircraft_designs
)


def example_basic_analysis():
    """
    Example 1: Basic aircraft analysis and comparison
    """
    print("="*60)
    print("EXAMPLE 1: BASIC AIRCRAFT ANALYSIS")
    print("="*60)
    
    # Create sample aircraft
    aircraft_list = create_sample_aircraft()
    
    for aircraft in aircraft_list:
        print(f"\n--- {aircraft.name} ---")
        
        # Basic design summary
        summary = aircraft.get_design_summary()
        print(f"Wing Span: {summary['wing_span']:.1f} m")
        print(f"Wing Area: {summary['wing_area']:.1f} m²")
        print(f"Aspect Ratio: {summary['aspect_ratio']:.1f}")
        print(f"Wing Loading: {summary['wing_loading']:.1f} N/m²")
        print(f"Max Takeoff Weight: {summary['max_takeoff_weight']:.0f} kg")
        
        # Performance analysis
        analyzer = PerformanceAnalyzer(aircraft)
        
        # Find optimal angle of attack
        optimal_aoa = analyzer.find_optimal_angle_of_attack()
        max_ld = aircraft.calculate_lift_drag_ratio(optimal_aoa)
        print(f"Optimal AoA: {optimal_aoa:.1f}°")
        print(f"Max L/D Ratio: {max_ld:.1f}")
        
        # Calculate range and endurance
        fuel_weight = aircraft.mass.fuel_capacity
        range_km = analyzer.calculate_range(10000, 200, fuel_weight)
        endurance_hrs = analyzer.calculate_endurance(10000, fuel_weight)
        print(f"Estimated Range: {range_km:.0f} km")
        print(f"Estimated Endurance: {endurance_hrs:.1f} hours")
        
        # Takeoff performance
        takeoff_data = analyzer.analyze_takeoff_performance(3000)  # 3km runway
        print(f"Takeoff Distance: {takeoff_data['total_distance']:.0f} m")
        print(f"Stall Speed: {takeoff_data['v_stall']:.1f} m/s")


def example_flight_conditions_testing():
    """
    Example 2: Testing various flight conditions
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: FLIGHT CONDITIONS TESTING")
    print("="*60)
    
    # Create test aircraft (use commercial airliner)
    aircraft_list = create_sample_aircraft()
    airliner = aircraft_list[0]  # Commercial airliner
    
    # Create various flight conditions
    test_conditions = create_test_conditions()
    
    print(f"\nTesting {airliner.name} under various flight conditions:")
    print("-" * 60)
    
    for i, condition in enumerate(test_conditions):
        print(f"\nCondition {i+1}:")
        print(f"  Altitude: {condition.atmospheric.altitude:.0f} m")
        print(f"  Airspeed: {condition.airspeed:.1f} m/s")
        print(f"  Temperature: {condition.atmospheric.temperature:.1f} K")
        print(f"  Density: {condition.atmospheric.density:.3f} kg/m³")
        print(f"  Mach Number: {condition.mach_number:.3f}")
        print(f"  Dynamic Pressure: {condition.dynamic_pressure:.1f} Pa")
        print(f"  Load Factor: {condition.load_factor:.1f} g")
        
        # Calculate required lift coefficient for this condition
        weight = airliner.mass.max_takeoff_weight * 9.81
        required_cl = (2 * weight * condition.load_factor / 
                      (condition.atmospheric.density * condition.airspeed**2 * airliner.geometry.wing_area))
        
        if required_cl <= airliner.cl_max:
            cd = airliner.calculate_drag_coefficient(required_cl)
            ld_ratio = required_cl / cd
            print(f"  Required CL: {required_cl:.3f} (feasible)")
            print(f"  L/D Ratio: {ld_ratio:.1f}")
        else:
            print(f"  Required CL: {required_cl:.3f} (EXCEEDS CL_MAX = {airliner.cl_max})")


def example_performance_optimization():
    """
    Example 3: Aircraft design optimization
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: DESIGN OPTIMIZATION")
    print("="*60)
    
    # Use general aviation aircraft as base design
    aircraft_list = create_sample_aircraft()
    base_aircraft = aircraft_list[1]  # General aviation
    
    print(f"Optimizing design based on: {base_aircraft.name}")
    print(f"Base design summary:")
    summary = base_aircraft.get_design_summary()
    for key, value in summary.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Set up optimizer
    optimizer = DesignOptimizer()
    
    # Add objectives
    optimizer.add_objective(MaximizeRange(cruise_altitude=8000, cruise_speed=150, weight=2.0))
    optimizer.add_objective(MaximizeLiftToDrag(weight=1.0))
    
    # Add constraints
    optimizer.add_constraint(StallSpeedConstraint(max_stall_speed=30))  # 30 m/s max stall speed
    optimizer.add_constraint(TakeoffDistanceConstraint(max_takeoff_distance=800))  # 800m runway
    
    # Set design variables (allow wing area and aspect ratio to vary)
    optimizer.set_design_variables({
        'wing_area': (12.0, 25.0),      # m²
        'aspect_ratio': (6.0, 12.0),    # dimensionless
        'max_takeoff_weight': (1000, 1500)  # kg
    })
    
    print("\nRunning optimization...")
    try:
        result = optimizer.optimize(base_aircraft, method='differential_evolution')
        
        if result['success']:
            print("Optimization successful!")
            print("\nOptimized design variables:")
            for var, value in result['design_variables'].items():
                print(f"  {var}: {value:.2f}")
            
            print("\nObjective improvements:")
            for obj_name, obj_value in result['objectives'].items():
                print(f"  {obj_name}: {obj_value:.3f}")
            
            print("\nConstraint violations:")
            for const_name, violation in result['constraints'].items():
                status = "SATISFIED" if violation < 1e-6 else f"VIOLATED ({violation:.3f})"
                print(f"  {const_name}: {status}")
            
            # Compare original vs optimized
            optimized_aircraft = result['optimized_aircraft']
            print(f"\nComparison:")
            print(f"{'Parameter':<20} {'Original':<12} {'Optimized':<12} {'Change':<12}")
            print("-" * 56)
            
            orig_summary = base_aircraft.get_design_summary()
            opt_summary = optimized_aircraft.get_design_summary()
            
            for key in ['wing_area', 'aspect_ratio', 'wing_loading']:
                if key in orig_summary and key in opt_summary:
                    orig_val = orig_summary[key]
                    opt_val = opt_summary[key]
                    change = ((opt_val - orig_val) / orig_val) * 100
                    print(f"{key:<20} {orig_val:<12.2f} {opt_val:<12.2f} {change:+.1f}%")
        
        else:
            print("Optimization failed!")
            print(f"Reason: {result.get('message', 'Unknown')}")
    
    except Exception as e:
        print(f"Optimization error: {e}")


def example_visualization():
    """
    Example 4: Comprehensive visualization
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: VISUALIZATION EXAMPLES")
    print("="*60)
    
    # Create sample aircraft
    aircraft_list = create_sample_aircraft()
    
    # Create organized folder structure
    visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
    reference_dir = os.path.join(visualizations_dir, 'reference_aircraft')
    comparisons_dir = os.path.join(visualizations_dir, 'comparisons')
    os.makedirs(comparisons_dir, exist_ok=True)
    
    aircraft_folder_names = ['commercial_airliner', 'general_aviation', 'fighter_jet']
    
    print("Generating visualizations...")
    
    # Individual aircraft analysis
    for i, (aircraft, folder_name) in enumerate(zip(aircraft_list, aircraft_folder_names)):
        print(f"\nGenerating plots for {aircraft.name}...")
        
        # Create aircraft-specific folder
        aircraft_folder = os.path.join(reference_dir, folder_name)
        os.makedirs(aircraft_folder, exist_ok=True)
        
        # Create visualizer and set output folder
        visualizer = AircraftVisualizer(aircraft)
        visualizer.set_output_folder(aircraft_folder)
        
        # Create plots (save to aircraft-specific folder)
        try:
            # Drag polar
            fig1 = visualizer.plot_drag_polar('drag_polar.png')
            print(f"  - Drag polar saved in '{folder_name}/'")
            plt.close(fig1)
            
            # Lift/drag vs AoA
            fig2 = visualizer.plot_lift_drag_vs_aoa('ld_vs_aoa.png')
            print(f"  - L/D vs AoA saved in '{folder_name}/'")
            plt.close(fig2)
            
            # V-n diagram
            fig3 = visualizer.plot_v_n_diagram(save_path='vn_diagram.png')
            print(f"  - V-n diagram saved in '{folder_name}/'")
            plt.close(fig3)
            
            # Performance envelope
            fig4 = visualizer.plot_performance_envelope('performance_envelope.png')
            print(f"  - Performance envelope saved in '{folder_name}/'")
            plt.close(fig4)
            
            # Climb performance (with estimated thrust)
            thrust_estimates = [200000, 5000, 120000]  # N, rough estimates
            fig5 = visualizer.plot_climb_performance(thrust_estimates[i], 'climb_performance.png')
            print(f"  - Climb performance saved in '{folder_name}/'")
            plt.close(fig5)
            
        except Exception as e:
            print(f"  Error generating plots for {aircraft.name}: {e}")
    
    # Comparison plot
    try:
        print("\nGenerating comparison plot...")
        fig_comp = compare_aircraft_designs(aircraft_list, None)  # Don't auto-save
        comparison_path = os.path.join(comparisons_dir, 'aircraft_comparison.png')
        fig_comp.savefig(comparison_path, dpi=300, bbox_inches='tight')
        print("  - Aircraft comparison saved in 'comparisons/'")
        plt.close(fig_comp)
    except Exception as e:
        print(f"  Error generating comparison plot: {e}")
    
    print("\nAll visualizations generated successfully!")


def example_flight_envelope_analysis():
    """
    Example 5: Detailed flight envelope analysis
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: FLIGHT ENVELOPE ANALYSIS")
    print("="*60)
    
    # Use fighter jet for interesting envelope
    aircraft_list = create_sample_aircraft()
    fighter = aircraft_list[2]  # Fighter jet
    
    print(f"Analyzing flight envelope for {fighter.name}")
    
    envelope = FlightEnvelope(fighter)
    
    # Calculate key performance parameters at different altitudes
    altitudes = [0, 5000, 10000, 15000]  # meters
    
    print(f"\n{'Altitude (m)':<12} {'Stall Speed (m/s)':<18} {'Service Ceiling (m)':<20}")
    print("-" * 50)
    
    for alt in altitudes:
        weight = fighter.mass.max_takeoff_weight
        v_stall = envelope.calculate_stall_speed(alt, weight)
        service_ceiling = envelope.calculate_service_ceiling(weight)
        
        print(f"{alt:<12} {v_stall:<18.1f} {service_ceiling:<20.0f}")
    
    # Generate V-n diagrams at different altitudes
    print(f"\nGenerating V-n diagrams at different altitudes...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, alt in enumerate(altitudes):
        velocities, load_factors = envelope.generate_v_n_diagram(alt)
        
        axes[i].plot(velocities, load_factors, 'b-', linewidth=2)
        axes[i].fill(velocities, load_factors, alpha=0.2, color='blue')
        axes[i].grid(True, alpha=0.3)
        axes[i].set_xlabel('Velocity (m/s)')
        axes[i].set_ylabel('Load Factor (g)')
        axes[i].set_title(f'V-n Diagram at {alt}m')
        axes[i].axhline(y=0, color='k', linestyle='-', alpha=0.3)
        axes[i].axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Add stall speed line
        v_stall = envelope.calculate_stall_speed(alt, fighter.mass.max_takeoff_weight)
        axes[i].axvline(x=v_stall, color='red', linestyle='--', alpha=0.7, 
                       label=f'V_stall = {v_stall:.1f} m/s')
        axes[i].legend()
    
    plt.tight_layout()
    
    # Save to examples folder
    visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
    examples_dir = os.path.join(visualizations_dir, 'examples')
    os.makedirs(examples_dir, exist_ok=True)
    save_path = os.path.join(examples_dir, 'flight_envelope_analysis.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("  - Flight envelope analysis saved in 'examples/'")


def run_all_examples():
    """
    Run all example analyses
    """
    print("AIRCRAFT DESIGN EXPLORATION EXAMPLES")
    print("="*60)
    print("This script demonstrates the capabilities of the aircraft design system")
    print("including design analysis, performance evaluation, optimization, and visualization.")
    
    try:
        example_basic_analysis()
        example_flight_conditions_testing()
        example_performance_optimization()
        example_visualization()
        example_flight_envelope_analysis()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nGenerated files in 'visualizations/' folder:")
        print("- Various PNG plots showing aircraft performance characteristics")
        print("- Comparison plots between different aircraft designs")
        print("- Flight envelope analysis diagrams")
        print("\nThe system provides comprehensive tools for:")
        print("- Aircraft design parameter analysis")
        print("- Performance evaluation under various flight conditions")
        print("- Multi-objective design optimization")
        print("- Advanced visualization and comparison capabilities")
        
    except Exception as e:
        print(f"\nError during example execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
