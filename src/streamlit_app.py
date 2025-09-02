"""
Streamlit web application for interactive aircraft design and analysis.

This module provides a user-friendly web interface for:
- Interactive parameter input with sliders and number inputs
- Real-time design assessment and validation
- Comprehensive performance analysis and visualization
- 3D aircraft visualization
- Design comparison and optimization

Author: Aircraft Design System
Version: 1.0
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import datetime
import tempfile
from io import BytesIO
import base64

# Import our aircraft design modules
import sys
import os
sys.path.append(os.path.dirname(__file__))

from aircraft import Aircraft, AircraftGeometry, AircraftMass
from performance_analysis import PerformanceAnalyzer
from visualization import AircraftVisualizer
from aircraft_3d import Aircraft3DVisualizer
from flight_conditions import AtmosphericConditions


# Configure Streamlit page
st.set_page_config(
    page_title="Aircraft Design Studio",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .assessment-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables for the app."""
    if 'aircraft_designs' not in st.session_state:
        st.session_state.aircraft_designs = {}
    if 'current_design' not in st.session_state:
        st.session_state.current_design = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False


def create_parameter_inputs():
    """Create interactive parameter input widgets."""
    st.sidebar.markdown("## 🛩️ Aircraft Design Parameters")
    
    # Aircraft Name
    aircraft_name = st.sidebar.text_input(
        "Aircraft Name", 
        value="Custom Aircraft",
        help="Give your aircraft a unique name"
    )
    
    st.sidebar.markdown("### Wing Geometry")
    
    # Wing parameters with realistic ranges and help text
    wing_span = st.sidebar.slider(
        "Wing Span (m)", 
        min_value=5.0, max_value=80.0, value=12.0, step=0.5,
        help="Distance from wingtip to wingtip. Larger spans improve efficiency but increase structural weight."
    )
    
    wing_area = st.sidebar.slider(
        "Wing Area (m²)", 
        min_value=8.0, max_value=800.0, value=25.0, step=1.0,
        help="Total wing surface area. Affects lift generation and stall speed."
    )
    
    wing_chord = st.sidebar.slider(
        "Wing Chord (m)", 
        min_value=0.8, max_value=15.0, value=2.0, step=0.1,
        help="Average wing width from leading edge to trailing edge."
    )
    
    sweep_angle = st.sidebar.slider(
        "Sweep Angle (°)", 
        min_value=0.0, max_value=60.0, value=5.0, step=1.0,
        help="Wing backward angle. Higher sweep enables higher speeds but reduces efficiency."
    )
    
    dihedral_angle = st.sidebar.slider(
        "Dihedral Angle (°)", 
        min_value=-10.0, max_value=15.0, value=2.0, step=0.5,
        help="Upward wing angle. Positive values improve stability."
    )
    
    taper_ratio = st.sidebar.slider(
        "Taper Ratio", 
        min_value=0.2, max_value=1.0, value=0.6, step=0.05,
        help="Ratio of tip chord to root chord. Lower values reduce weight and drag."
    )
    
    thickness_ratio = st.sidebar.slider(
        "Thickness Ratio", 
        min_value=0.06, max_value=0.20, value=0.12, step=0.01,
        help="Wing thickness as fraction of chord. Higher values provide structural strength."
    )
    
    st.sidebar.markdown("### Fuselage Geometry")
    
    fuselage_length = st.sidebar.slider(
        "Fuselage Length (m)", 
        min_value=6.0, max_value=80.0, value=15.0, step=0.5,
        help="Total aircraft length from nose to tail."
    )
    
    fuselage_diameter = st.sidebar.slider(
        "Fuselage Diameter (m)", 
        min_value=0.8, max_value=8.0, value=1.8, step=0.1,
        help="Maximum fuselage width. Affects passenger/cargo capacity and drag."
    )
    
    st.sidebar.markdown("### Mass Properties")
    
    max_takeoff_weight = st.sidebar.number_input(
        "Max Takeoff Weight (kg)", 
        min_value=500, max_value=600000, value=12000, step=100,
        help="Maximum weight at takeoff including fuel, payload, and structure."
    )
    
    empty_weight = st.sidebar.number_input(
        "Empty Weight (kg)", 
        min_value=300, max_value=400000, value=7500, step=100,
        help="Weight of aircraft structure, engines, and systems without fuel/payload."
    )
    
    fuel_capacity = st.sidebar.number_input(
        "Fuel Capacity (kg)", 
        min_value=50, max_value=200000, value=3000, step=50,
        help="Maximum fuel weight. Higher capacity increases range but reduces payload."
    )
    
    # Calculate derived parameters
    aspect_ratio = wing_span**2 / wing_area if wing_area > 0 else 1.0
    payload_weight = max_takeoff_weight - empty_weight - fuel_capacity
    wing_loading = max_takeoff_weight * 9.81 / wing_area if wing_area > 0 else 0
    fuel_fraction = fuel_capacity / max_takeoff_weight if max_takeoff_weight > 0 else 0
    
    # Display calculated parameters
    st.sidebar.markdown("### 📊 Calculated Parameters")
    st.sidebar.metric("Aspect Ratio", f"{aspect_ratio:.2f}")
    st.sidebar.metric("Wing Loading", f"{wing_loading:.0f} N/m²")
    st.sidebar.metric("Fuel Fraction", f"{fuel_fraction:.1%}")
    st.sidebar.metric("Payload Weight", f"{payload_weight:.0f} kg")
    
    return {
        'name': aircraft_name,
        'wing_span': wing_span,
        'wing_area': wing_area,
        'wing_chord': wing_chord,
        'aspect_ratio': aspect_ratio,
        'sweep_angle': sweep_angle,
        'dihedral_angle': dihedral_angle,
        'taper_ratio': taper_ratio,
        'thickness_ratio': thickness_ratio,
        'fuselage_length': fuselage_length,
        'fuselage_diameter': fuselage_diameter,
        'max_takeoff_weight': max_takeoff_weight,
        'empty_weight': empty_weight,
        'fuel_capacity': fuel_capacity,
        'payload_weight': payload_weight,
        'wing_loading': wing_loading,
        'fuel_fraction': fuel_fraction
    }


def create_aircraft_from_params(params):
    """Create Aircraft object from parameter dictionary."""
    geometry = AircraftGeometry(
        wing_span=params['wing_span'],
        wing_area=params['wing_area'],
        wing_chord=params['wing_chord'],
        aspect_ratio=params['aspect_ratio'],
        sweep_angle=params['sweep_angle'],
        dihedral_angle=params['dihedral_angle'],
        taper_ratio=params['taper_ratio'],
        thickness_ratio=params['thickness_ratio'],
        fuselage_length=params['fuselage_length'],
        fuselage_diameter=params['fuselage_diameter']
    )
    
    mass = AircraftMass(
        empty_weight=params['empty_weight'],
        fuel_capacity=params['fuel_capacity'],
        payload_capacity=params['payload_weight'],
        max_takeoff_weight=params['max_takeoff_weight']
    )
    
    return Aircraft(name=params['name'], geometry=geometry, mass=mass)


def display_design_assessment(aircraft, params):
    """Display real-time design assessment."""
    st.markdown('<div class="assessment-box">', unsafe_allow_html=True)
    st.markdown("## 🔍 Design Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Strengths")
        
        # Aspect ratio assessment
        if params['aspect_ratio'] > 8:
            st.success("🟢 High aspect ratio → Excellent fuel efficiency")
        elif params['aspect_ratio'] < 5:
            st.info("🔵 Low aspect ratio → High maneuverability")
        else:
            st.info("🔵 Moderate aspect ratio → Balanced performance")
        
        # Sweep angle assessment
        if params['sweep_angle'] > 20:
            st.success("🟢 Swept wing → High-speed capability")
        elif params['sweep_angle'] < 5:
            st.success("🟢 Straight wing → Excellent low-speed handling")
        else:
            st.info("🔵 Moderate sweep → Balanced speed capability")
    
    with col2:
        st.markdown("### Trade-offs")
        
        # Wing loading assessment
        if params['wing_loading'] > 4000:
            st.warning("🟡 High wing loading → Fast cruise, long runways needed")
        elif params['wing_loading'] < 1500:
            st.success("🟢 Low wing loading → Short runway capability")
        else:
            st.info("🔵 Moderate wing loading → Versatile performance")
        
        # Fuel fraction assessment
        if params['fuel_fraction'] > 0.4:
            st.info("🔵 High fuel fraction → Long range, reduced payload")
        elif params['fuel_fraction'] < 0.2:
            st.warning("🟡 Low fuel fraction → Limited range, high payload")
        else:
            st.success("🟢 Balanced fuel fraction → Good range-payload balance")
    
    st.markdown('</div>', unsafe_allow_html=True)


def calculate_performance_metrics(aircraft):
    """Calculate and return performance metrics."""
    analyzer = PerformanceAnalyzer(aircraft)
    
    # Standard atmospheric conditions
    atm_sl = AtmosphericConditions.standard_atmosphere(0)
    atm_cruise = AtmosphericConditions.standard_atmosphere(10000)
    
    try:
        # Basic performance metrics
        optimal_aoa = analyzer.find_optimal_angle_of_attack()
        max_ld = aircraft.calculate_lift_drag_ratio(optimal_aoa, atm_sl)
        stall_speed_sl = analyzer.calculate_stall_speed(atm_sl, aircraft.mass.max_takeoff_weight)
        
        # Mission performance
        range_km = analyzer.calculate_range(10000, 200, aircraft.mass.fuel_capacity) / 1000
        endurance_hrs = analyzer.calculate_endurance(10000, aircraft.mass.fuel_capacity) / 3600
        service_ceiling = analyzer.calculate_service_ceiling()
        
        # Takeoff performance
        takeoff_data = analyzer.analyze_takeoff_performance(3000)
        
        return {
            'optimal_aoa': optimal_aoa,
            'max_ld': max_ld,
            'stall_speed_sl': stall_speed_sl,
            'stall_speed_kmh': stall_speed_sl * 3.6,
            'range_km': range_km,
            'endurance_hrs': endurance_hrs,
            'service_ceiling': service_ceiling,
            'service_ceiling_km': service_ceiling / 1000,
            'takeoff_distance': takeoff_data['total_distance']
        }
    except Exception as e:
        st.error(f"Error calculating performance: {e}")
        return None


def get_feasibility_assessment(metrics):
    """Assess flight feasibility based on key metrics."""
    if metrics is None:
        return None
    
    assessments = {}
    overall_score = 0
    
    # Stall Speed Assessment (30% weight)
    stall_kmh = metrics['stall_speed_kmh']
    if stall_kmh < 100:
        assessments['stall'] = {'level': 'excellent', 'score': 100, 'color': '🟢', 'status': 'Excellent'}
    elif stall_kmh < 150:
        assessments['stall'] = {'level': 'good', 'score': 85, 'color': '🟢', 'status': 'Good'}
    elif stall_kmh < 200:
        assessments['stall'] = {'level': 'acceptable', 'score': 70, 'color': '🟡', 'status': 'Acceptable'}
    elif stall_kmh < 250:
        assessments['stall'] = {'level': 'marginal', 'score': 50, 'color': '🟡', 'status': 'Marginal'}
    elif stall_kmh < 300:
        assessments['stall'] = {'level': 'problematic', 'score': 25, 'color': '🔴', 'status': 'Problematic'}
    else:
        assessments['stall'] = {'level': 'critical', 'score': 5, 'color': '🔴', 'status': 'Critical'}
    overall_score += assessments['stall']['score'] * 0.30
    
    # L/D Ratio Assessment (25% weight)
    ld_ratio = metrics['max_ld']
    if ld_ratio > 15:
        assessments['ld'] = {'level': 'excellent', 'score': 100, 'color': '🟢', 'status': 'Excellent'}
    elif ld_ratio > 12:
        assessments['ld'] = {'level': 'good', 'score': 85, 'color': '🟢', 'status': 'Good'}
    elif ld_ratio > 8:
        assessments['ld'] = {'level': 'acceptable', 'score': 70, 'color': '🟡', 'status': 'Acceptable'}
    elif ld_ratio > 6:
        assessments['ld'] = {'level': 'marginal', 'score': 50, 'color': '🟡', 'status': 'Marginal'}
    elif ld_ratio > 4:
        assessments['ld'] = {'level': 'problematic', 'score': 25, 'color': '🔴', 'status': 'Problematic'}
    else:
        assessments['ld'] = {'level': 'critical', 'score': 5, 'color': '🔴', 'status': 'Critical'}
    overall_score += assessments['ld']['score'] * 0.25
    
    # Takeoff Distance Assessment (20% weight)
    takeoff_dist = metrics['takeoff_distance']
    if takeoff_dist < 300:
        assessments['takeoff'] = {'level': 'excellent', 'score': 100, 'color': '🟢', 'status': 'Excellent'}
    elif takeoff_dist < 800:
        assessments['takeoff'] = {'level': 'good', 'score': 85, 'color': '🟢', 'status': 'Good'}
    elif takeoff_dist < 1500:
        assessments['takeoff'] = {'level': 'acceptable', 'score': 70, 'color': '🟡', 'status': 'Acceptable'}
    elif takeoff_dist < 2500:
        assessments['takeoff'] = {'level': 'marginal', 'score': 50, 'color': '🟡', 'status': 'Marginal'}
    elif takeoff_dist < 4000:
        assessments['takeoff'] = {'level': 'problematic', 'score': 25, 'color': '🔴', 'status': 'Problematic'}
    else:
        assessments['takeoff'] = {'level': 'critical', 'score': 5, 'color': '🔴', 'status': 'Critical'}
    overall_score += assessments['takeoff']['score'] * 0.20
    
    # Service Ceiling Assessment (10% weight)
    ceiling_km = metrics['service_ceiling_km']
    if ceiling_km > 12:
        assessments['ceiling'] = {'level': 'excellent', 'score': 100, 'color': '🟢', 'status': 'Excellent'}
    elif ceiling_km > 8:
        assessments['ceiling'] = {'level': 'good', 'score': 85, 'color': '🟢', 'status': 'Good'}
    elif ceiling_km > 5:
        assessments['ceiling'] = {'level': 'acceptable', 'score': 70, 'color': '🟡', 'status': 'Acceptable'}
    elif ceiling_km > 3:
        assessments['ceiling'] = {'level': 'marginal', 'score': 50, 'color': '🟡', 'status': 'Marginal'}
    elif ceiling_km > 1:
        assessments['ceiling'] = {'level': 'problematic', 'score': 25, 'color': '🔴', 'status': 'Problematic'}
    else:
        assessments['ceiling'] = {'level': 'critical', 'score': 5, 'color': '🔴', 'status': 'Critical'}
    overall_score += assessments['ceiling']['score'] * 0.10
    
    # Overall Assessment
    if overall_score >= 90:
        overall = {'level': 'excellent', 'color': '🟢', 'status': 'Highly Flyable', 'score': overall_score}
    elif overall_score >= 70:
        overall = {'level': 'good', 'color': '🟢', 'status': 'Flyable', 'score': overall_score}
    elif overall_score >= 50:
        overall = {'level': 'acceptable', 'color': '🟡', 'status': 'Flyable with Limitations', 'score': overall_score}
    elif overall_score >= 30:
        overall = {'level': 'marginal', 'color': '🟡', 'status': 'Challenging', 'score': overall_score}
    elif overall_score >= 10:
        overall = {'level': 'problematic', 'color': '🔴', 'status': 'Significant Problems', 'score': overall_score}
    else:
        overall = {'level': 'critical', 'color': '🔴', 'status': 'Unlikely to Fly', 'score': overall_score}
    
    return {
        'assessments': assessments,
        'overall': overall
    }


def display_flight_feasibility(metrics, params):
    """Display flight feasibility assessment."""
    feasibility = get_feasibility_assessment(metrics)
    if feasibility is None:
        return
    
    st.markdown("## ✈️ Flight Feasibility Assessment")
    
    # Overall Assessment
    overall = feasibility['overall']
    
    # Create prominent overall assessment box
    if overall['level'] in ['excellent', 'good']:
        st.success(f"**{overall['color']} OVERALL: {overall['status']}** (Score: {overall['score']:.0f}/100)")
    elif overall['level'] in ['acceptable', 'marginal']:
        st.warning(f"**{overall['color']} OVERALL: {overall['status']}** (Score: {overall['score']:.0f}/100)")
    else:
        st.error(f"**{overall['color']} OVERALL: {overall['status']}** (Score: {overall['score']:.0f}/100)")
    
    # Detailed breakdown
    st.markdown("### 📊 Detailed Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Stall Speed
        stall_assess = feasibility['assessments']['stall']
        st.metric(
            f"{stall_assess['color']} Stall Speed",
            f"{metrics['stall_speed_kmh']:.0f} km/h",
            delta=f"{stall_assess['status']} (30% weight)"
        )
        
        # L/D Ratio  
        ld_assess = feasibility['assessments']['ld']
        st.metric(
            f"{ld_assess['color']} L/D Ratio",
            f"{metrics['max_ld']:.1f}",
            delta=f"{ld_assess['status']} (25% weight)"
        )
    
    with col2:
        # Takeoff Distance
        takeoff_assess = feasibility['assessments']['takeoff']
        st.metric(
            f"{takeoff_assess['color']} Takeoff Distance",
            f"{metrics['takeoff_distance']:.0f} m",
            delta=f"{takeoff_assess['status']} (20% weight)"
        )
        
        # Service Ceiling
        ceiling_assess = feasibility['assessments']['ceiling']
        st.metric(
            f"{ceiling_assess['color']} Service Ceiling",
            f"{metrics['service_ceiling_km']:.1f} km",
            delta=f"{ceiling_assess['status']} (10% weight)"
        )
    
    # Red Flags Section
    red_flags = []
    
    if metrics['stall_speed_kmh'] > 300:
        red_flags.append("🚨 Extremely high stall speed - dangerous for most applications")
    if metrics['max_ld'] < 4:
        red_flags.append("🚨 Very poor L/D ratio - flight may be unsustainable")
    if metrics['takeoff_distance'] > 4000:
        red_flags.append("🚨 Extreme takeoff distance - requires specialized facilities")
    if params['wing_loading'] > 8000:
        red_flags.append("🚨 Extreme wing loading - requires exceptional performance")
    if params['aspect_ratio'] < 1:
        red_flags.append("🚨 Very low aspect ratio - aerodynamically questionable")
    if params['fuel_fraction'] > 0.9:
        red_flags.append("🚨 Excessive fuel fraction - impractical design")
    if params['empty_weight'] > params['max_takeoff_weight']:
        red_flags.append("🚨 Empty weight exceeds MTOW - mass budget error")
    
    if red_flags:
        st.markdown("### 🚨 Critical Design Issues")
        for flag in red_flags:
            st.error(flag)
    
    # Improvement Suggestions
    if overall['level'] in ['marginal', 'problematic', 'critical']:
        st.markdown("### 💡 Improvement Suggestions")
        
        if metrics['stall_speed_kmh'] > 200:
            st.info("**To reduce stall speed:** Increase wing area, improve CL_max, or reduce weight")
        if metrics['max_ld'] < 8:
            st.info("**To improve L/D ratio:** Increase aspect ratio, reduce parasitic drag, optimize airfoils")
        if metrics['takeoff_distance'] > 1500:
            st.info("**To reduce takeoff distance:** Increase wing area, add high-lift devices, or increase thrust")
        if metrics['service_ceiling_km'] < 5:
            st.info("**To increase service ceiling:** Reduce wing loading, increase power, or improve L/D ratio")


def display_performance_metrics(metrics):
    """Display performance metrics in organized layout."""
    if metrics is None:
        return
    
    st.markdown("## 📊 Performance Analysis")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Max L/D Ratio", 
            f"{metrics['max_ld']:.1f}",
            help="Higher is better for efficiency"
        )
        st.metric(
            "Optimal AoA", 
            f"{metrics['optimal_aoa']:.1f}°",
            help="Angle of attack for best efficiency"
        )
    
    with col2:
        st.metric(
            "Stall Speed", 
            f"{metrics['stall_speed_kmh']:.0f} km/h",
            help="Minimum flying speed at sea level"
        )
        st.metric(
            "Range", 
            f"{metrics['range_km']:.0f} km",
            help="Estimated maximum range"
        )
    
    with col3:
        st.metric(
            "Endurance", 
            f"{metrics['endurance_hrs']:.1f} hrs",
            help="Maximum flight time"
        )
        st.metric(
            "Service Ceiling", 
            f"{metrics['service_ceiling_km']:.1f} km",
            help="Maximum operational altitude"
        )
    
    with col4:
        st.metric(
            "Takeoff Distance", 
            f"{metrics['takeoff_distance']:.0f} m",
            help="Runway length required"
        )


def create_interactive_plots(aircraft):
    """Create interactive Plotly visualizations."""
    analyzer = PerformanceAnalyzer(aircraft)
    
    # Create tabs for different plot types
    tab1, tab2, tab3, tab4 = st.tabs(["Drag Polar", "L/D vs AoA", "Performance Envelope", "V-n Diagram"])
    
    with tab1:
        st.markdown("### Drag Polar")
        
        # Generate drag polar data
        aoa_range = np.linspace(-5, 20, 50)
        atm = AtmosphericConditions.standard_atmosphere(0)
        
        cl_values = []
        cd_values = []
        
        for aoa in aoa_range:
            try:
                cl = aircraft.calculate_lift_coefficient(aoa, atm)
                cd = aircraft.calculate_drag_coefficient(aoa, atm)
                cl_values.append(cl)
                cd_values.append(cd)
            except:
                cl_values.append(0)
                cd_values.append(0.1)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cd_values, y=cl_values,
            mode='lines+markers',
            name='Drag Polar',
            line=dict(color='blue', width=2),
            marker=dict(size=4)
        ))
        
        fig.update_layout(
            title="Lift Coefficient vs Drag Coefficient",
            xaxis_title="Drag Coefficient (CD)",
            yaxis_title="Lift Coefficient (CL)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Lift-to-Drag Ratio vs Angle of Attack")
        
        ld_ratios = []
        for i, aoa in enumerate(aoa_range):
            if cd_values[i] > 0:
                ld_ratios.append(cl_values[i] / cd_values[i])
            else:
                ld_ratios.append(0)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=aoa_range, y=ld_ratios,
            mode='lines+markers',
            name='L/D Ratio',
            line=dict(color='green', width=2),
            marker=dict(size=4)
        ))
        
        # Highlight optimal point
        max_ld_idx = np.argmax(ld_ratios)
        fig.add_trace(go.Scatter(
            x=[aoa_range[max_ld_idx]], y=[ld_ratios[max_ld_idx]],
            mode='markers',
            name='Optimal Point',
            marker=dict(size=12, color='red', symbol='star')
        ))
        
        fig.update_layout(
            title="Lift-to-Drag Ratio vs Angle of Attack",
            xaxis_title="Angle of Attack (degrees)",
            yaxis_title="L/D Ratio",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Performance Envelope")
        
        # Create 3D performance surface
        altitudes = np.linspace(0, 15000, 20)
        speeds = np.linspace(50, 300, 20)
        
        Alt, Speed = np.meshgrid(altitudes, speeds)
        Performance = np.zeros_like(Alt)
        
        for i, alt in enumerate(altitudes):
            for j, speed in enumerate(speeds):
                try:
                    atm = AtmosphericConditions.standard_atmosphere(alt)
                    # Simple performance metric (inverse of power required)
                    Performance[j, i] = 1 / (speed**2 + alt/1000)
                except:
                    Performance[j, i] = 0
        
        fig = go.Figure(data=[go.Surface(
            z=Performance,
            x=Alt,
            y=Speed,
            colorscale='Viridis'
        )])
        
        fig.update_layout(
            title='Performance Envelope',
            scene=dict(
                xaxis_title='Altitude (m)',
                yaxis_title='Speed (m/s)',
                zaxis_title='Performance Index'
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### V-n Diagram (Flight Envelope)")
        
        # Generate V-n diagram data
        speeds = np.linspace(20, 400, 100)
        load_factors_pos = []
        load_factors_neg = []
        
        for speed in speeds:
            try:
                # Simplified load factor calculation
                max_load = min(6.0, 200000 / (speed**2 + 1000))  # Simplified
                min_load = max(-3.0, -100000 / (speed**2 + 1000))  # Simplified
                load_factors_pos.append(max_load)
                load_factors_neg.append(min_load)
            except:
                load_factors_pos.append(1.0)
                load_factors_neg.append(-1.0)
        
        fig = go.Figure()
        
        # Positive load factors
        fig.add_trace(go.Scatter(
            x=speeds, y=load_factors_pos,
            mode='lines',
            name='Positive Load Limit',
            line=dict(color='blue', width=2),
            fill='tonexty'
        ))
        
        # Negative load factors
        fig.add_trace(go.Scatter(
            x=speeds, y=load_factors_neg,
            mode='lines',
            name='Negative Load Limit',
            line=dict(color='red', width=2),
            fill='tozeroy'
        ))
        
        # Add reference lines
        fig.add_hline(y=1, line_dash="dash", line_color="gray", annotation_text="1g")
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title="V-n Diagram (Flight Envelope)",
            xaxis_title="Velocity (m/s)",
            yaxis_title="Load Factor (g)",
            height=500,
            yaxis=dict(range=[-4, 7])
        )
        
        st.plotly_chart(fig, use_container_width=True)


def create_3d_visualization(aircraft, params):
    """Create 3D aircraft visualization."""
    st.markdown("## 🛩️ 3D Aircraft Visualization")
    
    try:
        visualizer_3d = Aircraft3DVisualizer(aircraft)
        
        # Create interactive 3D plot
        fig = visualizer_3d.create_interactive_3d_plotly()
        
        # Update layout for Streamlit
        fig.update_layout(
            height=600,
            title=f"3D Model: {params['name']}",
            scene=dict(
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.5),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0)
                )
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display 3D model info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Wing Span:** {params['wing_span']:.1f} m")
        with col2:
            st.info(f"**Fuselage Length:** {params['fuselage_length']:.1f} m")
        with col3:
            st.info(f"**Scale:** 1:1 (True proportions)")
        
    except Exception as e:
        st.error(f"Error creating 3D visualization: {e}")


def save_design_to_session(params, aircraft, metrics):
    """Save current design to session state."""
    design_data = {
        'params': params,
        'aircraft': aircraft,
        'metrics': metrics,
        'timestamp': datetime.datetime.now()
    }
    
    st.session_state.aircraft_designs[params['name']] = design_data
    st.success(f"Design '{params['name']}' saved to session!")


def display_design_comparison():
    """Display comparison of saved designs."""
    if len(st.session_state.aircraft_designs) < 2:
        st.info("Save at least 2 designs to enable comparison.")
        return
    
    st.markdown("## ⚖️ Design Comparison")
    
    design_names = list(st.session_state.aircraft_designs.keys())
    selected_designs = st.multiselect(
        "Select designs to compare:",
        design_names,
        default=design_names[:2] if len(design_names) >= 2 else design_names
    )
    
    if len(selected_designs) < 2:
        st.warning("Please select at least 2 designs to compare.")
        return
    
    # Create comparison table
    comparison_data = []
    for name in selected_designs:
        design = st.session_state.aircraft_designs[name]
        params = design['params']
        metrics = design['metrics']
        
        if metrics:
            comparison_data.append({
                'Design': name,
                'Wing Span (m)': params['wing_span'],
                'Wing Area (m²)': params['wing_area'],
                'Aspect Ratio': params['aspect_ratio'],
                'Wing Loading (N/m²)': params['wing_loading'],
                'Max L/D': metrics['max_ld'],
                'Stall Speed (km/h)': metrics['stall_speed_kmh'],
                'Range (km)': metrics['range_km'],
                'Service Ceiling (km)': metrics['service_ceiling_km']
            })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
        
        # Create comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df, x='Design', y='Max L/D', title='L/D Ratio Comparison')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(df, x='Design', y='Range (km)', title='Range Comparison')
            st.plotly_chart(fig, use_container_width=True)


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # App header
    st.markdown('<h1 class="main-header">✈️ Aircraft Design Studio</h1>', unsafe_allow_html=True)
    st.markdown("Design, analyze, and visualize custom aircraft with real-time performance feedback.")
    
    # Add documentation link
    with st.expander("📚 Flight Feasibility Guide & Equations"):
        st.markdown("""
        **New!** Comprehensive flight feasibility assessment is now integrated into the app.
        
        The system evaluates your design using aerospace engineering principles and provides:
        - **Real-time feasibility scoring** (0-100 points)
        - **Color-coded assessments** (🟢 Good, 🟡 Marginal, 🔴 Problematic)
        - **Critical issue detection** with red flags
        - **Improvement suggestions** for problematic designs
        
        **Key Equations Used:**
        - Stall Speed: `V_stall = √(2×W/(ρ×CL_max×S))`
        - Lift-to-Drag: `L/D = CL/CD`
        - Wing Loading: `WL = W/S`
        - Takeoff Distance: `s_TO ≈ 1.44×W²/(ρ×g×CL_max×S×T)`
        
        **Assessment Weights:**
        - Stall Speed: 30% (most critical for safety)
        - L/D Ratio: 25% (efficiency and performance)
        - Takeoff Distance: 20% (operational flexibility)
        - Service Ceiling: 10% (altitude capability)
        - Design Sanity: 15% (physics violations)
        
        📖 **For complete equations and criteria, see:** `docs/FLIGHT_FEASIBILITY.md`
        """)
    
    # Main layout
    params = create_parameter_inputs()
    
    # Create aircraft object
    aircraft = create_aircraft_from_params(params)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Design Analysis", "📊 Performance Plots", "🛩️ 3D Visualization", "⚖️ Compare Designs"])
    
    with tab1:
        # Display design assessment
        display_design_assessment(aircraft, params)
        
        # Calculate and display performance metrics
        with st.spinner("Calculating performance metrics..."):
            metrics = calculate_performance_metrics(aircraft)
        
        if metrics:
            # Flight Feasibility Assessment (NEW!)
            display_flight_feasibility(metrics, params)
            
            # Performance Metrics
            display_performance_metrics(metrics)
            
            # Save design button
            if st.button("💾 Save This Design", type="primary"):
                save_design_to_session(params, aircraft, metrics)
        
        # Store current design in session
        st.session_state.current_design = {
            'params': params,
            'aircraft': aircraft,
            'metrics': metrics
        }
    
    with tab2:
        st.markdown('<div class="section-header">Performance Analysis</div>', unsafe_allow_html=True)
        with st.spinner("Generating interactive plots..."):
            create_interactive_plots(aircraft)
    
    with tab3:
        create_3d_visualization(aircraft, params)
    
    with tab4:
        display_design_comparison()
    
    # Footer
    st.markdown("---")
    st.markdown("*Aircraft Design Studio v1.0 - Built with Streamlit and Python*")


if __name__ == "__main__":
    main()
