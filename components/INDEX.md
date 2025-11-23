# CADAC Component Library - Quick Index

## Extracted Components (Ready to Use)

### Environment Components
- ✅ [gravity_constant.cpp](environment/gravity_constant.cpp) - Simple g=9.81 m/s² gravity
- ✅ [atmosphere_constant.cpp](environment/atmosphere_constant.cpp) - Fixed ρ=1.225 kg/m³ density

### Kinematics Components
- ✅ [kinematics_3dof_flat.cpp](kinematics/kinematics_3dof_flat.cpp) - Point mass on flat Earth

### Aerodynamics Components
- ✅ [drag_simple.cpp](aerodynamics/drag_simple.cpp) - Point mass drag force

### Propulsion Components
- ✅ [thrust_constant.cpp](propulsion/thrust_constant.cpp) - Fixed thrust magnitude

### Guidance Components
- ✅ [guidance_none.cpp](guidance/guidance_none.cpp) - No guidance (ballistic)
- ✅ [guidance_proportional_nav.cpp](guidance/guidance_proportional_nav.cpp) - Proportional Navigation Guidance

### Control Components
- ✅ [control_none.cpp](control/control_none.cpp) - No control (ballistic)

## Quick Start Examples

### Example 1: Ballistic Projectile (Like BALL3)
```cpp
// Required components:
components/environment/gravity_constant.cpp
components/environment/atmosphere_constant.cpp
components/kinematics/kinematics_3dof_flat.cpp
components/aerodynamics/drag_simple.cpp
components/guidance/guidance_none.cpp
components/control/control_none.cpp
```

### Example 2: Guided Missile (Simple)
```cpp
// Required components:
components/environment/gravity_constant.cpp
components/environment/atmosphere_constant.cpp
components/kinematics/kinematics_3dof_flat.cpp
components/aerodynamics/drag_simple.cpp
components/propulsion/thrust_constant.cpp
components/guidance/guidance_proportional_nav.cpp
components/control/control_none.cpp  // or control_pid when available
```

## Variable Index Quick Reference

| Range | Purpose | Example Variables |
|-------|---------|-------------------|
| 0-9 | Environment | gravity, atmosphere |
| 10-19 | Forces/Aero | drag, lift, area, cd |
| 20-29 | Kinematics | position, velocity, altitude |
| 30-39 | Dynamics | accelerations |
| 40-49 | Attitude | Euler angles, quaternions |
| 50-79 | Aerodynamics | coefficients, angles |
| 80-99 | Propulsion | thrust, fuel, mass |
| 100-129 | Guidance | waypoints, commands |
| 130-149 | Control | autopilot states |
| 150-179 | Sensors | GPS, INS |
| 180-199 | Navigation | filtered state |
| 200-229 | Target/Intercept | geometry |
| 230+ | Vehicle-specific | custom |

## Usage Pattern

1. **Choose components** based on physics needed
2. **Copy .cpp files** to your simulation directory
3. **Merge into class files** (put functions in your vehicle class)
4. **Update input.asc** to configure MODULES and DATA sections
5. **Compile and run**

## See Also

- [CATALOG.md](CATALOG.md) - Complete list of all components (extracted + planned)
- [README.md](README.md) - Philosophy and detailed usage guide
- [../BUILD_GUIDE.md](../BUILD_GUIDE.md) - How to compile CADAC simulations
- [../CREATING_SIMULATIONS.md](../CREATING_SIMULATIONS.md) - How to create custom sims

## Status

**8 of 50+ components extracted** (as of 2025-11-23)

Priority for next extractions:
1. newton_3dof - Point mass dynamics
2. kinematics_6dof - Full rigid body kinematics
3. atmosphere_us76 - Realistic atmosphere
4. aero_3dof_table - Table-based aerodynamics
5. control_pid - PID autopilot
