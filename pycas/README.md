# CADAC Builder - Python API for Modular Simulations

## Overview

The CADAC Builder is a Python framework for constructing and running CADAC simulations from modular components. It provides a high-level API that enables:

- **Component-based simulation construction** - Build simulations by composing reusable modules
- **Automatic dependency resolution** - Ensures all required modules are present
- **Input file generation** - Automatically generates `input.asc` files
- **Compilation and execution** - Compiles and runs simulations programmatically
- **Regression testing** - Compare trajectories against ground truth

## Architecture

The framework consists of several key modules:

### Core Modules

- **ComponentRegistry** (`component_registry.py`) - Loads and manages component metadata from INDEX.md files
- **Component** (`component.py`) - Wrapper classes for component instances with factory methods
- **Simulation** (`simulation.py`) - Main simulation builder class
- **InputFileGenerator** (`input_generator.py`) - Generates input.asc files
- **Compiler** (`compiler.py`) - Compiles C++ simulations
- **Runner** (`runner.py`) - Executes compiled simulations
- **Trajectory** (`trajectory.py`) - Parses and analyzes trajectory output
- **TrajectoryComparator** (`trajectory.py`) - Compares trajectories for regression testing

### Component Metadata

Each component has an `INDEX.md` file that specifies:

- **Inputs** - Variables read from the vehicle array
- **Outputs** - Variables written to the vehicle array
- **Parameters** - User-configurable values from input.asc
- **Dependencies** - Required modules
- **Lifecycle** - Which methods are needed (def, init, exec)

## Quick Start

### Installation

```bash
# Install dependencies
pip install pyyaml numpy matplotlib

# The CADAC Builder is located in the cadac_builder/ directory
```

### Basic Example - BALL3 Ballistic Simulation

```python
from cadac_builder import Simulation, Component

# Create simulation
sim = Simulation("BALL3_test")

# Add components
sim.add_component(Component.time_management())
sim.add_component(Component.kinematics_3dof_flat())
sim.add_component(Component.forces_3dof())
sim.add_component(Component.drag_simple(cd=0.47, area=0.01))
sim.add_component(Component.gravity_constant(grav=9.81))
sim.add_component(Component.atmosphere_constant(rho=1.225))
sim.add_component(Component.termination(altitude_min=0.0, time_max=10.0))

# Set initial conditions
sim.set_initial_state(
    sbel1=0.0, sbel2=0.0, sbel3=0.0,      # Position (m)
    vbel1=35.36, vbel2=0.0, vbel3=-35.36  # Velocity (m/s) - 50 m/s at 45°
)

# Configure simulation
sim.set_config(duration=10.0, dt=0.01, output_step=0.05)

# Validate
errors = sim.validate()
if errors:
    print("Errors:", errors)
else:
    # Generate input file
    input_file = sim.generate_input_file()
    print(f"Generated: {input_file}")

    # Compile and run (when ready)
    # sim.compile()
    # results = sim.run()
    # comparison = sim.compare(results, "reference/traj.asc")
```

### Running the BALL3 Example

```bash
python3 test_ball3.py
```

This will:
1. Build a BALL3 simulation using the Python API
2. Validate the configuration
3. Generate an `input.asc` file
4. Display the generated configuration

## Component Factory Methods

The `Component` class provides factory methods for all 36 extracted components:

### Environment Components
- `Component.time_management()` - Required for all simulations
- `Component.termination(altitude_min, time_max)` - Stop conditions
- `Component.gravity_constant(grav=9.81)` - Constant gravity
- `Component.gravity_wgs84_simple()` - Altitude-varying gravity
- `Component.atmosphere_constant(rho=1.225)` - Constant atmosphere
- `Component.atmosphere_us76()` - US Standard Atmosphere 1976
- `Component.wind_none()` - No wind
- `Component.wind_constant(vx, vy, vz)` - Constant wind vector

### Kinematics Components
- `Component.kinematics_3dof_flat()` - 3DoF on flat Earth
- `Component.kinematics_6dof(psi, theta, phi)` - 6DoF with DCM integration

### Dynamics Components
- `Component.forces_3dof()` - 3DoF force summation
- `Component.newton_6dof()` - 6DoF translational dynamics
- `Component.euler_6dof()` - 6DoF rotational dynamics
- `Component.forces_6dof()` - 6DoF force and moment summation

### Aerodynamics Components
- `Component.drag_simple(cd, area)` - Simple drag-only
- `Component.aero_3dof_table()` - 3DoF from tables
- `Component.aerodynamics_6dof(maero, refa, refd)` - 6DoF from tables

### Propulsion Components
- `Component.thrust_constant(thrust)` - Constant thrust
- `Component.rocket_motor_simple(thrust, burntime, spi)` - Simple motor
- `Component.propulsion_staging(...)` - Multi-stage with variable mass/inertia

### Guidance Components
- `Component.guidance_none()` - No guidance (ballistic)
- `Component.guidance_proportional_nav(gnav, gmax)` - PNG for missiles
- `Component.guidance_pitch_program(time_table, pitch_table)` - Time-based pitch

### Control Components
- `Component.control_none()` - No control
- `Component.control_rate_damping(gain)` - Simple rate feedback
- `Component.control_accel_autopilot(waclp, zaclp, paclp)` - 3DoF autopilot
- `Component.control_accel_6dof(waclp, zaclp, paclp)` - 6DoF autopilot

### Actuator Components
- `Component.actuator_first_order(tau)` - First-order lag
- `Component.tvc_simple(wntvc, zettvc, tvclimx)` - Thrust vector control
- `Component.rcs_simple(rcs_zeta, rcs_freq)` - Reaction control system

### Sensor Components
- `Component.seeker_perfect()` - Perfect target seeker
- `Component.gps_perfect()` - Perfect GPS sensor

### Navigation Components
- `Component.target_fixed(x, y, z)` - Stationary target
- `Component.target_const_velocity(x, y, z, vx, vy, vz)` - Moving target
- `Component.intercept_simple()` - Miss distance calculation

## Generated Files

The framework generates several files:

```
sims/
└── BALL3_test/
    ├── input.asc           # Generated input file
    ├── build/              # Compilation directory
    │   ├── BALL3_test      # Compiled executable
    │   └── main.cpp        # Auto-generated main
    └── traj.asc            # Trajectory output (after running)
```

## Input File Format

The generated `input.asc` file follows the standard CADAC format:

```
TITLE simulation_name
MONTE 1

MODULES
    component_name   def,init,exec
    ...
END

TIMING
    int_step = 0.01
    event_time = 100.0
    com_step = 0.1
END

VEHICLE
    // Initial conditions
    variable = value
    ...

    // Component parameters
    param = value
    ...
END

ENDTIME 9999
STOP
```

## Component Metadata Structure

Each component's `INDEX.md` file contains:

```yaml
component:
  name: drag_simple
  category: Aerodynamics
  dof: 3DoF
  description: Simple point mass drag force

lifecycle:
  def: true
  init: false
  exec: true

inputs:
  - index: 0
    name: grav
    type: double
    unit: m/s^2
    description: Gravity acceleration
    source: environment

outputs:
  - index: 13
    name: dvbe
    type: double
    unit: m/s
    description: Speed
    scope: inter-module

parameters:
  - index: 10
    name: cd
    type: double
    unit: dimensionless
    description: Drag coefficient
    required: true

dependencies:
  required_before: [environment, kinematics]

usage_example: |
  # In input.asc:
  cd = 0.47
  area = 0.0314
```

## Available Simulations

Based on extracted components, the following simulations can be built:

### ✅ Fully Available
1. **BALL3** - Ballistic cannonball (3DoF, 7 modules)
2. **ROCKET6G** - Three-stage space launch vehicle (6DoF, 16 modules)

### 🟡 Partially Available
3. **AIM5** - Air-to-air missile (3DoF, needs waypoint guidance)
4. **CRUISE5** - Cruise missile (3DoF, needs waypoint guidance)

## Future Enhancements

- [ ] Automatic compilation and execution
- [ ] Enhanced dependency resolution
- [ ] Parameter validation against INDEX.md specs
- [ ] Trajectory plotting and visualization
- [ ] Monte Carlo simulation support
- [ ] Configuration file templates
- [ ] Component documentation generator
- [ ] Unit tests for all modules

## File Structure

```
cadac_builder/
├── __init__.py                 # Package initialization
├── component_registry.py       # Component metadata management
├── component.py                # Component wrapper classes
├── simulation.py               # Main simulation builder
├── input_generator.py          # Input file generation
├── compiler.py                 # C++ compilation
├── runner.py                   # Simulation execution
├── trajectory.py               # Trajectory analysis
└── README.md                   # This file

components/
├── aerodynamics/
│   ├── drag_simple.cpp
│   ├── aero_3dof_table.cpp
│   ├── aerodynamics_6dof.cpp
│   └── INDEX.md                # Component metadata
├── kinematics/
│   ├── kinematics_3dof_flat.cpp
│   ├── kinematics_6dof.cpp
│   └── INDEX.md
└── [... other categories ...]

tools/
└── generate_index_files.py     # Auto-generate INDEX.md from headers

test_ball3.py                   # BALL3 example script
```

## Component Extraction Status

**Total: 36 of ~55 components extracted (72% complete)**

| Category | Extracted | Total | Percentage |
|----------|-----------|-------|------------|
| Actuators | 2 | 4 | 50% |
| Aerodynamics | 3 | 6 | 50% |
| Control | 5 | 8 | 63% |
| Dynamics | 4 | 6 | 67% |
| Environment | 6 | 8 | 75% |
| Guidance | 3 | 8 | 38% |
| Kinematics | 2 | 4 | 50% |
| Navigation | 3 | 5 | 60% |
| Propulsion | 4 | 5 | 80% |
| Sensors | 2 | 4 | 50% |
| Utilities | 2 | 2 | 100% |

## Contributing

When adding new components:

1. Extract component to `components/{category}/{name}.cpp`
2. Add comprehensive header documentation
3. Run `tools/generate_index_files.py` to update INDEX.md
4. Add factory method to `Component` class
5. Test with Python API

## License

Part of the CADAC framework. See main repository for license information.
