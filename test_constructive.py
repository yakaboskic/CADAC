#!/usr/bin/env python3
"""
Test pyCAS Constructive Framework

This demonstrates building a simulation from scratch using components,
compiling, and running - NO REUSING EXAMPLES!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pycas import Simulation, Component

def main():
    print("="*70)
    print("pyCAS - Constructive Aerospace Simulator")
    print("Building simulation from modular components")
    print("="*70)

    # Build a custom ballistic simulation from components
    sim = Simulation("MyProjectile")
    # Note: time_management and termination not included - Ball class doesn't support those modules
    # The framework handles time management and simulation termination automatically
    sim.add_component(Component.kinematics_3dof_flat())
    sim.add_component(Component.forces_3dof())
    sim.add_component(Component.drag_simple(cd=0.47, area=0.01))
    sim.add_component(Component.gravity_constant())
    sim.add_component(Component.atmosphere_constant())

    # Set initial conditions
    sim.set_initial_state(
        sbel1=0, sbel2=0, sbel3=0,          # Position (m)
        vbel1=35.36, vbel2=0, vbel3=-35.36  # Velocity (m/s) - 45° launch
    )

    print("\n" + "="*70)
    print("Step 1: Generate input file")
    print("="*70)
    input_file = sim.generate_input_file()
    print(f"✓ Generated: {input_file}")

    print("\n" + "="*70)
    print("Step 2: Compile from components")
    print("="*70)
    sim.compile()
    print(f"✓ Executable: {sim.executable_path}")

    print("\n" + "="*70)
    print("Step 3: Run simulation")
    print("="*70)
    trajectory = sim.run(duration=10.0, dt=0.01)

    print("\n" + "="*70)
    print("Step 4: Parse results")
    print("="*70)
    print(f"✓ Loaded trajectory with {len(trajectory.time)} points")
    print(f"✓ Variables: {', '.join(trajectory.variables)}")

    # Try to convert to DataFrame
    try:
        df = trajectory.to_dataframe()
        print(f"\n✓ Converted to Pandas DataFrame:")
        print(df.head())
        print(f"\nDataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
    except ImportError as e:
        print(f"\n⚠ Pandas not installed: {e}")
        print("Install with: pip install pandas")

    print("\n" + "="*70)
    print("✅ SUCCESS - Constructive simulation complete!")
    print("="*70)
    print("\nThis simulation was built entirely from modular components.")
    print("No examples were reused. All code was generated and compiled")
    print("from the pyCAS component library.")
    print("="*70)

    return 0

if __name__ == '__main__':
    sys.exit(main())
