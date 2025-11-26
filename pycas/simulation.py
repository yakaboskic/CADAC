"""
Simulation - Main class for building and running CADAC simulations
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from .component import Component
from .component_registry import ComponentRegistry, ComponentMetadata
from .input_generator import InputFileGenerator
from .compiler import Compiler
from .runner import Runner
from .trajectory import Trajectory


class Simulation:
    """Represents a complete CADAC simulation"""

    def __init__(self, name: str, working_dir: Optional[Path] = None,
                 components_dir: Optional[Path] = None):
        """
        Initialize a new simulation

        Args:
            name: Simulation name (used for directory and output files)
            working_dir: Working directory for simulation files (default: ./sims/{name})
            components_dir: Path to components directory (default: ../components)
        """
        self.name = name
        self.components: List[Component] = []
        self.initial_state: Dict[str, Any] = {}
        self.simulation_config: Dict[str, Any] = {
            'duration': 100.0,
            'dt': 0.01,
            'output_step': 0.1
        }

        # Set up directories
        if working_dir is None:
            self.working_dir = Path.cwd() / 'sims' / name
        else:
            self.working_dir = Path(working_dir)

        self.working_dir.mkdir(parents=True, exist_ok=True)

        # Initialize registry
        self.registry = ComponentRegistry(components_dir)

        # Initialize helper classes
        self.input_generator = InputFileGenerator(self.registry)
        self.compiler = Compiler(self.working_dir)
        self.runner = Runner(self.working_dir)

        self._compiled = False
        self._executable_path: Optional[Path] = None

    @property
    def executable_path(self) -> Optional[Path]:
        """Get path to compiled executable"""
        return self._executable_path

    def add_component(self, component: Component) -> 'Simulation':
        """
        Add a component to the simulation

        Args:
            component: Component instance to add

        Returns:
            self (for method chaining)
        """
        self.components.append(component)
        self._compiled = False  # Invalidate compilation
        return self

    def set_initial_state(self, **kwargs) -> 'Simulation':
        """
        Set initial state variables

        Common variables:
            - altitude: Initial altitude (m)
            - velocity: Initial velocity (m/s)
            - flight_path_angle: Initial flight path angle (deg)
            - lonx, latx: Initial longitude, latitude (deg)
            - psibdx, thtbdx, phibdx: Initial Euler angles (deg)

        Returns:
            self (for method chaining)
        """
        self.initial_state.update(kwargs)
        return self

    def set_config(self, **kwargs) -> 'Simulation':
        """
        Set simulation configuration

        Args:
            duration: Simulation duration (sec)
            dt: Integration time step (sec)
            output_step: Output time step (sec)

        Returns:
            self (for method chaining)
        """
        self.simulation_config.update(kwargs)
        return self

    def validate(self) -> List[str]:
        """
        Validate the simulation configuration

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for required components
        component_names = [c.name for c in self.components]

        if 'time_management' not in component_names:
            errors.append("Missing required component: time_management")

        if 'termination' not in component_names:
            errors.append("Missing required component: termination")

        # TODO: Add more sophisticated validation
        # For now, just check that components exist in registry
        for component in self.components:
            meta = self.registry.get(component.name)
            if not meta:
                errors.append(f"Unknown component: {component.name}")

        return errors

    def generate_input_file(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate input.asc file

        Args:
            output_path: Path to write input file (default: working_dir/input.asc)

        Returns:
            Path to generated file
        """
        if output_path is None:
            output_path = self.working_dir / 'input.asc'

        content = self.input_generator.generate(
            simulation_name=self.name,
            components=self.components,
            initial_state=self.initial_state,
            config=self.simulation_config
        )

        output_path.write_text(content)
        return output_path

    def compile(self, force: bool = False) -> Path:
        """
        Compile the simulation

        Args:
            force: Force recompilation even if already compiled

        Returns:
            Path to executable

        Raises:
            ValueError: If validation fails
            RuntimeError: If compilation fails
        """
        if self._compiled and not force:
            return self._executable_path

        # Validate first
        errors = self.validate()
        if errors:
            raise ValueError(f"Validation failed:\n" + '\n'.join(f"  - {e}" for e in errors))

        # Generate input file
        input_file = self.generate_input_file()
        print(f"Generated input file: {input_file}")

        # Compile
        print(f"Compiling simulation '{self.name}'...")
        self._executable_path = self.compiler.compile(
            simulation_name=self.name,
            components=[c.name for c in self.components]
        )

        self._compiled = True
        print(f"Compilation successful: {self._executable_path}")
        return self._executable_path

    def run(self, duration: Optional[float] = None,
            dt: Optional[float] = None,
            recompile: bool = False) -> Trajectory:
        """
        Run the simulation

        Args:
            duration: Override simulation duration (sec)
            dt: Override integration time step (sec)
            recompile: Force recompilation before running

        Returns:
            Trajectory object with results

        Raises:
            RuntimeError: If simulation is not compiled or run fails
        """
        # Update config if overrides provided
        if duration is not None:
            self.simulation_config['duration'] = duration
        if dt is not None:
            self.simulation_config['dt'] = dt

        # Ensure compiled
        if recompile or not self._compiled:
            self.compile(force=recompile)

        # Run simulation
        print(f"Running simulation '{self.name}'...")
        output_file = self.runner.run(
            executable=self._executable_path,
            input_file=self.working_dir / 'input.asc'
        )

        # Load and return trajectory
        trajectory = Trajectory.from_file(output_file)
        print(f"Simulation complete. Output: {output_file}")
        return trajectory

    def compare(self, trajectory: Trajectory, reference_file: Path) -> 'TrajectoryComparator':
        """
        Compare simulation results with reference trajectory

        Args:
            trajectory: Simulation results
            reference_file: Path to reference trajectory file

        Returns:
            TrajectoryComparator with comparison results
        """
        from .trajectory import TrajectoryComparator

        reference = Trajectory.from_file(reference_file)
        return TrajectoryComparator(trajectory, reference)

    def __repr__(self) -> str:
        return f"Simulation('{self.name}', {len(self.components)} components)"

    def __str__(self) -> str:
        lines = [f"Simulation: {self.name}"]
        lines.append(f"Working Directory: {self.working_dir}")
        lines.append(f"Components ({len(self.components)}):")
        for comp in self.components:
            lines.append(f"  - {comp.name}")
        if self.initial_state:
            lines.append("Initial State:")
            for key, value in self.initial_state.items():
                lines.append(f"  {key} = {value}")
        return '\n'.join(lines)
