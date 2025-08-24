#!/usr/bin/env python3
"""
Design Your Own Aircraft - Interactive 3D Designer

This script allows you to create custom aircraft designs and immediately
see them in 3D, helping you understand how parameters affect aircraft shape.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib.pyplot as plt
from src import Aircraft, AircraftGeometry, AircraftMass, Aircraft3DVisualizer


def get_user_input(prompt: str, default: float, min_val: float = None, max_val: float = None) -> float:
    """Get validated user input with default value."""
    while True:
        try:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            if not user_input:
                return default
            
            value = float(user_input)
            
            if min_val is not None and value < min_val:
                print(f"Value must be >= {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be <= {max_val}")
                continue
                
            return value
            
        except ValueError:
            print("Please enter a valid number.")


def design_aircraft_interactively():
    """Interactive aircraft design session."""
    print("✈️  DESIGN YOUR OWN AIRCRAFT")
    print("=" * 50)
    print("Create a custom aircraft design and see it in 3D!")
    print("Press Enter to use default values, or enter your own.\n")
    
    # Get aircraft name
    aircraft_name = input("Aircraft name (default: My Custom Aircraft): ").strip()
    if not aircraft_name:
        aircraft_name = "My Custom Aircraft"
    
    print(f"\n🔧 WING GEOMETRY for {aircraft_name}")
    print("-" * 30)
    
    # Wing parameters with explanations
    print("Wing span affects efficiency and ground handling:")
    wing_span = get_user_input("  Wing span (m)", 15.0, 5.0, 100.0)
    
    print("Wing area affects lift capability and stall speed:")
    wing_area = get_user_input("  Wing area (m²)", 25.0, 8.0, 500.0)
    
    # Calculate aspect ratio
    aspect_ratio = wing_span**2 / wing_area
    print(f"  → Calculated aspect ratio: {aspect_ratio:.1f}")
    
    print("Sweep angle affects high-speed performance:")
    sweep_angle = get_user_input("  Sweep angle (degrees)", 10.0, 0.0, 60.0)
    
    print("Dihedral angle affects stability:")
    dihedral_angle = get_user_input("  Dihedral angle (degrees)", 3.0, -10.0, 15.0)
    
    print("Taper ratio affects lift distribution:")
    taper_ratio = get_user_input("  Taper ratio", 0.4, 0.1, 1.0)
    
    print("Thickness ratio affects drag and structure:")
    thickness_ratio = get_user_input("  Thickness ratio", 0.12, 0.03, 0.20)
    
    print(f"\n🏗️  FUSELAGE GEOMETRY")
    print("-" * 30)
    
    print("Fuselage length affects capacity and stability:")
    fuselage_length = get_user_input("  Fuselage length (m)", 20.0, 5.0, 80.0)
    
    print("Fuselage diameter affects capacity and drag:")
    fuselage_diameter = get_user_input("  Fuselage diameter (m)", 2.5, 0.8, 6.0)
    
    print(f"\n⚖️  MASS PROPERTIES")
    print("-" * 30)
    
    print("Maximum takeoff weight determines overall size:")
    max_takeoff_weight = get_user_input("  Max takeoff weight (kg)", 15000, 500, 600000)
    
    print("Empty weight (structure, engines, systems):")
    empty_weight = get_user_input("  Empty weight (kg)", max_takeoff_weight * 0.55, 
                                 max_takeoff_weight * 0.3, max_takeoff_weight * 0.8)
    
    print("Fuel capacity determines range:")
    fuel_capacity = get_user_input("  Fuel capacity (kg)", max_takeoff_weight * 0.25,
                                  0, max_takeoff_weight - empty_weight)
    
    remaining_capacity = max_takeoff_weight - empty_weight - fuel_capacity
    print(f"Payload capacity (passengers/cargo): {remaining_capacity:.0f} kg")
    payload_capacity = remaining_capacity
    
    # Calculate derived parameters
    wing_chord = wing_area / wing_span  # Average chord
    
    # Create aircraft geometry and mass objects
    geometry = AircraftGeometry(
        wing_span=wing_span,
        wing_area=wing_area,
        wing_chord=wing_chord,
        aspect_ratio=aspect_ratio,
        sweep_angle=sweep_angle,
        dihedral_angle=dihedral_angle,
        taper_ratio=taper_ratio,
        thickness_ratio=thickness_ratio,
        fuselage_length=fuselage_length,
        fuselage_diameter=fuselage_diameter
    )
    
    mass = AircraftMass(
        empty_weight=empty_weight,
        fuel_capacity=fuel_capacity,
        payload_capacity=payload_capacity,
        max_takeoff_weight=max_takeoff_weight
    )
    
    # Create aircraft
    custom_aircraft = Aircraft(aircraft_name, geometry, mass)
    
    return custom_aircraft


def show_aircraft_analysis(aircraft: Aircraft):
    """Show analysis of the designed aircraft."""
    print(f"\n📊 AIRCRAFT ANALYSIS: {aircraft.name}")
    print("=" * 50)
    
    # Basic parameters
    geom = aircraft.geometry
    mass = aircraft.mass
    
    print("Geometric Properties:")
    print(f"  • Wing span: {geom.wing_span:.1f} m")
    print(f"  • Wing area: {geom.wing_area:.1f} m²")
    print(f"  • Aspect ratio: {geom.aspect_ratio:.1f}")
    print(f"  • Sweep angle: {geom.sweep_angle:.1f}°")
    print(f"  • Fuselage: {geom.fuselage_length:.1f}m × {geom.fuselage_diameter:.1f}m")
    
    # Derived parameters
    wing_loading = mass.max_takeoff_weight * 9.81 / geom.wing_area
    fuel_fraction = mass.fuel_capacity / mass.max_takeoff_weight
    payload_fraction = mass.payload_capacity / mass.max_takeoff_weight
    
    print(f"\nPerformance Indicators:")
    print(f"  • Wing loading: {wing_loading:.0f} N/m²")
    print(f"  • Fuel fraction: {fuel_fraction:.1%}")
    print(f"  • Payload fraction: {payload_fraction:.1%}")
    
    # Performance estimates
    from src import PerformanceAnalyzer
    analyzer = PerformanceAnalyzer(aircraft)
    optimal_aoa = analyzer.find_optimal_angle_of_attack()
    max_ld = aircraft.calculate_lift_drag_ratio(optimal_aoa)
    
    print(f"\nAerodynamic Performance:")
    print(f"  • Optimal angle of attack: {optimal_aoa:.1f}°")
    print(f"  • Maximum L/D ratio: {max_ld:.1f}")
    
    # Design category assessment
    print(f"\nDesign Assessment:")
    if geom.aspect_ratio > 8:
        print("  • High aspect ratio → Good for fuel efficiency")
    elif geom.aspect_ratio < 5:
        print("  • Low aspect ratio → Good for maneuverability")
    else:
        print("  • Moderate aspect ratio → Balanced performance")
    
    if geom.sweep_angle > 20:
        print("  • Swept wing → Suitable for high-speed flight")
    elif geom.sweep_angle < 5:
        print("  • Straight wing → Good for low-speed handling")
    else:
        print("  • Moderate sweep → Balanced speed capability")
    
    if wing_loading > 4000:
        print("  • High wing loading → Fast cruise, longer runways")
    elif wing_loading < 1500:
        print("  • Low wing loading → Short runways, gentle handling")
    else:
        print("  • Moderate wing loading → Versatile performance")


def create_3d_visualization(aircraft: Aircraft):
    """Create 3D visualization of the custom aircraft."""
    print(f"\n🎨 Creating 3D Visualization...")
    
    visualizer = Aircraft3DVisualizer(aircraft)
    
    # Create static 3D plot
    safe_name = aircraft.name.lower().replace(" ", "_").replace("/", "_")
    filename = f"custom_aircraft_{safe_name}.png"
    
    fig = visualizer.plot_3d_aircraft_matplotlib(filename)
    plt.show()  # Display the plot
    plt.close(fig)
    
    print(f"  ✓ 3D view saved as '{filename}'")
    
    # Create interactive 3D plot
    interactive_fig = visualizer.create_interactive_3d_plotly()
    interactive_filename = f"custom_aircraft_{safe_name}_interactive.html"
    
    visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
    interactive_path = os.path.join(visualizations_dir, interactive_filename)
    interactive_fig.write_html(interactive_path)
    
    print(f"  ✓ Interactive 3D saved as '{interactive_filename}'")
    
    # Try to open interactive version
    try:
        import webbrowser
        print(f"  🌐 Opening interactive 3D view in browser...")
        webbrowser.open(interactive_path)
    except:
        print(f"  💡 Open '{interactive_filename}' in your browser for interactivity")


def compare_with_reference_aircraft(custom_aircraft: Aircraft):
    """Compare custom aircraft with reference designs."""
    print(f"\n🔄 COMPARISON WITH REFERENCE AIRCRAFT")
    print("=" * 50)
    
    from src import create_sample_aircraft, create_aircraft_comparison_3d
    
    reference_aircraft = create_sample_aircraft()
    all_aircraft = reference_aircraft + [custom_aircraft]
    
    print("Creating comparison visualization...")
    fig = create_aircraft_comparison_3d(all_aircraft, f"custom_aircraft_comparison.png")
    plt.show()  # Display the comparison
    plt.close(fig)
    
    print("  ✓ Comparison saved as 'custom_aircraft_comparison.png'")
    
    # Show parameter comparison table
    print(f"\nParameter Comparison:")
    print(f"{'Parameter':<20} {'Airliner':<12} {'GA':<12} {'Fighter':<12} {'Your Design':<12}")
    print("-" * 68)
    
    params = [
        ('Wing Span (m)', 'wing_span'),
        ('Aspect Ratio', 'aspect_ratio'),
        ('Sweep Angle (°)', 'sweep_angle'),
        ('MTOW (kg)', 'max_takeoff_weight')
    ]
    
    for param_name, attr in params:
        values = []
        for aircraft in all_aircraft:
            if hasattr(aircraft.geometry, attr):
                value = getattr(aircraft.geometry, attr)
            else:
                value = getattr(aircraft.mass, attr)
            values.append(f"{value:.1f}")
        
        print(f"{param_name:<20} {values[0]:<12} {values[1]:<12} {values[2]:<12} {values[3]:<12}")


def main():
    """Run the interactive aircraft designer."""
    print("🎨 INTERACTIVE AIRCRAFT DESIGNER")
    print("=" * 60)
    print("Design your own aircraft and see it in 3D!")
    print("Learn how different parameters affect aircraft appearance and performance.")
    
    try:
        # Design aircraft interactively
        custom_aircraft = design_aircraft_interactively()
        
        # Show analysis
        show_aircraft_analysis(custom_aircraft)
        
        # Create 3D visualization
        create_3d_visualization(custom_aircraft)
        
        # Ask if user wants comparison
        print(f"\n" + "=" * 50)
        compare = input("Would you like to compare with reference aircraft? (y/n): ").lower().strip()
        if compare in ['y', 'yes']:
            compare_with_reference_aircraft(custom_aircraft)
        
        print(f"\n🎉 Aircraft design complete!")
        print(f"Your '{custom_aircraft.name}' has been visualized and analyzed.")
        print(f"Check the 'visualizations/' folder for all generated files.")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Design session cancelled. Thanks for trying the aircraft designer!")
    except Exception as e:
        print(f"\n❌ Error during design: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
