# CADAC Component Catalog

## Quick Reference Guide

This catalog lists all extracted components from the CADAC examples, organized by function.

## Symbol Key

- ✅ **Extracted** - Component is in library, ready to use
- 📝 **Documented** - Source identified, extraction pending
- 🔄 **Complex** - Needs multiple files or dependencies
- 🎯 **Recommended** - Good starting point for new users

## Environment Components

### Gravity Models

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `gravity_constant` | ✅ | BALL3 | 3/6 | 🎯 Simple g=9.81 m/s² downward |
| `gravity_wgs84` | 📝 | ROCKET6G | 6 | Full WGS84 ellipsoidal with J2 |
| `gravity_geocentric` | 📝 | GHAME6 | 6 | Geocentric gravity model |

**Variable Assignments:**
```cpp
// gravity_constant
vehicle[0] = grav (double) - Gravity magnitude m/s²

// gravity_wgs84
vehicle[62] = GRAVG (Matrix 3x1) - Gravity vector in geocentric coords m/s²
vehicle[63] = grav (double) - Gravity magnitude m/s²
```

### Atmosphere Models

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `atmosphere_constant` | ✅ | BALL3 | 3/6 | 🎯 Fixed ρ=1.225 kg/m³ at sea level |
| `atmosphere_us76` | 📝 | ROCKET6G | 3/6 | US Standard Atmosphere 1976 |
| `atmosphere_us76_extended` | 📝 | GHAME6 | 3/6 | US76 extended to 1000km (NASA) |
| `atmosphere_table` | 📝 | ROCKET6G | 3/6 | Tabular from weather deck |

**Variable Assignments:**
```cpp
// atmosphere_us76
vehicle[52] = press (double) - Pressure Pa
vehicle[53] = rho (double) - Density kg/m³
vehicle[54] = vsound (double) - Speed of sound m/s
vehicle[58] = tempk (double) - Temperature K
```

### Wind Models

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `wind_none` | 📝 | BALL3 | 3/6 | 🎯 No wind |
| `wind_constant` | 📝 | ROCKET6G | 3/6 | Constant wind vector |
| `wind_table` | 📝 | ROCKET6G | 3/6 | Tabular from weather deck |
| `wind_turbulence` | 📝 | ROCKET6G | 6 | Dryden turbulence model |

## Kinematics Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `kinematics_3dof_flat` | ✅ | BALL3 | 3 | 🎯 Point mass, flat Earth |
| `kinematics_3dof_rotating` | 📝 | MAGSIX | 3 | Point mass, rotating Earth |
| `kinematics_6dof_inertial` | 📝 | ROCKET6G | 6 | Position + attitude, ECI frame |
| `kinematics_6dof_geodetic` | 📝 | FALCON6 | 6 | Position + attitude, lat/lon/alt |

**Variable Assignments:**
```cpp
// kinematics_3dof_flat (BALL3 pattern)
vehicle[20] = SBEL (Matrix 3x1) - Position in Earth frame m
vehicle[21] = VBEL (Matrix 3x1) - Velocity in Earth frame m/s
vehicle[22] = altitude (double) - Altitude above ground m
```

## Dynamics Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `newton_3dof` | 📝 | BALL3 | 3 | 🎯 Point mass dynamics F=ma |
| `newton_6dof` | 📝 | ROCKET6G | 6 | Translational dynamics |
| `euler_6dof` | 📝 | ROCKET6G | 6 | Rotational dynamics M=Iα |

## Aerodynamics Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `drag_simple` | ✅ | BALL3 | 3 | 🎯 Point mass drag only |
| `aero_3dof_table` | 📝 | AIM5 | 3 | Lift+drag from tables |
| `aero_6dof_table` | 📝 | FALCON6 | 6 | Full forces + moments from tables |
| `aero_hypersonic` | 📝 | GHAME6 | 6 | High-speed aerodynamics |

**Variable Assignments:**
```cpp
// drag_simple (BALL3 pattern)
vehicle[10] = cd (double) - Drag coefficient ND
vehicle[11] = area (double) - Reference area m²
vehicle[12] = rho (double) - Air density kg/m³
vehicle[13] = dvbe (double) - Speed m/s
vehicle[14] = FSPB (Matrix 3x1) - Specific force m/s²
```

## Propulsion Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `thrust_none` | 📝 | BALL3 | 3/6 | 🎯 No propulsion (ballistic) |
| `thrust_constant` | ✅ | AIM5 | 3/6 | Fixed thrust magnitude |
| `thrust_table` | 📝 | ROCKET6G | 3/6 | Thrust vs time from table |
| `rocket_motor_solid` | 📝 | ROCKET6G | 3/6 | Solid rocket motor with staging |
| `jet_engine` | 📝 | FALCON6 | 6 | Jet thrust vs alt/Mach |

## Guidance Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `guidance_none` | ✅ | BALL3 | 3/6 | 🎯 Ballistic (no guidance) |
| `guidance_png` | ✅ | AIM5 | 3/6 | Proportional Navigation Guidance |
| `guidance_apn` | 📝 | SRAAM6 | 6 | Augmented PNG |
| `guidance_tpn` | 📝 | AGM6 | 6 | True PNG |
| `guidance_orbital` | 📝 | ROCKET6G | 6 | Orbital insertion guidance |
| `guidance_loft` | 📝 | CRUISE5 | 3 | Lofted trajectory |

## Control Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `control_none` | ✅ | BALL3 | 3/6 | 🎯 No control (ballistic) |
| `control_pid_roll` | 📝 | AIM5 | 3 | Roll PID autopilot |
| `control_pid_pitch_yaw` | 📝 | FALCON6 | 6 | 3-axis PID autopilot |
| `control_lqr` | 📝 | GHAME6 | 6 | Linear Quadratic Regulator |

## Sensor Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `gps_ideal` | 📝 | ROCKET6G | 3/6 | Perfect position measurement |
| `gps_errors` | 📝 | GHAME6 | 3/6 | GPS with realistic errors |
| `ins_ideal` | 📝 | ROCKET6G | 6 | Perfect inertial navigation |
| `ins_errors` | 📝 | GHAME6 | 6 | INS with gyro/accel drift |
| `seeker_ir` | 📝 | AGM6 | 6 | IR seeker model |
| `seeker_rf` | 📝 | SRAAM6 | 6 | RF seeker model |
| `star_tracker` | 📝 | ROCKET6G | 6 | Star tracker for attitude |

## Actuator Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `actuator_ideal` | 📝 | AIM5 | 3/6 | 🎯 Instant response |
| `actuator_lag` | 📝 | FALCON6 | 6 | First-order lag |
| `actuator_ratelimit` | 📝 | SRAAM6 | 6 | Rate and position limits |
| `tvc_dynamics` | 📝 | ROCKET6G | 6 | Thrust vector control |
| `rcs_jets` | 📝 | ROCKET6G | 6 | Reaction control system |

## Navigation Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `nav_ideal` | 📝 | BALL3 | 3/6 | 🎯 Perfect state knowledge |
| `nav_gps_only` | 📝 | CRUISE5 | 3 | GPS position only |
| `nav_gps_ins` | 📝 | ROCKET6G | 6 | GPS/INS Kalman filter |

## Intercept/Targeting Components

| Component | Status | Source | DoF | Description |
|-----------|--------|--------|-----|-------------|
| `intercept_geometry` | 📝 | AIM5 | 3 | Line-of-sight calculations |
| `intercept_kinematics` | 📝 | SRAAM6 | 6 | Closing velocity, time-to-go |

## How to Extract Components

### Step 1: Identify Source Example

Find which example has the module you want:
```bash
grep -l "guidance_proportional" example/*/guidance.cpp
# Result: example/AIM5/aim_modules.cpp
```

### Step 2: Examine Variable Indices

Look at the `def_xxx()` function to see what variables it uses:
```cpp
void Aim::def_guidance()
{
    aim[100].init("wp_lonx", ...);   // Uses indices 100-150
    aim[101].init("wp_latx", ...);
    // ...
}
```

### Step 3: Check Dependencies

See what it reads from other modules:
```cpp
void Aim::guidance(double int_step)
{
    // Reads from kinematics
    Matrix SBEL = aim[20].vec();     // Position
    Matrix VBEL = aim[21].vec();     // Velocity

    // Reads from target
    Matrix STEL = aim[200].vec();    // Target position

    // Outputs for control
    double acmd = ...;
    aim[110].gets(acmd);             // Commanded acceleration
}
```

### Step 4: Extract and Document

Create standalone file with:
1. Header comment (inputs, outputs, parameters)
2. `def_xxx()` function
3. `init_xxx()` function (if needed)
4. `xxx()` execution function
5. Update variable names to generic `vehicle[]`

### Step 5: Test in Isolation

Build a simple test simulation with just that component.

## Component Design Patterns

### Pattern 1: Pure Calculation (No State)

Example: `drag_simple`, `gravity_constant`

```cpp
void Vehicle::module_name(double int_step)
{
    // Read inputs
    double input1 = vehicle[X].real();

    // Calculate
    double output = f(input1);

    // Write outputs
    vehicle[Y].gets(output);
}
```

### Pattern 2: With Initialization

Example: `guidance_png`, `control_pid`

```cpp
void Vehicle::init_module_name()
{
    // Set initial values
    vehicle[X].gets(initial_value);
}

void Vehicle::module_name(double int_step)
{
    // Use initialized values
    // Update state
}
```

### Pattern 3: With State Variables

Example: `ins_errors`, `actuator_lag`

```cpp
void Vehicle::module_name(double int_step)
{
    // Read state
    double state = vehicle[STATE_INDEX].real();

    // Integrate
    double state_dot = ...;
    state = state + state_dot * int_step;

    // Write back
    vehicle[STATE_INDEX].gets(state);
}
```

## Variable Index Allocation Guide

To avoid conflicts, use these index ranges:

| Range | Purpose | Example |
|-------|---------|---------|
| 0-9 | Environment | gravity, atmosphere |
| 10-19 | Forces | drag, lift, thrust |
| 20-29 | Kinematics | position, velocity |
| 30-39 | Dynamics | accelerations |
| 40-49 | Attitude | Euler angles, quaternions |
| 50-79 | Aerodynamics | coefficients, angles |
| 80-99 | Propulsion | thrust, fuel |
| 100-129 | Guidance | waypoints, commands |
| 130-149 | Control | autopilot states |
| 150-179 | Sensors | GPS, INS |
| 180-199 | Navigation | filtered state |
| 200-229 | Target/Intercept | geometry |
| 230+ | Vehicle-specific | custom |

## Next Steps

1. **Extract remaining components** from examples
2. **Test each component** in isolation
3. **Create assembly guide** showing common combinations
4. **Build Python constructor** for automatic code generation
5. **Add component templates** for creating new components

## Contributing

To add a component:

1. Extract from example
2. Document header (inputs, outputs, params)
3. Use standard variable indices
4. Test standalone
5. Submit PR with component + test

## Status Summary

- ✅ **8** components fully extracted
- 📝 **45+** components identified and documented
- 🎯 **10** recommended starter components marked

Priority for next extraction:
1. Kinematics (3DoF and 6DoF)
2. Newton dynamics (3DoF and 6DoF)
3. Simple aerodynamics
4. Proportional navigation
5. PID control
