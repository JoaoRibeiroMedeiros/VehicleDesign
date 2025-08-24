#!/usr/bin/env python3
"""
Aircraft Parameter Explorer

This script demonstrates the enhanced documentation and helps users understand
the meaning and significance of each aircraft design parameter.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import create_sample_aircraft, AircraftGeometry, AircraftMass


def explore_aircraft_parameters():
    """
    Interactive exploration of aircraft parameters with detailed explanations.
    """
    print("🛩️  AIRCRAFT DESIGN PARAMETER EXPLORER")
    print("=" * 60)
    print("This tool helps you understand aircraft design parameters")
    print("and their impact on performance characteristics.\n")
    
    # Create sample aircraft
    aircraft_list = create_sample_aircraft()
    
    print("📋 AVAILABLE AIRCRAFT DESIGNS:")
    for i, aircraft in enumerate(aircraft_list, 1):
        print(f"{i}. {aircraft.name}")
    
    print("\n" + "=" * 60)
    print("PARAMETER DOCUMENTATION")
    print("=" * 60)
    
    # Display AircraftGeometry documentation
    print("\n🔧 GEOMETRIC PARAMETERS:")
    print("-" * 30)
    print(AircraftGeometry.__doc__)
    
    # Display AircraftMass documentation  
    print("\n⚖️  MASS PARAMETERS:")
    print("-" * 30)
    print(AircraftMass.__doc__)
    
    # Show parameter comparison between aircraft types
    print("\n📊 PARAMETER COMPARISON:")
    print("=" * 60)
    
    # Create comparison table
    print(f"{'Parameter':<20} {'Airliner':<12} {'GA Aircraft':<12} {'Fighter':<12} {'Units':<8}")
    print("-" * 70)
    
    params = [
        ('Wing Span', 'wing_span', 'm'),
        ('Wing Area', 'wing_area', 'm²'),
        ('Aspect Ratio', 'aspect_ratio', '-'),
        ('Sweep Angle', 'sweep_angle', '°'),
        ('Thickness Ratio', 'thickness_ratio', '-'),
        ('MTOW', 'max_takeoff_weight', 'kg'),
        ('Empty Weight', 'empty_weight', 'kg'),
        ('Fuel Capacity', 'fuel_capacity', 'kg')
    ]
    
    for param_name, attr_name, unit in params:
        values = []
        for aircraft in aircraft_list:
            if hasattr(aircraft.geometry, attr_name):
                value = getattr(aircraft.geometry, attr_name)
            elif hasattr(aircraft.mass, attr_name):
                value = getattr(aircraft.mass, attr_name)
            else:
                value = 0
            values.append(f"{value:.1f}" if isinstance(value, float) else str(value))
        
        print(f"{param_name:<20} {values[0]:<12} {values[1]:<12} {values[2]:<12} {unit:<8}")
    
    # Calculate and show derived parameters
    print(f"\n{'Derived Parameters':<20} {'Airliner':<12} {'GA Aircraft':<12} {'Fighter':<12} {'Units':<8}")
    print("-" * 70)
    
    for aircraft in aircraft_list:
        wing_loading = aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area
        fuel_fraction = aircraft.mass.fuel_capacity / aircraft.mass.max_takeoff_weight
        payload_fraction = aircraft.mass.payload_capacity / aircraft.mass.max_takeoff_weight
        
        if aircraft == aircraft_list[0]:  # First iteration, print labels
            print(f"{'Wing Loading':<20} {wing_loading:<12.0f}", end="")
        elif aircraft == aircraft_list[1]:
            wing_loading_ga = aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area
            print(f" {wing_loading_ga:<12.0f}", end="")
        else:
            wing_loading_fighter = aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area
            print(f" {wing_loading_fighter:<12.0f} {'N/m²':<8}")
            
        if aircraft == aircraft_list[0]:
            print(f"{'Fuel Fraction':<20} {fuel_fraction:<12.3f}", end="")
        elif aircraft == aircraft_list[1]:
            fuel_fraction_ga = aircraft.mass.fuel_capacity / aircraft.mass.max_takeoff_weight
            print(f" {fuel_fraction_ga:<12.3f}", end="")
        else:
            fuel_fraction_fighter = aircraft.mass.fuel_capacity / aircraft.mass.max_takeoff_weight
            print(f" {fuel_fraction_fighter:<12.3f} {'-':<8}")
    
    # Show design insights
    print(f"\n🎯 DESIGN INSIGHTS:")
    print("=" * 60)
    
    insights = [
        ("High Aspect Ratio (Airliner)", "Better fuel efficiency, longer range"),
        ("Low Aspect Ratio (Fighter)", "Better maneuverability, higher roll rate"),
        ("Wing Sweep (Airliner/Fighter)", "Delays compressibility, enables higher cruise speed"),
        ("Thick Airfoils (GA)", "More structural depth, docile stall characteristics"),
        ("Thin Airfoils (Fighter)", "Lower drag at high speeds, better for supersonic flight"),
        ("High Wing Loading (Airliner/Fighter)", "Better ride quality, higher cruise speed"),
        ("Low Wing Loading (GA)", "Lower stall speed, better short-field performance"),
        ("High Fuel Fraction (Airliner)", "Longer range capability"),
        ("Low Fuel Fraction (GA/Fighter)", "More payload capacity, lower operating costs")
    ]
    
    for design_feature, benefit in insights:
        print(f"• {design_feature:<30} → {benefit}")
    
    print(f"\n💡 KEY TAKEAWAYS:")
    print("=" * 60)
    print("• Aircraft design involves complex trade-offs between competing requirements")
    print("• Each parameter affects multiple aspects of performance")
    print("• Different mission requirements lead to different optimal designs")
    print("• Understanding these relationships is key to effective aircraft design")
    
    print(f"\n📚 TO LEARN MORE:")
    print("=" * 60)
    print("• Run 'python scripts/run_examples.py' for performance analysis")
    print("• Run 'python scripts/interactive_demo.py' for visual exploration")
    print("• Examine the source code in 'src/' for implementation details")
    print("• Try modifying parameters to see their effects on performance")


def show_method_documentation():
    """Show documentation for key aircraft methods."""
    print(f"\n🔍 METHOD DOCUMENTATION:")
    print("=" * 60)
    
    from src import Aircraft
    
    methods = [
        'calculate_lift_coefficient',
        'calculate_drag_coefficient', 
        'calculate_lift_drag_ratio',
        'get_design_summary'
    ]
    
    for method_name in methods:
        method = getattr(Aircraft, method_name)
        print(f"\n📖 {method_name}:")
        print("-" * 40)
        print(method.__doc__)


if __name__ == "__main__":
    explore_aircraft_parameters()
    
    # Ask if user wants to see method documentation
    print(f"\n" + "=" * 60)
    response = input("Would you like to see detailed method documentation? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        show_method_documentation()
    
    print(f"\n✈️  Happy designing!")
