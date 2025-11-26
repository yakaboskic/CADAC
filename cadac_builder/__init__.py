"""
CADAC Simulation Builder

A Python framework for constructing and running CADAC simulations from modular components.

Key Features:
- Component-based simulation construction
- Automatic dependency resolution
- Input file generation
- Compilation and execution
- Trajectory comparison for regression testing

Example Usage:
    from cadac_builder import Simulation, Component

    # Build a simple ballistic simulation
    sim = Simulation("BALL3_test")
    sim.add_component(Component.time_management())
    sim.add_component(Component.kinematics_3dof_flat())
    sim.add_component(Component.forces_3dof())
    sim.add_component(Component.drag_simple(cd=0.47, area=0.0314))
    sim.add_component(Component.gravity_constant())
    sim.add_component(Component.atmosphere_constant())
    sim.add_component(Component.termination(altitude_min=0))

    # Set initial conditions
    sim.set_initial_state(
        altitude=1000,
        velocity=250,
        flight_path_angle=45
    )

    # Compile and run
    sim.compile()
    results = sim.run(duration=100, dt=0.01)

    # Compare with ground truth
    comparison = sim.compare(results, "BALL3/traj.asc")
    print(f"RMS error: {comparison.rms_error()}")
"""

from .component_registry import ComponentRegistry
from .component import Component
from .simulation import Simulation
from .compiler import Compiler
from .runner import Runner
from .trajectory import Trajectory, TrajectoryComparator

__all__ = [
    'ComponentRegistry',
    'Component',
    'Simulation',
    'Compiler',
    'Runner',
    'Trajectory',
    'TrajectoryComparator',
]

__version__ = '0.1.0'
