"""
Compiler - Compiles CADAC simulations
"""

import subprocess
from pathlib import Path
from typing import List


class Compiler:
    """Compiles CADAC C++ simulations"""

    def __init__(self, working_dir: Path):
        self.working_dir = Path(working_dir)
        self.components_dir = Path(__file__).parent.parent / 'components'

    def compile(self, simulation_name: str, components: List[str]) -> Path:
        """
        Compile simulation executable

        For now, this uses the existing BALL3 example as a base.
        Future: Full compilation from modular components (see test_ball3_regression.py)

        Args:
            simulation_name: Name of simulation
            components: List of component names to include

        Returns:
            Path to compiled executable

        Raises:
            RuntimeError: If compilation fails
        """
        # Use existing BALL3 example for now
        example_dir = self.components_dir.parent / 'example' / 'BALL3'
        if not example_dir.exists():
            raise RuntimeError(
                f"BALL3 example not found at {example_dir}. "
                "Full compilation from components requires framework adaptation. "
                "See tests/regression/test_ball3_regression.py for proper implementation."
            )

        # Build BALL3 example
        print(f"  Using existing BALL3 example for compilation...")
        result = subprocess.run(
            ['make'],
            cwd=example_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"BALL3 compilation failed:\n{result.stderr}")

        # Return path to executable
        executable = example_dir / 'ball3'
        if not executable.exists():
            raise RuntimeError(f"Executable not found: {executable}")

        print(f"  ✓ Compiled: {executable}")
        return executable

    def _find_component_file(self, comp_name: str) -> Path:
        """Find component source file"""
        # Search all subdirectories for the component
        for cpp_file in self.components_dir.rglob(f"{comp_name}.cpp"):
            return cpp_file
        return None

    def _create_ball_functions(self, components: List[str], build_dir: Path) -> Path:
        """Create ball_functions.cpp with adapted component code"""
        # Start with Ball class implementation stub
        content = """// Auto-generated ball_functions.cpp
#include "class_hierarchy.hpp"

// Ball class module implementations
// These are stubs - the actual module implementations come from component files
"""

        ball_functions = build_dir / 'ball_functions.cpp'
        ball_functions.write_text(content)
        return ball_functions

    def _create_generic_main(self, simulation_name: str, build_dir: Path) -> Path:
        """Create a generic main.cpp for the simulation"""
        main_content = f"""
// Auto-generated main for {simulation_name}
#include "class_hierarchy.hpp"

int main()
{{
    // Create simulation
    Vehicle vehicle;

    // Load input file
    vehicle.load_input("../input.asc");

    // Run simulation
    vehicle.run();

    return 0;
}}
"""
        main_file = build_dir / 'main.cpp'
        main_file.write_text(main_content)
        return main_file
