#!/usr/bin/env python3
"""
Aircraft Scaling Comparison

This script demonstrates the difference between distorted scaling and proper 1:1 scaling
in 3D aircraft visualizations, showing why accurate proportions matter.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib.pyplot as plt
import numpy as np
from src import create_sample_aircraft, Aircraft3DVisualizer


def create_scaling_comparison():
    """Create side-by-side comparison of different scaling approaches."""
    print("📏 AIRCRAFT SCALING COMPARISON")
    print("=" * 50)
    print("Demonstrating the importance of 1:1 scaling in aircraft visualization")
    
    # Get sample aircraft
    aircraft_list = create_sample_aircraft()
    
    for aircraft in aircraft_list:
        print(f"\nCreating scaling comparison for {aircraft.name}...")
        
        visualizer = Aircraft3DVisualizer(aircraft)
        
        # Generate geometries
        X_wing, Y_wing, Z_wing = visualizer.generate_wing_geometry()
        X_fus, Y_fus, Z_fus = visualizer.generate_fuselage_geometry()
        X_tail, Y_tail, Z_tail = visualizer.generate_tail_geometry()
        
        # Create figure with two subplots
        fig = plt.figure(figsize=(16, 8))
        
        # Left plot: Distorted scaling (old way)
        ax1 = fig.add_subplot(121, projection='3d')
        
        # Plot aircraft components
        ax1.plot_surface(X_wing, Y_wing, Z_wing, alpha=0.7, color='lightblue', 
                        edgecolor='darkblue', linewidth=0.5)
        ax1.plot_surface(X_fus, Y_fus, Z_fus, alpha=0.8, color='lightgray', 
                        edgecolor='darkgray', linewidth=0.5)
        for i in range(X_tail.shape[0]):
            ax1.plot(X_tail[i], Y_tail[i], Z_tail[i], 'r-', linewidth=2, alpha=0.8)
        
        # Old distorted scaling
        max_range = max(aircraft.geometry.fuselage_length, aircraft.geometry.wing_span) / 2
        ax1.set_xlim([-max_range*0.2, max_range*1.2])
        ax1.set_ylim([-max_range*1.1, max_range*1.1])
        ax1.set_zlim([-max_range*0.3, max_range*0.3])
        
        ax1.set_title('❌ Distorted Scaling\n(Non-proportional axes)', fontsize=12, fontweight='bold', color='red')
        ax1.set_xlabel('X (Length) [m]')
        ax1.set_ylabel('Y (Span) [m]')
        ax1.set_zlabel('Z (Height) [m]')
        
        # Right plot: Proper 1:1 scaling (new way)
        ax2 = fig.add_subplot(122, projection='3d')
        
        # Plot aircraft components
        ax2.plot_surface(X_wing, Y_wing, Z_wing, alpha=0.7, color='lightblue', 
                        edgecolor='darkblue', linewidth=0.5)
        ax2.plot_surface(X_fus, Y_fus, Z_fus, alpha=0.8, color='lightgray', 
                        edgecolor='darkgray', linewidth=0.5)
        for i in range(X_tail.shape[0]):
            ax2.plot(X_tail[i], Y_tail[i], Z_tail[i], 'r-', linewidth=2, alpha=0.8)
        
        # New 1:1 scaling
        x_center = aircraft.geometry.fuselage_length / 2
        y_center = 0
        z_center = 0
        
        ax2.set_xlim([x_center - max_range*1.2, x_center + max_range*1.2])
        ax2.set_ylim([y_center - max_range*1.2, y_center + max_range*1.2])
        ax2.set_zlim([z_center - max_range*0.6, z_center + max_range*0.6])
        
        try:
            ax2.set_box_aspect([2.4, 2.4, 1.2])
        except AttributeError:
            pass
        
        ax2.set_title('✅ True 1:1 Scaling\n(Accurate proportions)', fontsize=12, fontweight='bold', color='green')
        ax2.set_xlabel('X (Length) [m]')
        ax2.set_ylabel('Y (Span) [m]')
        ax2.set_zlabel('Z (Height) [m]')
        
        # Add aircraft info
        info_text = (f"{aircraft.name}\n"
                    f"Span: {aircraft.geometry.wing_span:.1f}m\n"
                    f"Length: {aircraft.geometry.fuselage_length:.1f}m\n"
                    f"Ratio: {aircraft.geometry.wing_span/aircraft.geometry.fuselage_length:.2f}")
        
        fig.suptitle(f'Scaling Comparison - {aircraft.name}', fontsize=16, fontweight='bold')
        
        # Add explanation text
        explanation = ("Left: Axes scaled differently - aircraft appears distorted\n"
                      "Right: True 1:1 scaling - accurate proportions and relationships")
        fig.text(0.5, 0.02, explanation, ha='center', fontsize=11, style='italic')
        
        plt.tight_layout()
        
        # Save comparison
        safe_name = aircraft.name.lower().replace(" ", "_")
        filename = f"scaling_comparison_{safe_name}.png"
        
        visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
        full_path = os.path.join(visualizations_dir, filename)
        plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved as '{filename}'")


def show_scaling_importance():
    """Explain why 1:1 scaling is important for aircraft visualization."""
    print(f"\n💡 WHY 1:1 SCALING MATTERS")
    print("=" * 50)
    
    aircraft_list = create_sample_aircraft()
    
    print("Real aircraft proportions:")
    print(f"{'Aircraft':<20} {'Span (m)':<10} {'Length (m)':<12} {'Span/Length':<12}")
    print("-" * 54)
    
    for aircraft in aircraft_list:
        span = aircraft.geometry.wing_span
        length = aircraft.geometry.fuselage_length
        ratio = span / length
        print(f"{aircraft.name:<20} {span:<10.1f} {length:<12.1f} {ratio:<12.2f}")
    
    print(f"\n🎯 Key Insights with 1:1 Scaling:")
    print("• Commercial airliners have wings nearly as wide as they are long")
    print("• Fighter jets are much longer than their wingspan (low aspect ratio)")
    print("• GA aircraft have moderate proportions between the two extremes")
    print("• True scaling reveals design trade-offs and engineering constraints")
    
    print(f"\n❌ Problems with Distorted Scaling:")
    print("• Aircraft appear stretched or compressed")
    print("• Design relationships are obscured")
    print("• Comparative analysis becomes misleading")
    print("• Educational value is reduced")
    
    print(f"\n✅ Benefits of 1:1 Scaling:")
    print("• Accurate visual representation of real aircraft")
    print("• Proper understanding of design proportions")
    print("• Meaningful comparison between aircraft types")
    print("• Better intuition for design parameters")


def main():
    """Run the scaling comparison demonstration."""
    print("📐 AIRCRAFT SCALING ANALYSIS")
    print("=" * 60)
    print("Understanding the importance of accurate 1:1 scaling in 3D visualization")
    
    try:
        # Create scaling comparisons
        create_scaling_comparison()
        
        # Explain importance
        show_scaling_importance()
        
        print(f"\n" + "=" * 60)
        print("🎉 SCALING COMPARISON COMPLETE!")
        print("=" * 60)
        
        print(f"\n📂 Generated Files:")
        print("• scaling_comparison_commercial_airliner.png")
        print("• scaling_comparison_general_aviation.png")
        print("• scaling_comparison_fighter_jet.png")
        
        print(f"\n🔍 What to Look For:")
        print("• Notice how the left (distorted) images make aircraft look unnatural")
        print("• The right (1:1 scaled) images show true aircraft proportions")
        print("• Compare wingspan-to-length ratios between aircraft types")
        print("• Observe how scaling affects your perception of the design")
        
        print(f"\n💡 The updated 3D visualization system now uses proper 1:1 scaling")
        print("   for accurate representation of aircraft geometries!")
        
    except Exception as e:
        print(f"\n❌ Error during scaling comparison: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
