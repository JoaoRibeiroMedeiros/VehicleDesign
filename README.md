# Aircraft Design Exploration System

A comprehensive Python framework for exploring airplane designs and testing flight conditions. This system provides tools for aerodynamic analysis, performance evaluation, design optimization, advanced visualization, and **real-time flight feasibility assessment**.

## ✈️ New: Flight Feasibility Assessment

The system now includes **comprehensive flight feasibility analysis** that automatically evaluates whether your aircraft design will fly safely and efficiently. Features include:

- **🎯 Real-time scoring (0-100 points)** based on aerospace engineering principles
- **🟢🟡🔴 Color-coded assessments** for immediate visual feedback
- **🚨 Critical issue detection** with detailed red flags
- **💡 Smart improvement suggestions** for problematic designs
- **📊 Weighted scoring system** prioritizing safety-critical metrics

**📖 Complete Documentation:** See [`docs/FLIGHT_FEASIBILITY.md`](docs/FLIGHT_FEASIBILITY.md) for all equations, criteria, and assessment methods.

## 📁 Project Structure

```
VehicleDesign/
├── src/                          # Core modules (importable library)
│   ├── __init__.py              # Package initialization with exports
│   ├── aircraft.py              # Aircraft design classes and geometry
│   ├── flight_conditions.py     # Atmospheric modeling and flight parameters
│   ├── performance_analysis.py  # Performance calculations and analysis
│   ├── design_optimizer.py      # Multi-objective optimization framework
│   ├── visualization.py         # Plotting and visualization tools
│   ├── aircraft_3d.py           # 3D aircraft visualization and modeling
│   └── streamlit_app.py         # Interactive web application interface
├── scripts/                      # Executable scripts (inherit from src)
│   ├── __init__.py              # Scripts package initialization
│   ├── test_system.py           # System validation and testing
│   ├── run_examples.py          # Comprehensive analysis examples
│   ├── interactive_demo.py      # Interactive web-based visualizations
│   ├── design_your_aircraft.py  # Custom aircraft design wizard
│   ├── view_aircraft_3d.py      # 3D aircraft visualization examples
│   ├── explore_parameters.py    # Parameter explanation and examples
│   └── run_streamlit_app.py     # Streamlit web application launcher
├── docs/                        # Documentation and guides
│   └── FLIGHT_FEASIBILITY.md    # Complete flight feasibility guide
├── visualizations/               # All generated plots and dashboards
│   ├── *.png                    # Static performance plots
│   └── *.html                   # Interactive web dashboards
├── .venv/                        # Virtual environment
├── requirements.txt              # Python dependencies
├── activate.sh                   # Environment activation script
└── README.md                     # This file
```

## Features

### 📚 Comprehensive Documentation
- **Parameter Explanations**: Detailed docstrings for all aircraft parameters
- **Physical Significance**: Understanding of how each parameter affects performance
- **Typical Values**: Real-world ranges for different aircraft types
- **Design Trade-offs**: Insights into competing design requirements
- **Interactive Explorer**: Script to explore parameter relationships

### 🛩️ Aircraft Design Analysis
- **Geometric Parameters**: Wing span, area, aspect ratio, sweep angle, and more
- **Mass Properties**: Empty weight, fuel capacity, payload, MTOW
- **Aerodynamic Modeling**: Lift and drag coefficient calculations
- **Performance Metrics**: L/D ratios, stall speeds, wing loading

### 🌤️ Flight Conditions Testing
- **Atmospheric Modeling**: ISA standard atmosphere implementation
- **Flight Parameters**: Airspeed, altitude, angle of attack, load factors
- **Environmental Effects**: Temperature, pressure, density variations
- **Mach Number Calculations**: Compressibility effects

### 📊 Performance Analysis
- **Range & Endurance**: Breguet equations for mission analysis
- **Climb Performance**: Rate of climb, service ceiling calculations
- **Takeoff Analysis**: Ground roll, obstacle clearance distances
- **Flight Envelope**: V-n diagrams, performance boundaries

### 🎯 Design Optimization
- **Multi-Objective Optimization**: Range, fuel efficiency, L/D ratio
- **Constraint Handling**: Stall speed, takeoff distance, wing loading limits
- **Algorithm Support**: Differential evolution, gradient-based methods
- **Design Variable Control**: Wing geometry, mass parameters

### 📈 Advanced Visualization
- **Performance Plots**: Drag polars, L/D curves, climb performance
- **3D Envelopes**: Altitude-speed-performance relationships
- **Comparison Charts**: Multi-aircraft design analysis
- **Interactive Dashboards**: Plotly-based dynamic visualizations

### ✈️ 3D Aircraft Visualization
- **Realistic 3D Models**: See actual aircraft shapes and proportions
- **Interactive 3D Gallery**: Rotate, zoom, and explore aircraft in your browser
- **Design Comparison**: Side-by-side 3D views of different aircraft types
- **Custom Aircraft Designer**: Create and visualize your own aircraft designs
- **Parameter Impact**: Understand how design choices affect aircraft appearance

## Installation

1. Clone or download the repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Understanding Aircraft Parameters

First, explore the comprehensive parameter documentation:

```bash
# Activate the virtual environment
source activate.sh

# Explore aircraft parameters with detailed explanations
python scripts/explore_parameters.py
```

### Basic Aircraft Analysis

```python
from src import create_sample_aircraft, PerformanceAnalyzer

# Create sample aircraft designs
aircraft_list = create_sample_aircraft()
airliner = aircraft_list[0]  # Commercial airliner

# Analyze performance
analyzer = PerformanceAnalyzer(airliner)

# Find optimal angle of attack
optimal_aoa = analyzer.find_optimal_angle_of_attack()
max_ld = airliner.calculate_lift_drag_ratio(optimal_aoa)

print(f"Optimal AoA: {optimal_aoa:.1f}°")
print(f"Max L/D Ratio: {max_ld:.1f}")

# Calculate range and endurance
fuel_weight = airliner.mass.fuel_capacity
range_km = analyzer.calculate_range(10000, 200, fuel_weight)
endurance_hrs = analyzer.calculate_endurance(10000, fuel_weight)

print(f"Range: {range_km:.0f} km")
print(f"Endurance: {endurance_hrs:.1f} hours")
```

### Flight Conditions Testing

```python
from src import FlightConditions, AtmosphericConditions

# Create flight condition
altitude = 10000  # meters
atm = AtmosphericConditions.standard_atmosphere(altitude)
condition = FlightConditions(
    atmospheric=atm,
    airspeed=200,      # m/s
    angle_of_attack=5, # degrees
    bank_angle=0,      # degrees
    load_factor=1.0    # g's
)

print(f"Mach Number: {condition.mach_number:.3f}")
print(f"Dynamic Pressure: {condition.dynamic_pressure:.1f} Pa")
```

### Design Optimization

```python
from src import (DesignOptimizer, MaximizeRange, 
                StallSpeedConstraint, TakeoffDistanceConstraint)

# Set up optimizer
optimizer = DesignOptimizer()

# Add objectives
optimizer.add_objective(MaximizeRange(cruise_altitude=8000, weight=2.0))

# Add constraints
optimizer.add_constraint(StallSpeedConstraint(max_stall_speed=30))
optimizer.add_constraint(TakeoffDistanceConstraint(max_takeoff_distance=800))

# Set design variables
optimizer.set_design_variables({
    'wing_area': (12.0, 25.0),
    'aspect_ratio': (6.0, 12.0),
    'max_takeoff_weight': (1000, 1500)
})

# Run optimization
result = optimizer.optimize(base_aircraft)
```

### Visualization

```python
from src import AircraftVisualizer, compare_aircraft_designs

# Single aircraft analysis
visualizer = AircraftVisualizer(aircraft)
fig1 = visualizer.plot_drag_polar()
fig2 = visualizer.plot_v_n_diagram()
fig3 = visualizer.plot_performance_envelope()

# Compare multiple aircraft
aircraft_list = create_sample_aircraft()
fig_comp = compare_aircraft_designs(aircraft_list)
```

### 3D Aircraft Visualization

```python
from src import Aircraft3DVisualizer, create_aircraft_comparison_3d

# Create 3D visualizer for an aircraft
visualizer = Aircraft3DVisualizer(aircraft)

# Generate 3D matplotlib plot
fig_3d = visualizer.plot_3d_aircraft_matplotlib('my_aircraft_3d.png')

# Create interactive 3D model
interactive_fig = visualizer.create_interactive_3d_plotly()

# Compare multiple aircraft in 3D
comparison_fig = create_aircraft_comparison_3d(aircraft_list, 'comparison_3d.png')
```

## Example Scripts

Run the comprehensive examples to see all features in action:

```bash
# Activate virtual environment
source activate.sh

# Run comprehensive examples with performance analysis
python scripts/run_examples.py

# Create interactive web-based visualizations
python scripts/interactive_demo.py

# Explore parameter documentation and design insights
python scripts/explore_parameters.py

# Test system functionality
python scripts/test_system.py

# View aircraft in 3D (NEW!)
python scripts/view_aircraft_3d.py

# Design your own aircraft interactively (NEW!)
python scripts/design_your_aircraft.py
```

This will generate:
- Performance analysis for multiple aircraft types
- Flight condition testing scenarios
- Design optimization examples
- Comprehensive visualization plots
- Flight envelope analysis

## Aircraft Types Included

The system includes three pre-configured aircraft types:

1. **Commercial Airliner** (Boeing 737-like)
   - Wing span: 35.8 m
   - MTOW: 79,000 kg
   - Optimized for efficiency and range

2. **General Aviation** (Cessna 172-like)
   - Wing span: 11.0 m
   - MTOW: 1,157 kg
   - Good for training and personal transport

3. **Fighter Jet** (F-16-like)
   - Wing span: 9.96 m
   - MTOW: 19,200 kg
   - High performance and maneuverability

## Key Modules

### Core Library (`src/`)
- **`aircraft.py`**: Core aircraft classes with comprehensive parameter documentation
- **`flight_conditions.py`**: Atmospheric modeling and flight parameters
- **`performance_analysis.py`**: Range, endurance, and performance calculations
- **`design_optimizer.py`**: Multi-objective optimization framework
- **`visualization.py`**: Plotting and visualization tools with automatic path management
- **`aircraft_3d.py`**: 3D aircraft geometry generation and visualization

### Executable Scripts (`scripts/`)
- **`test_system.py`**: System validation and functionality testing
- **`run_examples.py`**: Comprehensive analysis examples and demonstrations
- **`interactive_demo.py`**: Web-based interactive visualizations
- **`explore_parameters.py`**: Interactive parameter documentation and insights
- **`view_aircraft_3d.py`**: 3D aircraft visualization and comparison
- **`design_your_aircraft.py`**: Interactive aircraft designer with 3D preview

### Generated Content (`visualizations/`)
- **Static plots**: PNG files with performance analysis charts
- **Interactive dashboards**: HTML files with web-based exploration tools

## Technical Approach

### Aerodynamic Modeling
- Simplified drag polar: CD = CD0 + k×CL²
- Lift curve slope based on aspect ratio
- Stall characteristics and maximum lift coefficients

### Performance Calculations
- Breguet range equation for fuel consumption
- Standard atmosphere (ISA) implementation
- V-n diagram generation for flight envelope analysis

### Optimization Framework
- Scipy-based optimization algorithms
- Constraint handling with penalty methods
- Multi-objective weighted sum approach

## 🚀 Quick Start: Streamlit Web App

**NEW: Interactive Web Interface!** Launch the comprehensive aircraft design studio:

```bash
# Activate virtual environment
source .venv/bin/activate

# Launch web application
python scripts/run_streamlit_app.py
```

**Features:**
- **🎛️ Interactive Controls**: Real-time parameter adjustment with sliders
- **✈️ Flight Feasibility Scoring**: Instant 0-100 assessment with color feedback
- **📊 Live Performance Analysis**: 4 interactive plot types (drag polar, L/D, envelope, V-n)
- **🛩️ 3D Visualization**: Realistic aircraft models with 1:1 scaling
- **⚖️ Design Comparison**: Save and compare multiple designs
- **🚨 Smart Alerts**: Critical issue detection with improvement suggestions

## Applications

This system is ideal for:
- **Educational Purposes**: Learning aircraft design principles with real-time feedback
- **Conceptual Design**: Early-stage aircraft development with feasibility assessment
- **Trade Studies**: Comparing design alternatives with systematic scoring
- **Performance Analysis**: Understanding flight characteristics with interactive tools
- **Research**: Investigating design parameter effects with comprehensive visualization

## Limitations

- Simplified aerodynamic models (suitable for conceptual design)
- No detailed structural or systems analysis
- Assumes steady-state flight conditions
- Limited to subsonic flight regimes

## Future Enhancements

Potential areas for expansion:
- Supersonic aerodynamics
- Detailed engine modeling
- Structural weight estimation
- Cost analysis integration
- Multi-disciplinary optimization

## Contributing

Feel free to extend the system with additional features:
- New aircraft configurations
- Advanced aerodynamic models
- Additional optimization objectives
- Enhanced visualization capabilities

## License

This project is provided as-is for educational and research purposes.
