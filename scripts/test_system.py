#!/usr/bin/env python3
"""
Quick test script to verify the aircraft design system is working correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import traceback

def test_basic_functionality():
    """Test basic system functionality"""
    print("Testing Aircraft Design System...")
    print("=" * 50)
    
    try:
        # Test aircraft creation
        print("1. Testing aircraft creation...")
        from src import create_sample_aircraft
        aircraft_list = create_sample_aircraft()
        print(f"   ✓ Created {len(aircraft_list)} sample aircraft")
        
        # Test basic calculations
        print("2. Testing aerodynamic calculations...")
        airliner = aircraft_list[0]
        cl = airliner.calculate_lift_coefficient(5.0)  # 5 degrees AoA
        cd = airliner.calculate_drag_coefficient(cl)
        ld_ratio = cl / cd
        print(f"   ✓ CL = {cl:.3f}, CD = {cd:.3f}, L/D = {ld_ratio:.1f}")
        
        # Test flight conditions
        print("3. Testing flight conditions...")
        from src import AtmosphericConditions, FlightConditions
        atm = AtmosphericConditions.standard_atmosphere(10000)
        condition = FlightConditions(atm, 200, 5.0, 0, 1.0)
        print(f"   ✓ Mach = {condition.mach_number:.3f}, q = {condition.dynamic_pressure:.0f} Pa")
        
        # Test performance analysis
        print("4. Testing performance analysis...")
        from src import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer(airliner)
        optimal_aoa = analyzer.find_optimal_angle_of_attack()
        range_km = analyzer.calculate_range(10000, 200, 20000)
        print(f"   ✓ Optimal AoA = {optimal_aoa:.1f}°, Range = {range_km:.0f} km")
        
        # Test flight envelope
        print("5. Testing flight envelope...")
        from src import FlightEnvelope
        envelope = FlightEnvelope(airliner)
        v_stall = envelope.calculate_stall_speed(0, airliner.mass.max_takeoff_weight)
        print(f"   ✓ Stall speed = {v_stall:.1f} m/s")
        
        # Test visualization (without actually displaying)
        print("6. Testing visualization setup...")
        from src import AircraftVisualizer
        visualizer = AircraftVisualizer(airliner)
        print("   ✓ Visualizer created successfully")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("The aircraft design system is working correctly.")
        print("\nTo run full examples with plots, execute:")
        print("   python scripts/run_examples.py")
        print("   python scripts/interactive_demo.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
