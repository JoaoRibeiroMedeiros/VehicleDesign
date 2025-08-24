#!/usr/bin/env python3
"""
Design Your Own Aircraft - Interactive 3D Designer

This script allows you to create custom aircraft designs and immediately
see them in 3D, helping you understand how parameters affect aircraft shape.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
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
    from src import PerformanceAnalyzer, FlightEnvelope
    analyzer = PerformanceAnalyzer(aircraft)
    envelope = FlightEnvelope(aircraft)
    
    optimal_aoa = analyzer.find_optimal_angle_of_attack()
    max_ld = aircraft.calculate_lift_drag_ratio(optimal_aoa)
    
    # Calculate key performance metrics
    stall_speed_sl = envelope.calculate_stall_speed(0, mass.max_takeoff_weight)  # Sea level
    stall_speed_10k = envelope.calculate_stall_speed(10000, mass.max_takeoff_weight)  # 10km altitude
    service_ceiling = envelope.calculate_service_ceiling(mass.max_takeoff_weight)
    
    # Range and endurance estimates
    range_km = analyzer.calculate_range(10000, 200, mass.fuel_capacity)  # Cruise at 10km, 200 m/s
    endurance_hrs = analyzer.calculate_endurance(8000, mass.fuel_capacity)  # Endurance at 8km
    
    # Takeoff performance
    takeoff_data = analyzer.analyze_takeoff_performance(3000)  # 3km runway
    
    print(f"\nAerodynamic Performance:")
    print(f"  • Optimal angle of attack: {optimal_aoa:.1f}°")
    print(f"  • Maximum L/D ratio: {max_ld:.1f}")
    print(f"  • Stall speed (sea level): {stall_speed_sl:.1f} m/s ({stall_speed_sl*3.6:.0f} km/h)")
    print(f"  • Stall speed (10km alt): {stall_speed_10k:.1f} m/s ({stall_speed_10k*3.6:.0f} km/h)")
    
    print(f"\nMission Performance:")
    print(f"  • Estimated range: {range_km:.0f} km")
    print(f"  • Estimated endurance: {endurance_hrs:.1f} hours")
    print(f"  • Service ceiling: {service_ceiling:.0f} m ({service_ceiling/1000:.1f} km)")
    print(f"  • Takeoff distance: {takeoff_data['total_distance']:.0f} m")
    
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


def create_comprehensive_analysis(aircraft: Aircraft):
    """Create comprehensive performance analysis and visualizations."""
    print(f"\n📊 Creating Comprehensive Performance Analysis...")
    
    safe_name = aircraft.name.lower().replace(" ", "_").replace("/", "_")
    
    # Create organized folder structure for this custom aircraft
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{safe_name}_{timestamp}"
    
    visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
    aircraft_folder = os.path.join(visualizations_dir, 'custom_designs', folder_name)
    os.makedirs(aircraft_folder, exist_ok=True)
    
    print(f"  📁 Created folder: visualizations/custom_designs/{folder_name}/")
    
    # Import required modules
    from src import (AircraftVisualizer, Aircraft3DVisualizer, PerformanceAnalyzer, 
                    FlightEnvelope)
    
    # Create visualizers and set their output folders
    visualizer_2d = AircraftVisualizer(aircraft)
    visualizer_2d.set_output_folder(aircraft_folder)
    
    visualizer_3d = Aircraft3DVisualizer(aircraft)
    visualizer_3d.set_output_folder(aircraft_folder)
    
    analyzer = PerformanceAnalyzer(aircraft)
    envelope = FlightEnvelope(aircraft)
    
    print("  📈 Generating performance plots...")
    
    # 1. Drag polar
    fig1 = visualizer_2d.plot_drag_polar('drag_polar.png')
    plt.close(fig1)
    print("    ✓ Drag polar")
    
    # 2. L/D vs angle of attack
    fig2 = visualizer_2d.plot_lift_drag_vs_aoa('ld_vs_aoa.png')
    plt.close(fig2)
    print("    ✓ L/D vs angle of attack")
    
    # 3. V-n diagram
    fig3 = visualizer_2d.plot_v_n_diagram(save_path='vn_diagram.png')
    plt.close(fig3)
    print("    ✓ V-n diagram (flight envelope)")
    
    # 4. Performance envelope
    fig4 = visualizer_2d.plot_performance_envelope('performance_envelope.png')
    plt.close(fig4)
    print("    ✓ Performance envelope (3D)")
    
    # 5. Climb performance (estimate thrust based on aircraft type)
    # Estimate thrust based on aircraft characteristics
    wing_loading = aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area
    if wing_loading > 4000:  # High performance aircraft
        thrust_estimate = aircraft.mass.max_takeoff_weight * 9.81 * 0.8  # High T/W ratio
    elif wing_loading < 1500:  # Light aircraft
        thrust_estimate = aircraft.mass.max_takeoff_weight * 9.81 * 0.25  # Low T/W ratio
    else:  # Medium aircraft
        thrust_estimate = aircraft.mass.max_takeoff_weight * 9.81 * 0.4  # Medium T/W ratio
    
    fig5 = visualizer_2d.plot_climb_performance(thrust_estimate, 'climb_performance.png')
    plt.close(fig5)
    print("    ✓ Climb performance")
    
    print("  🛩️ Generating 3D visualization...")
    
    # 6. 3D aircraft model
    fig6 = visualizer_3d.plot_3d_aircraft_matplotlib('aircraft_3d.png')
    plt.show()  # Display the 3D plot
    plt.close(fig6)
    print("    ✓ 3D aircraft model")
    
    # 7. Interactive 3D model
    interactive_fig = visualizer_3d.create_interactive_3d_plotly()
    interactive_filename = 'aircraft_interactive.html'
    interactive_path = os.path.join(aircraft_folder, interactive_filename)
    interactive_fig.write_html(interactive_path)
    print("    ✓ Interactive 3D model")
    
    # 8. Create summary dashboard
    create_performance_summary_plot(aircraft, aircraft_folder)
    print("    ✓ Performance summary dashboard")
    
    print(f"\n  📁 Generated Files in '{folder_name}/':")
    print(f"    • drag_polar.png")
    print(f"    • ld_vs_aoa.png") 
    print(f"    • vn_diagram.png")
    print(f"    • performance_envelope.png")
    print(f"    • climb_performance.png")
    print(f"    • aircraft_3d.png")
    print(f"    • aircraft_interactive.html")
    print(f"    • performance_summary.png")
    
    # Create a README file for the aircraft folder
    create_aircraft_readme(aircraft, aircraft_folder, folder_name)
    print(f"    • README.md (aircraft specifications)")
    
    # Try to open interactive version
    try:
        import webbrowser
        print(f"\n  🌐 Opening interactive 3D model in browser...")
        webbrowser.open(interactive_path)
    except:
        print(f"\n  💡 Open '{interactive_filename}' in your browser for interactivity")
    
    return aircraft_folder


def create_performance_summary_plot(aircraft: Aircraft, aircraft_folder: str):
    """Create a comprehensive performance summary dashboard."""
    from src import PerformanceAnalyzer, FlightEnvelope
    
    analyzer = PerformanceAnalyzer(aircraft)
    envelope = FlightEnvelope(aircraft)
    
    # Create figure with multiple subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Drag polar (top left)
    angles = np.linspace(-5, 20, 100)
    cl_values = []
    cd_values = []
    
    for angle in angles:
        cl = aircraft.calculate_lift_coefficient(angle)
        cd = aircraft.calculate_drag_coefficient(cl)
        cl_values.append(cl)
        cd_values.append(cd)
    
    ax1.plot(cd_values, cl_values, 'b-', linewidth=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Drag Coefficient (CD)')
    ax1.set_ylabel('Lift Coefficient (CL)')
    ax1.set_title('Drag Polar')
    
    # Mark optimal point
    optimal_aoa = analyzer.find_optimal_angle_of_attack()
    optimal_cl = aircraft.calculate_lift_coefficient(optimal_aoa)
    optimal_cd = aircraft.calculate_drag_coefficient(optimal_cl)
    ax1.plot(optimal_cd, optimal_cl, 'ro', markersize=8)
    ax1.annotate(f'Max L/D\n({optimal_cd:.3f}, {optimal_cl:.3f})', 
                xy=(optimal_cd, optimal_cl), xytext=(optimal_cd+0.005, optimal_cl+0.1),
                arrowprops=dict(arrowstyle='->', color='red'))
    
    # 2. L/D vs AoA (top right)
    ld_ratios = []
    for angle in angles:
        ld = aircraft.calculate_lift_drag_ratio(angle)
        ld_ratios.append(ld)
    
    ax2.plot(angles, ld_ratios, 'g-', linewidth=2)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Angle of Attack (degrees)')
    ax2.set_ylabel('L/D Ratio')
    ax2.set_title('Lift-to-Drag Ratio vs AoA')
    
    # Mark optimal point
    max_ld = aircraft.calculate_lift_drag_ratio(optimal_aoa)
    ax2.plot(optimal_aoa, max_ld, 'ro', markersize=8)
    ax2.annotate(f'Max L/D\n({optimal_aoa:.1f}°, {max_ld:.1f})', 
                xy=(optimal_aoa, max_ld), xytext=(optimal_aoa+2, max_ld+1),
                arrowprops=dict(arrowstyle='->', color='red'))
    
    # 3. Stall speed vs altitude (bottom left)
    altitudes = np.linspace(0, 15000, 30)
    stall_speeds = []
    
    for alt in altitudes:
        v_stall = envelope.calculate_stall_speed(alt, aircraft.mass.max_takeoff_weight)
        stall_speeds.append(v_stall)
    
    ax3.plot(stall_speeds, altitudes, 'r-', linewidth=2)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlabel('Stall Speed (m/s)')
    ax3.set_ylabel('Altitude (m)')
    ax3.set_title('Stall Speed vs Altitude')
    
    # 4. Performance summary bars (bottom right)
    metrics = ['Wing Loading\n(N/m²)', 'Max L/D', 'Aspect Ratio', 'Fuel Fraction\n(%)', 'T/O Distance\n(m)']
    
    wing_loading = aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area
    fuel_fraction = aircraft.mass.fuel_capacity / aircraft.mass.max_takeoff_weight * 100
    takeoff_data = analyzer.analyze_takeoff_performance(3000)
    
    values = [wing_loading/100, max_ld, aircraft.geometry.aspect_ratio, fuel_fraction, takeoff_data['total_distance']/100]
    colors = ['skyblue', 'lightgreen', 'orange', 'pink', 'lightcoral']
    
    bars = ax4.bar(metrics, values, color=colors, alpha=0.7)
    ax4.set_title('Key Performance Metrics')
    ax4.set_ylabel('Normalized Values')
    ax4.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value, original in zip(bars, values, [wing_loading, max_ld, aircraft.geometry.aspect_ratio, fuel_fraction, takeoff_data['total_distance']]):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{original:.1f}', ha='center', va='bottom', fontsize=9)
    
    # Overall title
    plt.suptitle(f'Performance Analysis Summary - {aircraft.name}', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save summary
    summary_path = os.path.join(aircraft_folder, 'performance_summary.png')
    plt.savefig(summary_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_aircraft_readme(aircraft: Aircraft, aircraft_folder: str, folder_name: str):
    """Create a README file with aircraft specifications and analysis results."""
    from src import PerformanceAnalyzer, FlightEnvelope
    
    analyzer = PerformanceAnalyzer(aircraft)
    envelope = FlightEnvelope(aircraft)
    
    # Calculate performance metrics
    optimal_aoa = analyzer.find_optimal_angle_of_attack()
    max_ld = aircraft.calculate_lift_drag_ratio(optimal_aoa)
    stall_speed_sl = envelope.calculate_stall_speed(0, aircraft.mass.max_takeoff_weight)
    stall_speed_10k = envelope.calculate_stall_speed(10000, aircraft.mass.max_takeoff_weight)
    service_ceiling = envelope.calculate_service_ceiling(aircraft.mass.max_takeoff_weight)
    range_km = analyzer.calculate_range(10000, 200, aircraft.mass.fuel_capacity)
    endurance_hrs = analyzer.calculate_endurance(8000, aircraft.mass.fuel_capacity)
    takeoff_data = analyzer.analyze_takeoff_performance(3000)
    
    # Wing loading and other derived parameters
    wing_loading = aircraft.mass.max_takeoff_weight * 9.81 / aircraft.geometry.wing_area
    fuel_fraction = aircraft.mass.fuel_capacity / aircraft.mass.max_takeoff_weight
    payload_fraction = aircraft.mass.payload_capacity / aircraft.mass.max_takeoff_weight
    
    # Create README content
    readme_content = f"""# {aircraft.name}

**Custom Aircraft Design Analysis**  
Generated: {folder_name.split('_')[-2]}_{folder_name.split('_')[-1]}

## Aircraft Specifications

### Geometric Properties
- **Wing Span**: {aircraft.geometry.wing_span:.1f} m
- **Wing Area**: {aircraft.geometry.wing_area:.1f} m²
- **Wing Chord**: {aircraft.geometry.wing_chord:.1f} m
- **Aspect Ratio**: {aircraft.geometry.aspect_ratio:.1f}
- **Sweep Angle**: {aircraft.geometry.sweep_angle:.1f}°
- **Dihedral Angle**: {aircraft.geometry.dihedral_angle:.1f}°
- **Taper Ratio**: {aircraft.geometry.taper_ratio:.2f}
- **Thickness Ratio**: {aircraft.geometry.thickness_ratio:.2f}
- **Fuselage Length**: {aircraft.geometry.fuselage_length:.1f} m
- **Fuselage Diameter**: {aircraft.geometry.fuselage_diameter:.1f} m

### Mass Properties
- **Empty Weight**: {aircraft.mass.empty_weight:.0f} kg
- **Fuel Capacity**: {aircraft.mass.fuel_capacity:.0f} kg
- **Payload Capacity**: {aircraft.mass.payload_capacity:.0f} kg
- **Max Takeoff Weight**: {aircraft.mass.max_takeoff_weight:.0f} kg

### Derived Parameters
- **Wing Loading**: {wing_loading:.0f} N/m²
- **Fuel Fraction**: {fuel_fraction:.1%}
- **Payload Fraction**: {payload_fraction:.1%}

## Performance Analysis

### Aerodynamic Performance
- **Optimal Angle of Attack**: {optimal_aoa:.1f}°
- **Maximum L/D Ratio**: {max_ld:.1f}
- **Stall Speed (Sea Level)**: {stall_speed_sl:.1f} m/s ({stall_speed_sl*3.6:.0f} km/h)
- **Stall Speed (10km Altitude)**: {stall_speed_10k:.1f} m/s ({stall_speed_10k*3.6:.0f} km/h)

### Mission Performance
- **Estimated Range**: {range_km:.0f} km
- **Estimated Endurance**: {endurance_hrs:.1f} hours
- **Service Ceiling**: {service_ceiling:.0f} m ({service_ceiling/1000:.1f} km)
- **Takeoff Distance**: {takeoff_data['total_distance']:.0f} m

## Design Assessment

### Strengths
"""
    
    # Add design assessment
    if aircraft.geometry.aspect_ratio > 8:
        readme_content += "- High aspect ratio provides excellent fuel efficiency\n"
    elif aircraft.geometry.aspect_ratio < 5:
        readme_content += "- Low aspect ratio enables high maneuverability\n"
    else:
        readme_content += "- Moderate aspect ratio balances efficiency and maneuverability\n"
    
    if aircraft.geometry.sweep_angle > 20:
        readme_content += "- Swept wing design suitable for high-speed flight\n"
    elif aircraft.geometry.sweep_angle < 5:
        readme_content += "- Straight wing provides excellent low-speed handling\n"
    else:
        readme_content += "- Moderate sweep balances speed and handling characteristics\n"
    
    if wing_loading > 4000:
        readme_content += "- High wing loading enables fast cruise speeds\n"
    elif wing_loading < 1500:
        readme_content += "- Low wing loading allows short runway operations\n"
    else:
        readme_content += "- Moderate wing loading provides versatile performance\n"
    
    readme_content += f"""
### Trade-offs
- Range vs Payload: Current fuel fraction of {fuel_fraction:.1%} prioritizes {'range' if fuel_fraction > 0.3 else 'payload'}
- Speed vs Efficiency: Design optimized for {'speed' if aircraft.geometry.sweep_angle > 15 else 'efficiency'}
- Runway Performance: {'Long runway required' if takeoff_data['total_distance'] > 2000 else 'Good short-field performance'}

## Generated Visualizations

### Performance Plots
- `drag_polar.png` - Lift vs drag coefficient relationship
- `ld_vs_aoa.png` - Lift-to-drag ratio vs angle of attack
- `vn_diagram.png` - Flight envelope (velocity vs load factor)
- `performance_envelope.png` - 3D performance surface
- `climb_performance.png` - Rate of climb vs altitude

### 3D Visualizations
- `aircraft_3d.png` - Static 3D aircraft model
- `aircraft_interactive.html` - Interactive 3D model (open in browser)

### Summary
- `performance_summary.png` - Comprehensive performance dashboard

## Usage Notes

1. **Interactive 3D Model**: Open `aircraft_interactive.html` in your web browser to explore the 3D model
2. **Performance Analysis**: Review all PNG files for detailed performance characteristics
3. **Design Iteration**: Use this analysis to refine your design parameters

---
*Generated by Aircraft Design System v1.0*
"""
    
    # Write README file
    readme_path = os.path.join(aircraft_folder, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(readme_content)


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
        
        # Create comprehensive performance analysis
        create_comprehensive_analysis(custom_aircraft)
        
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
