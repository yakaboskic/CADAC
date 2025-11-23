# CADAC Aerospace Simulations

> **C**omputer **A**ided **D**esign of **A**erospace **C**oncepts
> Peter H. Zipfel's aerospace vehicle simulation framework

[![Build](https://img.shields.io/badge/build-makefile-blue)]()
[![C++](https://img.shields.io/badge/C++-11-00599C)]()
[![License](https://img.shields.io/badge/license-Academic-green)]()

## Overview

This repository contains the complete CADAC simulation framework from Peter Zipfel's book *"Modeling and Simulation of Aerospace Vehicle Dynamics"*. Originally distributed for Microsoft Visual Studio 2013, the code has been modernized with cross-platform Makefiles for Linux, macOS, and Windows (MinGW/Cygwin).

**Original Source**: [AIAA CADAC Multi-use Architecture for Constructive Aerospace Simulations](https://www.researchgate.net/publication/238043429_CADAC_Multi-use_Architecture_for_Constructive_Aerospace_Simulations)

## Quick Start

```bash
# Build all simulations
make

# Build and run a specific simulation
make MAGSIX
cd example/MAGSIX
./magsix

# View results
cat plot1.asc
```

## What's Included

| Simulation | Type | Description |
|------------|------|-------------|
| **MAGSIX** | 6DoF | Magnus rotor dynamics (simplest example) |
| **ROCKET6G** | 6DoF | Three-stage rocket with GPS/INS, orbital insertion |
| **FALCON6** | 6DoF | F-16 aircraft with flight control system |
| **AIM5** | 5DoF | Short-range air-to-air missile |
| **SRAAM6** | 6DoF | Advanced air-to-air missile, Monte Carlo capable |
| **AGM6** | 6DoF | Air-to-ground missile with IR seeker |
| **ADS6** | 6DoF | Air defense system, Monte Carlo capable |
| **CRUISE5** | 5DoF | Cruise missile with terminal sensor |
| **GHAME3** | 3DoF | NASA hypersonic vehicle |
| **GHAME6** | 6DoF | Advanced hypersonic vehicle, Monte Carlo capable |

## Features

✅ **Cross-Platform Build System** - Modern Makefiles replace Visual Studio projects
✅ **10 Complete Simulations** - Missiles, aircraft, rockets, hypersonic vehicles
✅ **6DoF & 5DoF Dynamics** - Full rigid body dynamics
✅ **Monte Carlo Capability** - Statistical analysis for several simulations
✅ **GPS/INS Sensors** - Realistic sensor modeling
✅ **Atmospheric Models** - US Standard Atmosphere 1976
✅ **WGS-84 Geodesy** - Earth modeling and coordinate transformations
✅ **Comprehensive Documentation** - Full build and user guide included

## Build Requirements

- **Compiler**: g++ with C++11 support (GCC 4.8.1+)
- **Build Tool**: GNU Make
- **OS**: Linux, macOS, or Windows (MinGW/Cygwin)

## Usage

### Build Commands

```bash
make              # Build all simulations
make <SIM>        # Build specific simulation (MAGSIX, ROCKET6G, etc.)
make clean        # Remove all build artifacts
make test         # Build and test MAGSIX
make help         # Show available targets
```

### Running Simulations

Each simulation reads configuration from `input.asc`:

```bash
cd example/ROCKET6G
./rocket6g                        # Run with default input.asc
./rocket6g < input_ballistic.asc  # Run with alternate input
```

### Input File Structure

```
TITLE Three-stage orbital insertion
OPTIONS y_scrn y_plot y_doc
MODULES
    environment   def,exec
    kinematics    def,exec
    newton        def,init,exec
    guidance      def,exec
END
TIMING
    scrn_step 2.0
    plot_step 0.1
    int_step 0.01
END
VEHICLES 1
    ROCKET6 SLV
        // Initial conditions
        lonx  -75.5    // Launch longitude - deg
        latx  28.5     // Launch latitude - deg
        alt   0        // Launch altitude - m
        // ... more parameters ...
    END
ENDTIME 600
STOP
```

### Output Files

| File | Content |
|------|---------|
| `plot1.asc` | Time history of selected variables |
| `traj.asc` | Trajectory data for all vehicles |
| `tabout.asc` | Tabular output |
| `doc.asc` | Auto-generated variable documentation |

## Visualization

### Python Example

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('plot1.asc', skiprows=2)
time = data[:, 0]
altitude = data[:, 7]

plt.plot(time, altitude)
plt.xlabel('Time (s)')
plt.ylabel('Altitude (m)')
plt.grid(True)
plt.savefig('trajectory.png')
```

### MATLAB/Octave Example

```matlab
data = load('plot1.asc', '-ascii');
data = data(3:end, :);
plot(data(:,1), data(:,8));
xlabel('Time (s)'); ylabel('Altitude (m)'); grid on;
```

## Framework Architecture

```
CADAC Architecture
├── Execution Framework
│   ├── Simulation executive (execution.cpp)
│   ├── Module management
│   └── Time integration
├── Vehicle Classes
│   ├── Cadac (base class)
│   └── Specific vehicles (Rocket, Missile, Aircraft, etc.)
├── Core Utilities
│   ├── Matrix class (linear algebra)
│   ├── Coordinate transformations
│   ├── Atmospheric models
│   └── Integration methods
└── Modules (vehicle-specific)
    ├── Environment (gravity, atmosphere, wind)
    ├── Kinematics (position, velocity)
    ├── Dynamics (forces, moments)
    ├── Aerodynamics (lift, drag)
    ├── Propulsion (thrust, fuel)
    ├── Guidance (navigation, targeting)
    ├── Control (autopilot, stability)
    └── Sensors (GPS, INS, seeker)
```

## Documentation

- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Complete build and usage documentation
- **example/*/readme.asc** - Simulation-specific instructions
- **example/*/documentation.asc** - Detailed module documentation
- **example/Installation.pdf** - Original installation guide

## What's New in This Version

### Modernization

- ✅ **Cross-platform Makefiles** for all 10 simulations
- ✅ **Fixed C++ compatibility issues** (added `#include <cstring>`, removed extra qualifications)
- ✅ **Root Makefile** to build all examples at once
- ✅ **Modern documentation** (BUILD_GUIDE.md with markdown formatting)
- ✅ **Automated build scripts** for consistency

### Original Code Preserved

All original functionality is preserved. Changes are limited to:
- Build system (Makefile instead of .vcxproj)
- Missing standard library includes
- C++ standard compliance fixes

## Example: Running MAGSIX

```bash
# Build
cd example/MAGSIX
make

# Run trajectory test
./magsix

# Output shows:
# - Steady-state conditions
# - Time-stepped trajectory data
# - Speed, altitude, spin rate progression
```

Sample output:
```
RECT.MR1
time    sim_time    vmach       pdynmc      dvbe        hbe         omega_rpm
0       0           0.0493409   153.164     16.6074     999.964     850.86
2       2           0.0379373   91.534      12.7767     910.531     2351.14
4       4           0.039566    100.157     13.3326     861.237     2316.15
...
```

## References

1. Zipfel, Peter H, *"Modeling and Simulation of Aerospace Vehicle Dynamics"*, AIAA Education Series, 3rd Ed. 2014
2. Zipfel, Peter H, *"Building Aerospace Simulations in C++"*, AIAA Self-Study Series, 3rd Ed. 2014
3. Zipfel, Peter H, *"Fundamentals of 6 DoF Aerospace Simulation and Analysis in C++"*, AIAA Self-Study Series, 2nd Ed. 2014
4. Zipfel, Peter H, *"Advanced 6 DoF Aerospace Simulation and Analysis in C++"*, AIAA Self-Study Series, 2nd Ed. 2014
5. Zipfel, Peter H, *"INS/GPS Star_Tracker in 6 DoF"*, Modeling and Simulation Technologies, Amazon 2015

## License

Academic software provided by Peter H. Zipfel. Free to use and modify without warranty.

## Contact

**Original Author**: Peter H. Zipfel, Ph.D.
**Modeling and Simulation Technologies (MaSTech)**
mastech.zipfel@cox.net

---

**Note**: This is educational/research software. For production aerospace applications, use certified flight dynamics software with appropriate validation and verification.
