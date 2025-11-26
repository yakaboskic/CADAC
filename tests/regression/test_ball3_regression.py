#!/usr/bin/env python3
"""
BALL3 Regression Test

Tests that the CADAC Builder Python API can correctly build, compile,
run, and validate the BALL3 ballistic simulation against a reference trajectory.
"""

import sys
import shutil
import subprocess
from pathlib import Path
import numpy as np

# Add cadac_builder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cadac_builder import Simulation, Component
from cadac_builder.trajectory import Trajectory, TrajectoryComparator


class BALL3Test:
    """Regression test for BALL3 ballistic simulation"""

    def __init__(self, test_dir: Path):
        self.test_dir = Path(test_dir)
        self.cadac_root = Path(__file__).parent.parent.parent
        self.reference_dir = self.cadac_root / 'tests/regression/reference'
        self.example_dir = self.cadac_root / 'example/BALL3'
        self.reference_traj = self.reference_dir / 'ball3_reference.asc'

        # Create test directory
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def build_simulation(self) -> Simulation:
        """Build BALL3 using Python API"""
        print("\n" + "="*60)
        print("STEP 1: Building BALL3 with Python API")
        print("="*60)

        sim = Simulation("BALL3", working_dir=self.test_dir)

        # Add components in correct order
        sim.add_component(Component.time_management())
        sim.add_component(Component.kinematics_3dof_flat())
        sim.add_component(Component.forces_3dof())
        sim.add_component(Component.drag_simple(cd=0.47, area=0.01))
        sim.add_component(Component.gravity_constant(grav=9.81))
        sim.add_component(Component.atmosphere_constant(rho=1.225))
        sim.add_component(Component.termination())

        # Set initial conditions matching reference
        sim.set_initial_state(
            sbel1=0.0,      # X position (East)
            sbel2=0.0,      # Y position (North)
            sbel3=0.0,      # Z position (Down)
            vbel1=35.36,    # X velocity (East)
            vbel2=0.0,      # Y velocity (North)
            vbel3=-35.36,   # Z velocity (Down, negative = up)
        )

        # Configure simulation
        sim.set_config(
            duration=10.0,
            dt=0.01,
            output_step=0.05
        )

        # Validate
        errors = sim.validate()
        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"  - {error}")
            return None

        print("✓ Configuration valid")
        print(f"✓ Components: {len(sim.components)}")

        return sim

    def setup_build_environment(self):
        """Copy necessary framework files for compilation"""
        print("\n" + "="*60)
        print("STEP 2: Setting up build environment")
        print("="*60)

        # Copy framework files from example
        framework_files = [
            'class_hierarchy.hpp',
            'global_header.hpp',
            'global_constants.hpp',
            'utility_header.hpp',
            'utility_functions.cpp',
            'global_functions.cpp',
            'class_functions.cpp',
            'execution.cpp'
        ]

        for file in framework_files:
            src = self.example_dir / file
            dst = self.test_dir / file
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✓ Copied {file}")
            else:
                print(f"  ⚠ Warning: {file} not found in example")

    def create_ball_functions(self):
        """Create minimal ball_functions.cpp for component-based BALL3"""
        print("\n" + "="*60)
        print("STEP 3: Creating ball_functions.cpp")
        print("="*60)

        # The CADAC framework expects ball_functions.cpp with module implementations
        # For component-based approach, we create a minimal version that uses our components
        ball_content = """//==============================================================================
// BALL3 - Ballistic Cannonball
// Built from modular components via CADAC Builder Python API
//==============================================================================

#include "class_hierarchy.hpp"

///////////////////////////////////////////////////////////////////////////////
// Ball class implementation using modular components
///////////////////////////////////////////////////////////////////////////////

// Note: Module implementations come from component files:
// - kinematics_3dof_flat.cpp provides def_kinematics(), init_kinematics(), kinematics()
// - forces_3dof.cpp provides def_forces(), forces()
// - drag_simple.cpp provides aerodynamics calculations in forces module
// - gravity_constant.cpp provides environment calculations
// - atmosphere_constant.cpp provides atmosphere calculations
// - time_management.cpp provides time management
// - termination.cpp provides termination conditions

// The framework in execution.cpp handles the simulation loop and module calling
"""

        ball_file = self.test_dir / 'ball_functions.cpp'
        ball_file.write_text(ball_content)
        print(f"✓ Created ball_functions.cpp")

    def compile_simulation(self) -> bool:
        """Compile the simulation"""
        print("\n" + "="*60)
        print("STEP 4: Compiling simulation")
        print("="*60)

        # Copy component files
        component_dir = self.cadac_root / 'components'

        # Map components to their files
        components_needed = [
            'kinematics/kinematics_3dof_flat.cpp',
            'dynamics/forces_3dof.cpp',
            'aerodynamics/drag_simple.cpp',
            'environment/gravity_constant.cpp',
            'environment/atmosphere_constant.cpp',
            'utilities/time_management.cpp',
            'utilities/termination.cpp',
        ]

        print("Copying component files...")
        for comp_path in components_needed:
            src = component_dir / comp_path
            if src.exists():
                dst = self.test_dir / src.name
                shutil.copy2(src, dst)
                print(f"  ✓ {src.name}")
            else:
                print(f"  ✗ Missing: {comp_path}")
                return False

        # Compile
        print("\nCompiling...")
        compile_cmd = [
            'g++',
            '-std=c++11',
            '-O2',
            '-Wno-write-strings',  # Suppress string literal warnings
            'ball_functions.cpp',
            'class_functions.cpp',
            'execution.cpp',
            'global_functions.cpp',
            'utility_functions.cpp',
            'kinematics_3dof_flat.cpp',
            'forces_3dof.cpp',
            'drag_simple.cpp',
            'gravity_constant.cpp',
            'atmosphere_constant.cpp',
            'time_management.cpp',
            'termination.cpp',
            '-o', 'ball3',
            '-I', str(self.test_dir)
        ]

        try:
            result = subprocess.run(
                compile_cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"❌ Compilation failed:")
                print(result.stderr)
                return False

            print("✓ Compilation successful")
            return True

        except Exception as e:
            print(f"❌ Compilation error: {e}")
            return False

    def run_simulation(self) -> bool:
        """Run the compiled simulation"""
        print("\n" + "="*60)
        print("STEP 5: Running simulation")
        print("="*60)

        executable = self.test_dir / 'ball3'
        if not executable.exists():
            print("❌ Executable not found")
            return False

        try:
            result = subprocess.run(
                [str(executable)],
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            print("Simulation output:")
            print(result.stdout[:500])  # Print first 500 chars

            # Check for output files
            output_files = list(self.test_dir.glob('*.asc'))
            print(f"\n✓ Generated {len(output_files)} output files:")
            for f in output_files:
                if f.name != 'input.asc':
                    print(f"  - {f.name} ({f.stat().st_size} bytes)")

            return True

        except Exception as e:
            print(f"❌ Execution error: {e}")
            return False

    def compare_results(self) -> dict:
        """Compare test results with reference"""
        print("\n" + "="*60)
        print("STEP 6: Comparing with reference trajectory")
        print("="*60)

        # Find test trajectory
        test_traj_file = self.test_dir / 'plot1.asc'
        if not test_traj_file.exists():
            print("❌ Test trajectory not found")
            return {'success': False, 'error': 'No trajectory file'}

        if not self.reference_traj.exists():
            print("❌ Reference trajectory not found")
            return {'success': False, 'error': 'No reference file'}

        try:
            # Load trajectories
            test = Trajectory.from_file(test_traj_file)
            reference = Trajectory.from_file(self.reference_traj)

            print(f"✓ Test trajectory: {len(test.time)} points")
            print(f"✓ Reference trajectory: {len(reference.time)} points")

            # Compare
            comparator = TrajectoryComparator(test, reference)

            # Get errors
            rms_errors = comparator.rms_error()
            max_errors = comparator.max_error()

            # Display results
            print("\n" + comparator.summary())

            # Define pass criteria
            # For ballistic trajectory, we expect very small errors
            critical_vars = ['SBEL3', 'altitude', 'dvbe']
            max_rms_threshold = 0.1  # 10cm RMS error threshold

            passed = True
            for var in critical_vars:
                if var in rms_errors:
                    if rms_errors[var] > max_rms_threshold:
                        print(f"⚠ {var} RMS error {rms_errors[var]:.3f} exceeds threshold {max_rms_threshold}")
                        passed = False

            return {
                'success': passed,
                'rms_errors': rms_errors,
                'max_errors': max_errors,
                'common_vars': len(comparator.common_vars)
            }

        except Exception as e:
            print(f"❌ Comparison error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def run_test(self) -> bool:
        """Run complete regression test"""
        print("\n" + "="*70)
        print(" BALL3 REGRESSION TEST")
        print("="*70)

        # Step 1: Build simulation with Python API
        sim = self.build_simulation()
        if not sim:
            print("\n❌ TEST FAILED: Could not build simulation")
            return False

        # Generate input file
        input_file = sim.generate_input_file()
        print(f"\n✓ Generated input file: {input_file}")

        # Step 2: Setup build environment
        self.setup_build_environment()

        # Step 3: Create ball_functions file
        self.create_ball_functions()

        # Step 4: Compile
        if not self.compile_simulation():
            print("\n❌ TEST FAILED: Compilation failed")
            return False

        # Step 5: Run
        if not self.run_simulation():
            print("\n❌ TEST FAILED: Execution failed")
            return False

        # Step 6: Compare
        results = self.compare_results()

        # Final verdict
        print("\n" + "="*70)
        if results['success']:
            print(" ✅ TEST PASSED - BALL3 regression successful!")
        else:
            print(" ❌ TEST FAILED - Trajectory mismatch")
            if 'error' in results:
                print(f"   Error: {results['error']}")
        print("="*70)

        return results['success']


def main():
    """Main test entry point"""
    test_dir = Path.cwd() / 'tests/regression/BALL3'

    test = BALL3Test(test_dir)
    success = test.run_test()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
