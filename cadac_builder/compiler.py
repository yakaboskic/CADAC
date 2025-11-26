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

        Args:
            simulation_name: Name of simulation
            components: List of component names to include

        Returns:
            Path to compiled executable

        Raises:
            RuntimeError: If compilation fails
        """
        # Create build directory
        build_dir = self.working_dir / 'build'
        build_dir.mkdir(exist_ok=True)

        # Collect all component source files
        source_files = []
        for comp_name in components:
            # Find the component file
            comp_file = self._find_component_file(comp_name)
            if comp_file:
                source_files.append(str(comp_file))

        if not source_files:
            raise RuntimeError("No component source files found")

        # Add main simulation driver (we'll need to create this)
        # For now, assume it exists in the CADAC framework
        main_file = self.components_dir.parent / 'BALL3' / 'BALL3.cpp'
        if not main_file.exists():
            # Use a generic main if example doesn't exist
            main_file = self._create_generic_main(simulation_name, build_dir)

        # Compile command
        executable = build_dir / simulation_name
        compile_cmd = [
            'g++',
            '-std=c++11',
            '-O2',
            str(main_file),
            *source_files,
            '-I', str(self.components_dir.parent),
            '-o', str(executable)
        ]

        # Run compilation
        try:
            result = subprocess.run(
                compile_cmd,
                cwd=build_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return executable
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Compilation failed:\n{e.stderr}\n\nCommand: {' '.join(compile_cmd)}"
            )

    def _find_component_file(self, comp_name: str) -> Path:
        """Find component source file"""
        # Search all subdirectories for the component
        for cpp_file in self.components_dir.rglob(f"{comp_name}.cpp"):
            return cpp_file
        return None

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
