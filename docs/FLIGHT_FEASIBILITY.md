# Flight Feasibility Guide

## 📋 Overview

This guide explains how to determine if an aircraft design will fly, covering the fundamental physics, key equations, and practical assessment criteria used in the Aircraft Design Studio.

## 🧮 Fundamental Flight Equations

### 1. Basic Flight Condition
For an aircraft to fly, **lift must equal or exceed weight**:

```
L ≥ W
```

Where:
- `L` = Lift force (N)
- `W` = Aircraft weight (N)

### 2. Lift Generation Equation
```
L = ½ × ρ × V² × CL × S
```

Where:
- `ρ` = Air density (kg/m³)
- `V` = Airspeed (m/s)
- `CL` = Lift coefficient (dimensionless)
- `S` = Wing reference area (m²)

### 3. Stall Speed Calculation
The minimum flying speed (stall speed) occurs at maximum lift coefficient:

```
V_stall = √(2 × W / (ρ × CL_max × S))
```

Where:
- `CL_max` = Maximum lift coefficient before stall

### 4. Drag Force Equation
```
D = ½ × ρ × V² × CD × S
```

Where:
- `CD` = Drag coefficient (dimensionless)

### 5. Drag Polar Relationship
```
CD = CD0 + k × CL²
```

Where:
- `CD0` = Zero-lift drag coefficient (parasitic drag)
- `k` = Induced drag factor = 1/(π × AR × e)
- `AR` = Aspect ratio
- `e` = Oswald efficiency factor (≈ 0.8)

### 6. Lift-to-Drag Ratio
```
L/D = CL/CD
```

Maximum L/D occurs when:
```
CL_optimal = √(CD0/k)
L/D_max = 1/(2√(CD0 × k))
```

### 7. Wing Loading
```
WL = W/S
```

Where:
- `WL` = Wing loading (N/m² or Pa)

### 8. Aspect Ratio
```
AR = b²/S = b/c_avg
```

Where:
- `b` = Wing span (m)
- `c_avg` = Average wing chord (m)

### 9. Takeoff Distance (Simplified)
```
s_TO ≈ 1.44 × W² / (ρ × g × CL_max × S × T)
```

Where:
- `s_TO` = Takeoff distance (m)
- `g` = Gravitational acceleration (9.81 m/s²)
- `T` = Available thrust (N)

### 10. Rate of Climb
```
RC = (T - D) × V / W
```

Where:
- `RC` = Rate of climb (m/s)
- `T` = Thrust available (N)

## 🎯 Flight Feasibility Criteria

### 📊 Performance Thresholds

#### Stall Speed Assessment
| Category | Stall Speed (km/h) | Feasibility | Description |
|----------|-------------------|-------------|-------------|
| 🟢 Excellent | < 100 | ✅ Highly Flyable | Easy handling, short runways |
| 🟢 Good | 100-150 | ✅ Flyable | Good general aviation performance |
| 🟡 Acceptable | 150-200 | ⚠️ Flyable | Requires pilot skill, standard runways |
| 🟡 Marginal | 200-250 | ⚠️ Challenging | High performance required |
| 🔴 Problematic | 250-300 | ❌ Difficult | Very challenging to operate |
| 🔴 Critical | > 300 | ❌ Unfeasible | Likely unsafe for normal operations |

#### Lift-to-Drag Ratio Assessment
| Category | L/D Ratio | Feasibility | Description |
|----------|-----------|-------------|-------------|
| 🟢 Excellent | > 15 | ✅ Highly Efficient | Sailplane/high-efficiency category |
| 🟢 Good | 12-15 | ✅ Efficient | Good transport aircraft performance |
| 🟡 Acceptable | 8-12 | ⚠️ Adequate | Typical general aviation |
| 🟡 Marginal | 6-8 | ⚠️ Poor Efficiency | High fuel consumption |
| 🔴 Problematic | 4-6 | ❌ Very Poor | Barely sustainable flight |
| 🔴 Critical | < 4 | ❌ Unfeasible | Flight likely impossible |

#### Takeoff Distance Assessment
| Category | Distance (m) | Feasibility | Runway Requirements |
|----------|-------------|-------------|-------------------|
| 🟢 Excellent | < 300 | ✅ STOL Capable | Grass strips, small airports |
| 🟢 Good | 300-800 | ✅ Versatile | Most general aviation airports |
| 🟡 Acceptable | 800-1500 | ⚠️ Standard | Standard commercial airports |
| 🟡 Marginal | 1500-2500 | ⚠️ Long Runway | Major airports only |
| 🔴 Problematic | 2500-4000 | ❌ Very Long | Specialized facilities |
| 🔴 Critical | > 4000 | ❌ Extreme | Military/specialized only |

#### Wing Loading Assessment
| Category | Wing Loading (N/m²) | Feasibility | Characteristics |
|----------|-------------------|-------------|-----------------|
| 🟢 Low | < 1000 | ✅ Gentle Flying | Easy handling, short runways |
| 🟢 Light | 1000-2000 | ✅ Good Handling | Typical GA aircraft |
| 🟡 Moderate | 2000-4000 | ⚠️ Standard | Transport aircraft range |
| 🟡 High | 4000-6000 | ⚠️ Fast/Challenging | High speed, skilled pilots |
| 🔴 Very High | 6000-8000 | ❌ Specialized | Fighter/high-performance |
| 🔴 Extreme | > 8000 | ❌ Critical | Experimental/military only |

#### Service Ceiling Assessment
| Category | Ceiling (km) | Feasibility | Operational Capability |
|----------|-------------|-------------|----------------------|
| 🟢 High Altitude | > 12 | ✅ Excellent | Commercial airliner capability |
| 🟢 Good | 8-12 | ✅ Good | Most operational needs |
| 🟡 Adequate | 5-8 | ⚠️ Adequate | General aviation standard |
| 🟡 Limited | 3-5 | ⚠️ Limited | Low altitude operations |
| 🔴 Poor | 1-3 | ❌ Very Limited | Severely restricted |
| 🔴 Critical | < 1 | ❌ Unfeasible | Barely above ground level |

## 🔍 Design Assessment Matrix

### Quick Flight Feasibility Check

Use this matrix to rapidly assess if a design will fly:

| Metric | Weight | Excellent | Good | Acceptable | Marginal | Poor | Critical |
|--------|--------|-----------|------|------------|----------|------|----------|
| Stall Speed | 30% | < 100 km/h | 100-150 | 150-200 | 200-250 | 250-300 | > 300 |
| L/D Ratio | 25% | > 15 | 12-15 | 8-12 | 6-8 | 4-6 | < 4 |
| Takeoff Dist | 20% | < 300m | 300-800 | 800-1500 | 1500-2500 | 2500-4000 | > 4000 |
| Wing Loading | 15% | < 1000 | 1000-2000 | 2000-4000 | 4000-6000 | 6000-8000 | > 8000 |
| Service Ceil | 10% | > 12km | 8-12 | 5-8 | 3-5 | 1-3 | < 1 |

### Overall Feasibility Score

**Calculation:**
```
Score = Σ(Metric_Score × Weight)
```

**Interpretation:**
- **90-100**: 🟢 Excellent - Highly flyable design
- **70-89**: 🟢 Good - Flyable with good characteristics  
- **50-69**: 🟡 Acceptable - Flyable but with limitations
- **30-49**: 🟡 Marginal - Challenging but possible
- **10-29**: 🔴 Poor - Significant problems
- **0-9**: 🔴 Critical - Unlikely to fly safely

## ⚠️ Critical Design Red Flags

### Immediate Concerns
1. **Stall Speed > 300 km/h**: Extremely dangerous for most applications
2. **L/D < 4**: Flight may be unsustainable
3. **Takeoff Distance > 4km**: Requires specialized facilities
4. **Wing Loading > 8000 N/m²**: Requires extreme performance
5. **Negative Service Ceiling**: Fundamental design error

### Physics Violations
1. **Aspect Ratio < 1**: Aerodynamically questionable
2. **Wing Area = 0**: No lift generation possible
3. **Empty Weight > MTOW**: Mass budget error
4. **Fuel Fraction > 90%**: Impractical fuel requirements

## 🛠️ Design Improvement Strategies

### To Improve Stall Speed:
1. **Increase Wing Area** (S ↑)
2. **Increase CL_max** (better airfoils, flaps)
3. **Reduce Weight** (W ↓)

### To Improve L/D Ratio:
1. **Increase Aspect Ratio** (reduce induced drag)
2. **Reduce CD0** (cleaner design)
3. **Optimize wing loading**

### To Reduce Takeoff Distance:
1. **Increase Wing Area**
2. **Add high-lift devices** (flaps, slats)
3. **Increase Thrust-to-Weight ratio**
4. **Reduce Wing Loading**

### To Increase Service Ceiling:
1. **Reduce Wing Loading**
2. **Increase Engine Power**
3. **Improve L/D Ratio**
4. **Optimize for high-altitude conditions**

## 📚 References

1. Anderson, J.D. "Introduction to Flight" - Fundamental aerodynamics
2. Raymer, D.P. "Aircraft Design: A Conceptual Approach" - Design methodology  
3. Roskam, J. "Airplane Design" - Detailed design procedures
4. McCormick, B.W. "Aerodynamics, Aeronautics and Flight Mechanics" - Flight mechanics
5. Nicolai, L.M. "Fundamentals of Aircraft Design" - Design principles

## 🎯 Using This Guide

1. **Calculate key metrics** using the equations provided
2. **Compare against thresholds** in the assessment tables
3. **Identify problem areas** using the red flags checklist
4. **Apply improvement strategies** to optimize design
5. **Iterate and reassess** until acceptable performance achieved

This systematic approach ensures your aircraft design meets fundamental flight requirements before detailed analysis and construction.