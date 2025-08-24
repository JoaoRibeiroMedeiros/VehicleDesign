#!/usr/bin/env python3
"""
3D Aircraft Viewer

This script creates 3D visualizations of aircraft geometries, allowing you to
see the actual shape and proportions of different aircraft designs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib.pyplot as plt
from src import (
    create_sample_aircraft, 
    Aircraft3DVisualizer, 
    create_aircraft_comparison_3d,
    create_interactive_aircraft_gallery
)


def create_individual_3d_views():
    """Create individual 3D views for each aircraft type."""
    print("🛩️  Creating Individual 3D Aircraft Views")
    print("=" * 50)
    
    aircraft_list = create_sample_aircraft()
    
    for i, aircraft in enumerate(aircraft_list, 1):
        print(f"Generating 3D view for {aircraft.name}...")
        
        visualizer = Aircraft3DVisualizer(aircraft)
        
        # Create matplotlib 3D plot
        fig = visualizer.plot_3d_aircraft_matplotlib(f'aircraft_3d_{i}_{aircraft.name.lower().replace(" ", "_")}.png')
        plt.close(fig)
        
        print(f"  ✓ Saved as 'aircraft_3d_{i}_{aircraft.name.lower().replace(' ', '_')}.png'")
    
    print("\n✅ Individual 3D views created successfully!")


def create_comparison_3d_view():
    """Create side-by-side 3D comparison of all aircraft."""
    print("\n🔄 Creating 3D Aircraft Comparison")
    print("=" * 50)
    
    aircraft_list = create_sample_aircraft()
    
    print("Generating side-by-side 3D comparison...")
    fig = create_aircraft_comparison_3d(aircraft_list, 'aircraft_3d_comparison.png')
    plt.close(fig)
    
    print("  ✓ Saved as 'aircraft_3d_comparison.png'")
    print("\n✅ 3D comparison created successfully!")


def create_interactive_3d_gallery():
    """Create interactive 3D aircraft gallery."""
    print("\n🌐 Creating Interactive 3D Aircraft Gallery")
    print("=" * 50)
    
    aircraft_list = create_sample_aircraft()
    
    print("Generating interactive 3D gallery...")
    fig = create_interactive_aircraft_gallery(aircraft_list)
    
    # Save to visualizations folder
    visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
    gallery_path = os.path.join(visualizations_dir, 'aircraft_3d_interactive_gallery.html')
    fig.write_html(gallery_path)
    
    print("  ✓ Saved as 'aircraft_3d_interactive_gallery.html'")
    print("\n✅ Interactive 3D gallery created successfully!")


def demonstrate_design_differences():
    """Show how different parameters affect aircraft appearance."""
    print("\n📊 Design Parameter Impact Demonstration")
    print("=" * 50)
    
    aircraft_list = create_sample_aircraft()
    
    print("\nKey Visual Differences:")
    print("-" * 30)
    
    for aircraft in aircraft_list:
        geom = aircraft.geometry
        print(f"\n🛩️  {aircraft.name}:")
        print(f"   • Wing Span: {geom.wing_span:.1f}m - {'Wide' if geom.wing_span > 20 else 'Narrow'} wingspan")
        print(f"   • Aspect Ratio: {geom.aspect_ratio:.1f} - {'High' if geom.aspect_ratio > 8 else 'Low'} efficiency")
        print(f"   • Sweep Angle: {geom.sweep_angle:.1f}° - {'Swept' if geom.sweep_angle > 10 else 'Straight'} wing")
        print(f"   • Thickness: {geom.thickness_ratio:.2f} - {'Thick' if geom.thickness_ratio > 0.1 else 'Thin'} airfoil")
        print(f"   • Fuselage: {geom.fuselage_length:.1f}m × {geom.fuselage_diameter:.1f}m")
        
        # Design implications
        if aircraft.name == "Commercial Airliner":
            print("   → Optimized for fuel efficiency and passenger capacity")
        elif aircraft.name == "General Aviation":
            print("   → Balanced for versatility and ease of handling")
        elif aircraft.name == "Fighter Jet":
            print("   → Designed for speed and maneuverability")


def show_3d_viewing_tips():
    """Provide tips for interpreting 3D aircraft visualizations."""
    print("\n💡 3D Visualization Tips")
    print("=" * 50)
    
    tips = [
        "🔍 Aspect Ratio: Compare wing span to chord - high AR wings look long and narrow",
        "📐 Sweep Angle: Notice how wings angle backward from the fuselage",
        "📏 Taper Ratio: See how wing chord decreases from root to tip",
        "📊 Thickness: Thin airfoils (fighters) vs thick airfoils (GA aircraft)",
        "🎯 Proportions: Compare overall size relationships between aircraft types",
        "🔄 Interactive: Use mouse to rotate, zoom, and explore different angles",
        "📱 Web View: Open HTML files in browser for full interactivity"
    ]
    
    for tip in tips:
        print(f"   {tip}")
    
    print(f"\n📁 All visualizations saved in 'visualizations/' folder")


def main():
    """Run the 3D aircraft visualization demo."""
    print("✈️  3D AIRCRAFT VISUALIZATION SYSTEM")
    print("=" * 60)
    print("This tool creates 3D visualizations of aircraft geometries,")
    print("helping you understand how design parameters affect aircraft shape.")
    
    try:
        # Create individual 3D views
        create_individual_3d_views()
        
        # Create comparison view
        create_comparison_3d_view()
        
        # Create interactive gallery
        create_interactive_3d_gallery()
        
        # Show design differences
        demonstrate_design_differences()
        
        # Provide viewing tips
        show_3d_viewing_tips()
        
        print("\n" + "=" * 60)
        print("🎉 3D VISUALIZATION COMPLETE!")
        print("=" * 60)
        
        print("\n📂 Generated Files:")
        print("   Static 3D Views:")
        print("   • aircraft_3d_1_commercial_airliner.png")
        print("   • aircraft_3d_2_general_aviation.png") 
        print("   • aircraft_3d_3_fighter_jet.png")
        print("   • aircraft_3d_comparison.png")
        print("\n   Interactive 3D Gallery:")
        print("   • aircraft_3d_interactive_gallery.html")
        
        print("\n🌐 To view interactive 3D models:")
        print("   Open 'aircraft_3d_interactive_gallery.html' in your web browser")
        print("   Use mouse to rotate, zoom, and explore the aircraft!")
        
        # Try to open the interactive gallery
        try:
            import webbrowser
            visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
            gallery_path = os.path.join(visualizations_dir, 'aircraft_3d_interactive_gallery.html')
            print(f"\n🚀 Opening interactive gallery in your browser...")
            webbrowser.open(gallery_path)
        except:
            print(f"\n💡 Manually open the HTML file in your browser for interactivity")
        
    except Exception as e:
        print(f"\n❌ Error during 3D visualization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
