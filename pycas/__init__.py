"""
pyCAS - Python-wrapped Constructive Aerospace Simulator

A modular Python framework built on the CADAC++ aerospace simulation framework.
pyCAS extracts core concepts from CADAC examples into reusable, extendable components
for constructive simulation building.

Philosophy:
- Truly constructive: Build simulations from fundamental, composable components
- Modular by design: Each component is independent and self-contained
- Framework-agnostic components: Generic components adapt to any CADAC vehicle type
- Full transparency: Direct access to generated C++ code and compilation

Key Features:
- Component-based simulation construction from 36+ validated components
- Automatic dependency resolution and module management
- Framework adaptation layer (Vehicle → Ball/Rocket/Missile)
- Input file generation with type checking
- Compilation and execution orchestration
- Trajectory comparison for regression testing

Example Usage:
    from pycas import Simulation, Component

    # Build a ballistic simulation from fundamental components
    sim = Simulation("BALL3_test")
    sim.add_component(Component.kinematics_3dof_flat())
    sim.add_component(Component.forces_3dof())
    sim.add_component(Component.drag_simple(cd=0.47, area=0.0314))
    sim.add_component(Component.gravity_constant())
    sim.add_component(Component.atmosphere_constant())

    # Set initial conditions
    sim.set_initial_state(
        sbel1=0, sbel2=0, sbel3=0,
        vbel1=35.36, vbel2=0, vbel3=-35.36
    )

    # Generate input file and run
    sim.generate_input_file()
    results = sim.run(duration=10, dt=0.01)
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
