"""
Compiler - Compiles CADAC simulations from modular components
"""

import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Set
import tempfile


class Compiler:
    """Compiles CADAC C++ simulations from modular components"""

    def __init__(self, working_dir: Path):
        self.working_dir = Path(working_dir)
        self.components_dir = Path(__file__).parent.parent / 'components'
        # Core CADAC++ framework files
        self.framework_dir = Path(__file__).parent.parent / 'framework'

    def compile(self, simulation_name: str, components: List[str]) -> Path:
        """
        Compile simulation executable from modular components

        This performs full framework adaptation and compilation:
        1. Creates build directory
        2. Copies framework files
        3. Adapts components (Vehicle → Ball)
        4. Handles module merging
        5. Creates ball_functions.cpp
        6. Compiles everything

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
        build_dir.mkdir(parents=True, exist_ok=True)

        print(f"Building {simulation_name} from components...")
        print(f"  Build directory: {build_dir}")

        # Step 1: Copy framework files
        self._copy_framework_files(build_dir)

        # Step 2: Identify and group components by module
        module_groups = self._group_components_by_module(components)

        # Step 3: Adapt and merge components
        adapted_files = self._adapt_components(module_groups, build_dir)

        # Step 4: Compile everything
        executable = self._compile_sources(simulation_name, adapted_files, build_dir)

        print(f"  ✓ Compilation successful: {executable}")
        return executable

    def _copy_framework_files(self, build_dir: Path):
        """Copy all necessary framework files to build directory"""
        print("  Copying framework files...")

        framework_files = [
            'class_hierarchy.hpp',
            'global_header.hpp',
            'global_constants.hpp',
            'utility_header.hpp',
            'utility_functions.cpp',
            'global_functions.cpp',
            'class_functions.cpp',
            'execution.cpp',
            'ball_functions.cpp'  # Utility functions for Ball class
        ]

        for filename in framework_files:
            src = self.framework_dir / filename
            dst = build_dir / filename
            if src.exists():
                shutil.copy(src, dst)
                print(f"    ✓ {filename}")
            else:
                raise RuntimeError(f"Framework file not found: {src}")

    def _group_components_by_module(self, components: List[str]) -> Dict[str, List[str]]:
        """
        Group components by their module names

        Some components contribute to the same module (e.g., gravity_constant
        and atmosphere_constant both contribute to environment module).
        We need to merge these.
        """
        # Map component names to module names
        # This is based on the module functions they define
        # Note: time_management and termination are not supported by Ball class
        module_map = {
            # 'time_management': 'time',  # Not supported by Ball class
            'kinematics_3dof_flat': 'kinematics',
            'kinematics_6dof_sph': 'kinematics',
            'forces_3dof': 'forces',
            'forces_6dof': 'forces',
            'drag_simple': 'forces',  # Contributes to forces
            'gravity_constant': 'environment',
            'gravity_wgs84': 'environment',
            'atmosphere_constant': 'environment',
            'atmosphere_us76': 'environment',
            # 'termination': 'termination',  # Not supported by Ball class
        }

        groups = {}
        for comp_name in components:
            if comp_name not in module_map:
                print(f"    ⚠ Skipping unsupported component: {comp_name}")
                continue
            module = module_map[comp_name]
            if module not in groups:
                groups[module] = []
            groups[module].append(comp_name)

        print(f"  Component grouping:")
        for module, comps in groups.items():
            print(f"    {module}: {', '.join(comps)}")

        return groups

    def _adapt_components(self, module_groups: Dict[str, List[str]], build_dir: Path) -> List[Path]:
        """
        Adapt components from Vehicle:: to Ball:: and merge when necessary

        Returns list of adapted .cpp files
        """
        print("  Adapting components...")
        adapted_files = []

        for module_name, component_names in module_groups.items():
            if len(component_names) == 1:
                # Single component - simple adaptation
                adapted_file = self._adapt_single_component(
                    component_names[0], module_name, build_dir
                )
            else:
                # Multiple components - need to merge
                adapted_file = self._merge_components(
                    component_names, module_name, build_dir
                )

            adapted_files.append(adapted_file)
            print(f"    ✓ {adapted_file.name}")

        return adapted_files

    def _adapt_single_component(self, comp_name: str, module_name: str, build_dir: Path) -> Path:
        """Adapt a single component from Vehicle:: to Ball::"""
        # Find component source file
        comp_file = self._find_component_file(comp_name)
        if not comp_file:
            raise RuntimeError(f"Component not found: {comp_name}")

        # Read and adapt
        content = comp_file.read_text()
        adapted_content = content.replace('Vehicle::', 'Ball::').replace('vehicle[', 'ball[')

        # Write to build directory
        output_file = build_dir / f'{module_name}.cpp'
        output_file.write_text(adapted_content)

        return output_file

    def _merge_components(self, comp_names: List[str], module_name: str, build_dir: Path) -> Path:
        """
        Merge multiple components that contribute to the same module

        For example: gravity_constant + atmosphere_constant → environment.cpp
        """
        print(f"    Merging {len(comp_names)} components into {module_name}.cpp")

        # Special handling for known module merges
        if module_name == 'environment':
            return self._merge_environment_components(comp_names, build_dir)
        elif module_name == 'forces':
            return self._merge_forces_components(comp_names, build_dir)
        else:
            # Generic merge - just concatenate (may need manual fixing)
            return self._generic_merge(comp_names, module_name, build_dir)

    def _merge_environment_components(self, comp_names: List[str], build_dir: Path) -> Path:
        """Merge environment components (gravity + atmosphere)"""
        content = """// Merged environment module
#include "class_hierarchy.hpp"

void Ball::def_environment()
{
"""
        # Collect all variable definitions
        init_calls = []
        for comp_name in comp_names:
            comp_file = self._find_component_file(comp_name)
            comp_content = comp_file.read_text()

            # Extract init calls from def_environment
            if 'def_environment' in comp_content:
                lines = comp_content.split('\n')
                in_def = False
                for line in lines:
                    if 'void Vehicle::def_environment()' in line:
                        in_def = True
                    elif in_def and '.init(' in line:
                        # Adapt line
                        adapted = line.replace('vehicle[', 'ball[')
                        init_calls.append(adapted)
                    elif in_def and line.strip() == '}':
                        break

        content += '\n'.join(init_calls)
        content += """
}

void Ball::environment(double int_step)
{
    // Read parameters (will be set from input.asc)
"""

        # Add variable reads and assignments
        assignments = []
        for comp_name in comp_names:
            if 'gravity' in comp_name:
                content += "    double grav = ball[0].real();\n"
                assignments.append("    ball[0].gets(grav);")
            elif 'atmosphere' in comp_name:
                content += "    double rho = ball[12].real();\n"
                assignments.append("    ball[12].gets(rho);")

        content += "\n"
        content += '\n'.join(assignments)
        content += "\n}\n"

        output_file = build_dir / 'environment.cpp'
        output_file.write_text(content)
        return output_file

    def _merge_forces_components(self, comp_names: List[str], build_dir: Path) -> Path:
        """Merge forces components (forces_3dof + drag)"""
        # Check if we have drag + forces
        has_drag = any('drag' in name for name in comp_names)
        has_forces = any('forces' in name for name in comp_names)

        if has_drag and has_forces:
            # Merge drag into forces
            content = """// Merged forces module
#include "class_hierarchy.hpp"

void Ball::def_forces()
{
    // From drag component
    ball[10].init("cd",0,"Drag coefficient - ND","data","","");
    ball[11].init("area",0,"Reference area - m^2","data","","");
    ball[13].init("dvbe",0,"Speed - m/s","out","scrn","plot");

    // From forces component
    ball[14].init("FSPA",0,0,0,"Specific force in body frame - m/s^2","forces","out","");
}

void Ball::forces(double int_step)
{
    // Read parameters
    double cd = ball[10].real();
    double area = ball[11].real();
    double grav = ball[0].real();
    double rho = ball[12].real();

    // Read velocity
    Matrix VBEL = ball[21].vec();

    // Calculate speed
    double dvbe = VBEL.absolute();
    ball[13].gets(dvbe);

    // Calculate drag force
    Matrix FSPB(3,1);
    if(dvbe > 0.01) {
        double q = 0.5 * rho * dvbe * dvbe;  // dynamic pressure
        Matrix drag_dir = VBEL * (-1.0 / dvbe);  // opposite to velocity
        Matrix FDRAG = drag_dir * (q * cd * area);
        FSPB = FDRAG;
    }

    // Add gravity (down direction is positive Z)
    FSPB[2] = FSPB[2] + grav;

    ball[14].gets_vec(FSPB);
}
"""
        else:
            # Just one component - adapt it
            return self._adapt_single_component(comp_names[0], 'forces', build_dir)

        output_file = build_dir / 'forces.cpp'
        output_file.write_text(content)
        return output_file

    def _generic_merge(self, comp_names: List[str], module_name: str, build_dir: Path) -> Path:
        """Generic component merge - just adapt and concatenate"""
        content = "#include \"class_hierarchy.hpp\"\n\n"

        for comp_name in comp_names:
            comp_file = self._find_component_file(comp_name)
            comp_content = comp_file.read_text()

            # Adapt
            adapted = comp_content.replace('Vehicle::', 'Ball::').replace('vehicle[', 'ball[')

            # Remove duplicate includes
            lines = [line for line in adapted.split('\n') if not line.strip().startswith('#include')]
            content += '\n'.join(lines) + '\n\n'

        output_file = build_dir / f'{module_name}.cpp'
        output_file.write_text(content)
        return output_file

    def _compile_sources(self, simulation_name: str, adapted_files: List[Path], build_dir: Path) -> Path:
        """Compile all sources into executable"""
        print("  Compiling C++ sources...")

        # Collect all source files
        source_files = [
            'ball_functions.cpp',
            'class_functions.cpp',
            'execution.cpp',
            'global_functions.cpp',
            'utility_functions.cpp',
        ]

        # Add adapted component files
        source_files.extend([f.name for f in adapted_files])

        # Compile command
        executable = build_dir / simulation_name.lower()
        compile_cmd = [
            'g++',
            '-std=c++11',
            '-O2',
            '-Wno-write-strings',
            '-Wno-conversion-null',
            '-Wno-format-overflow',
            *source_files,
            '-o', str(executable.name),
            '-I', str(build_dir)
        ]

        print(f"    Compiling...")

        # Run compilation
        result = subprocess.run(
            compile_cmd,
            cwd=build_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Print detailed error
            print(f"\n❌ Compilation failed:")
            print(result.stderr)
            raise RuntimeError(f"Compilation failed. See errors above.")

        if not executable.exists():
            raise RuntimeError(f"Executable not found after compilation: {executable}")

        return executable

    def _find_component_file(self, comp_name: str) -> Path:
        """Find component source file"""
        for cpp_file in self.components_dir.rglob(f"{comp_name}.cpp"):
            return cpp_file
        return None
