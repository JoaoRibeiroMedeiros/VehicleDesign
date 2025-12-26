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
    .persistent-3d-container {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 2px solid #e9ecef;
    }
    .comparison-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
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
        max_ld = aircraft.calculate_lift_drag_ratio(optimal_aoa)
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
        
        cl_values = []
        cd_values = []
        
        for aoa in aoa_range:
            try:
                cl = aircraft.calculate_lift_coefficient(aoa)
                cd = aircraft.calculate_drag_coefficient(cl)
                cl_values.append(cl)
                cd_values.append(cd)
            except Exception as e:
                # Skip invalid points or use reasonable defaults
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


def create_3d_visualization_persistent(aircraft, params):
    """Create persistent 3D aircraft visualization that maintains state."""
    try:
        visualizer_3d = Aircraft3DVisualizer(aircraft)
        
        # Create interactive 3D plot
        fig = visualizer_3d.create_interactive_3d_plotly()
        
        # Update layout for persistent view
        fig.update_layout(
            height=500,
            title=f"{params['name']}",
            scene=dict(
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.5),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0)
                )
            ),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Use session state key to maintain camera position
        st.plotly_chart(fig, use_container_width=True, key="persistent_3d_view")
        
        # Display compact 3D model info
        st.markdown(f"""
        **📏 Dimensions:** {params['wing_span']:.1f}m × {params['fuselage_length']:.1f}m  
        **⚖️ MTOW:** {params['max_takeoff_weight']:,.0f} kg  
        **📊 AR:** {params['aspect_ratio']:.1f} | **🔄 Sweep:** {params['sweep_angle']:.0f}°
        """)
        
    except Exception as e:
        st.error(f"Error creating 3D visualization: {e}")


def display_saved_designs_summary():
    """Display summary of saved designs."""
    if not st.session_state.aircraft_designs:
        st.info("No saved designs yet. Save your current design to see it here!")
        return
    
    st.markdown("### Saved Aircraft Designs")
    
    # Create summary table
    designs_summary = []
    for name, design_data in st.session_state.aircraft_designs.items():
        params = design_data['params']
        metrics = design_data['metrics']
        timestamp = design_data['timestamp']
        
        summary = {
            'Name': name,
            'Saved': timestamp.strftime('%Y-%m-%d %H:%M'),
            'Span (m)': f"{params['wing_span']:.1f}",
            'AR': f"{params['aspect_ratio']:.1f}",
            'MTOW (kg)': f"{params['max_takeoff_weight']:,.0f}",
        }
        
        if metrics:
            summary.update({
                'Max L/D': f"{metrics['max_ld']:.1f}",
                'Stall Speed (km/h)': f"{metrics['stall_speed_kmh']:.0f}",
                'Range (km)': f"{metrics['range_km']:.0f}"
            })
        
        designs_summary.append(summary)
    
    if designs_summary:
        df = pd.DataFrame(designs_summary)
        st.dataframe(df, use_container_width=True)
        
        # Quick actions
        st.markdown("### Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_design = st.selectbox(
                "Load Design:",
                list(st.session_state.aircraft_designs.keys()),
                key="load_design_select"
            )
            if st.button("📥 Load Selected Design"):
                load_design_to_current(selected_design)
        
        with col2:
            if len(st.session_state.aircraft_designs) >= 2:
                if st.button("⚖️ Compare All Designs"):
                    st.session_state.comparison_mode = True
                    st.experimental_rerun()
        
        # Delete design option
        with st.expander("🗑️ Delete Designs"):
            delete_design = st.selectbox(
                "Select design to delete:",
                [""] + list(st.session_state.aircraft_designs.keys()),
                key="delete_design_select"
            )
            if delete_design and st.button("🗑️ Delete Selected Design", type="secondary"):
                del st.session_state.aircraft_designs[delete_design]
                st.success(f"Deleted design: {delete_design}")
                st.experimental_rerun()


def load_design_to_current(design_name):
    """Load a saved design as the current design."""
    if design_name not in st.session_state.aircraft_designs:
        st.error(f"Design '{design_name}' not found!")
        return
    
    design_data = st.session_state.aircraft_designs[design_name]
    
    # Update sidebar parameters (this would require parameter state management)
    st.info(f"To load '{design_name}', manually adjust the parameters in the sidebar to match the values shown in the table above.")
    
    # Note: Full parameter loading would require more complex state management
    # For now, we show the user the parameters to manually adjust


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


# Old comparison function removed - now using dedicated comparison page


def create_comparison_page():
    """Create dedicated comparison page with side-by-side 3D views."""
    st.markdown('<div class="comparison-header"><h1>⚖️ Aircraft Design Comparison</h1><p>Compare multiple aircraft designs with side-by-side 3D visualizations and detailed metrics.</p></div>', unsafe_allow_html=True)
    
    if len(st.session_state.aircraft_designs) < 2:
        st.info("Save at least 2 designs from the main design studio to enable comparison.")
        if st.button("🔙 Back to Design Studio"):
            st.session_state.comparison_mode = False
            st.experimental_rerun()
        return
    
    design_names = list(st.session_state.aircraft_designs.keys())
    
    # Design selection
    st.markdown("### Select Designs to Compare")
    col1, col2 = st.columns(2)
    
    with col1:
        design_a = st.selectbox(
            "First Design:",
            design_names,
            key="design_a"
        )
    
    with col2:
        design_b = st.selectbox(
            "Second Design:",
            [name for name in design_names if name != design_a],
            key="design_b"
        )
    
    if design_a and design_b:
        design_data_a = st.session_state.aircraft_designs[design_a]
        design_data_b = st.session_state.aircraft_designs[design_b]
        
        # Side-by-side 3D visualizations
        st.markdown("### 3D Model Comparison")
        col_3d_a, col_3d_b = st.columns(2)
        
        with col_3d_a:
            st.markdown(f"**{design_a}**")
            create_3d_visualization_compact(design_data_a['aircraft'], design_data_a['params'])
        
        with col_3d_b:
            st.markdown(f"**{design_b}**")
            create_3d_visualization_compact(design_data_b['aircraft'], design_data_b['params'])
        
        # Detailed comparison metrics
        display_detailed_comparison(design_data_a, design_data_b)
        
        # Performance plots comparison
        create_comparison_plots(design_data_a, design_data_b)
    
    # Back button
    if st.button("🔙 Back to Design Studio"):
        st.session_state.comparison_mode = False
        st.experimental_rerun()


def create_3d_visualization_compact(aircraft, params):
    """Create compact 3D aircraft visualization for comparison view."""
    try:
        visualizer_3d = Aircraft3DVisualizer(aircraft)
        
        # Create interactive 3D plot
        fig = visualizer_3d.create_interactive_3d_plotly()
        
        # Update layout for compact view
        fig.update_layout(
            height=400,
            title=None,  # No title to save space
            scene=dict(
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.5),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0)
                )
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display key specs
        st.info(f"**Span:** {params['wing_span']:.1f}m | **Length:** {params['fuselage_length']:.1f}m | **MTOW:** {params['max_takeoff_weight']:.0f}kg")
        
    except Exception as e:
        st.error(f"Error creating 3D visualization: {e}")


def display_detailed_comparison(design_a, design_b):
    """Display detailed comparison metrics between two designs."""
    st.markdown("### Detailed Performance Comparison")
    
    params_a = design_a['params']
    params_b = design_b['params']
    metrics_a = design_a['metrics']
    metrics_b = design_b['metrics']
    
    if not metrics_a or not metrics_b:
        st.warning("Performance metrics missing for one or both designs.")
        return
    
    # Create comparison table
    comparison_data = {
        'Metric': [
            'Wing Span (m)',
            'Wing Area (m²)',
            'Aspect Ratio',
            'Wing Loading (N/m²)',
            'Fuel Fraction (%)',
            'Max L/D Ratio',
            'Stall Speed (km/h)',
            'Range (km)',
            'Endurance (hrs)',
            'Service Ceiling (km)',
            'Takeoff Distance (m)'
        ],
        params_a['name']: [
            params_a['wing_span'],
            params_a['wing_area'],
            params_a['aspect_ratio'],
            params_a['wing_loading'],
            params_a['fuel_fraction'] * 100,
            metrics_a['max_ld'],
            metrics_a['stall_speed_kmh'],
            metrics_a['range_km'],
            metrics_a['endurance_hrs'],
            metrics_a['service_ceiling_km'],
            metrics_a['takeoff_distance']
        ],
        params_b['name']: [
            params_b['wing_span'],
            params_b['wing_area'],
            params_b['aspect_ratio'],
            params_b['wing_loading'],
            params_b['fuel_fraction'] * 100,
            metrics_b['max_ld'],
            metrics_b['stall_speed_kmh'],
            metrics_b['range_km'],
            metrics_b['endurance_hrs'],
            metrics_b['service_ceiling_km'],
            metrics_b['takeoff_distance']
        ]
    }
    
    # Calculate differences and add winner column
    differences = []
    winners = []
    
    for i, metric in enumerate(comparison_data['Metric']):
        val_a = comparison_data[params_a['name']][i]
        val_b = comparison_data[params_b['name']][i]
        
        diff = val_b - val_a
        diff_pct = (diff / val_a * 100) if val_a != 0 else 0
        
        # Determine better value based on metric type
        better_higher = metric in ['Wing Span (m)', 'Wing Area (m²)', 'Aspect Ratio', 'Max L/D Ratio', 
                                 'Range (km)', 'Endurance (hrs)', 'Service Ceiling (km)']
        better_lower = metric in ['Wing Loading (N/m²)', 'Stall Speed (km/h)', 'Takeoff Distance (m)']
        
        if better_higher:
            winner = params_b['name'] if val_b > val_a else params_a['name'] if val_a > val_b else "Tie"
        elif better_lower:
            winner = params_b['name'] if val_b < val_a else params_a['name'] if val_a < val_b else "Tie"
        else:
            winner = "N/A"
        
        differences.append(f"{diff:+.1f} ({diff_pct:+.1f}%)")
        winners.append(winner)
    
    comparison_data['Difference (B-A)'] = differences
    comparison_data['Better'] = winners
    
    # Display as dataframe
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    # Performance summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        a_wins = sum(1 for winner in winners if winner == params_a['name'])
        st.metric(f"{params_a['name']} Wins", a_wins)
    
    with col2:
        b_wins = sum(1 for winner in winners if winner == params_b['name'])
        st.metric(f"{params_b['name']} Wins", b_wins)
    
    with col3:
        ties = sum(1 for winner in winners if winner == "Tie")
        st.metric("Ties", ties)


def create_comparison_plots(design_a, design_b):
    """Create comparison plots for two designs."""
    st.markdown("### Performance Charts Comparison")
    
    aircraft_a = design_a['aircraft']
    aircraft_b = design_b['aircraft']
    
    # Create side-by-side comparison plots
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Drag Polar Comparison")
        
        # Generate drag polar data for both aircraft
        aoa_range = np.linspace(-5, 20, 50)
        
        cl_values_a, cd_values_a = [], []
        cl_values_b, cd_values_b = [], []
        
        for aoa in aoa_range:
            try:
                cl_a = aircraft_a.calculate_lift_coefficient(aoa)
                cd_a = aircraft_a.calculate_drag_coefficient(cl_a)
                cl_values_a.append(cl_a)
                cd_values_a.append(cd_a)
                
                cl_b = aircraft_b.calculate_lift_coefficient(aoa)
                cd_b = aircraft_b.calculate_drag_coefficient(cl_b)
                cl_values_b.append(cl_b)
                cd_values_b.append(cd_b)
            except:
                cl_values_a.append(0)
                cd_values_a.append(0.1)
                cl_values_b.append(0)
                cd_values_b.append(0.1)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cd_values_a, y=cl_values_a,
            mode='lines+markers',
            name=design_a['params']['name'],
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=cd_values_b, y=cl_values_b,
            mode='lines+markers',
            name=design_b['params']['name'],
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            xaxis_title="Drag Coefficient (CD)",
            yaxis_title="Lift Coefficient (CL)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Key Metrics Comparison")
        
        metrics_a = design_a['metrics']
        metrics_b = design_b['metrics']
        
        if metrics_a and metrics_b:
            # Radar chart comparison
            categories = ['Max L/D', 'Range (km/100)', 'Service Ceiling (km)', 'Endurance (hrs)']
            
            values_a = [
                metrics_a['max_ld'],
                metrics_a['range_km'] / 100,  # Scale for visualization
                metrics_a['service_ceiling_km'],
                metrics_a['endurance_hrs']
            ]
            
            values_b = [
                metrics_b['max_ld'],
                metrics_b['range_km'] / 100,  # Scale for visualization
                metrics_b['service_ceiling_km'],
                metrics_b['endurance_hrs']
            ]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values_a + [values_a[0]],  # Close the shape
                theta=categories + [categories[0]],
                fill='toself',
                name=design_a['params']['name'],
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=values_b + [values_b[0]],  # Close the shape
                theta=categories + [categories[0]],
                fill='toself',
                name=design_b['params']['name'],
                line=dict(color='red')
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(max(values_a), max(values_b)) * 1.1]
                    )),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Initialize comparison mode if not set
    if 'comparison_mode' not in st.session_state:
        st.session_state.comparison_mode = False
    
    # Route to comparison page if in comparison mode
    if st.session_state.comparison_mode:
        create_comparison_page()
        return
    
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
    
    # NEW LAYOUT: Main content with persistent 3D view
    # Create two main columns: sidebar for parameters, main area split between 3D and content
    main_container = st.container()
    
    with main_container:
        # Parameters in sidebar (existing)
        params = create_parameter_inputs()
        
        # Create aircraft object
        aircraft = create_aircraft_from_params(params)
        
        # Calculate metrics once for the session
        with st.spinner("Calculating performance metrics..."):
            metrics = calculate_performance_metrics(aircraft)
        
        # Store current design in session
        st.session_state.current_design = {
            'params': params,
            'aircraft': aircraft,
            'metrics': metrics
        }
        
        # Main content area: Split between persistent 3D and tabbed content
        col_3d, col_content = st.columns([1, 1])  # Equal width columns
        
        with col_3d:
            st.markdown('<div class="persistent-3d-container">', unsafe_allow_html=True)
            st.markdown("### 🛩️ Live 3D Model")
            create_3d_visualization_persistent(aircraft, params)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add save design button here for easy access
            if st.button("💾 Save Current Design", type="primary", use_container_width=True):
                save_design_to_session(params, aircraft, metrics)
            
            # Quick access to comparison if designs available
            if len(st.session_state.aircraft_designs) >= 2:
                if st.button("⚖️ Compare Designs", use_container_width=True):
                    st.session_state.comparison_mode = True
                    st.experimental_rerun()
        
        with col_content:
            # Tabbed content area (smaller tabs, no 3D tab needed)
            tab1, tab2, tab3 = st.tabs(["🔍 Design Analysis", "📊 Performance Plots", "📋 Saved Designs"])
            
            with tab1:
                # Display design assessment
                display_design_assessment(aircraft, params)
                
                if metrics:
                    # Flight Feasibility Assessment
                    display_flight_feasibility(metrics, params)
                    
                    # Performance Metrics
                    display_performance_metrics(metrics)
            
            with tab2:
                st.markdown('<div class="section-header">Performance Analysis</div>', unsafe_allow_html=True)
                with st.spinner("Generating interactive plots..."):
                    create_interactive_plots(aircraft)
            
            with tab3:
                display_saved_designs_summary()
    
    # Footer
    st.markdown("---")
    st.markdown("*Aircraft Design Studio v1.0 - Built with Streamlit and Python*")


if __name__ == "__main__":
    main()
