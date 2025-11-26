"""
Component - Wrapper class for CADAC components
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class Component:
    """Represents a configured component instance"""

    name: str
    """Component type name (e.g., 'drag_simple')"""

    parameters: Dict[str, Any] = field(default_factory=dict)
    """User-configured parameters"""

    enabled_lifecycle: List[str] = field(default_factory=lambda: ['def', 'exec'])
    """Which lifecycle methods to enable (def, init, exec)"""

    custom_label: Optional[str] = None
    """Optional custom label for this instance (for multiple instances of same type)"""

    def __post_init__(self):
        """Validate configuration"""
        # Ensure enabled_lifecycle contains valid values
        valid = {'def', 'init', 'exec'}
        for lifecycle in self.enabled_lifecycle:
            if lifecycle not in valid:
                raise ValueError(f"Invalid lifecycle method: {lifecycle}")

    def set_parameter(self, param_name: str, value: Any) -> 'Component':
        """Set a parameter value (chainable)"""
        self.parameters[param_name] = value
        return self

    def enable_init(self) -> 'Component':
        """Enable initialization lifecycle (chainable)"""
        if 'init' not in self.enabled_lifecycle:
            self.enabled_lifecycle.append('init')
        return self

    def disable_init(self) -> 'Component':
        """Disable initialization lifecycle (chainable)"""
        if 'init' in self.enabled_lifecycle:
            self.enabled_lifecycle.remove('init')
        return self

    @property
    def module_spec(self) -> str:
        """Generate MODULES section entry for input.asc"""
        lifecycle_str = ','.join(self.enabled_lifecycle)
        return f"{self.name}   {lifecycle_str}"

    def __repr__(self) -> str:
        label = f" ({self.custom_label})" if self.custom_label else ""
        return f"Component({self.name}{label}, {len(self.parameters)} params)"


# Factory methods for common components
class ComponentFactory:
    """Factory class with convenience methods for creating components"""

    # ===== ENVIRONMENT COMPONENTS =====

    @staticmethod
    def time_management() -> Component:
        """Time management component (required for all simulations)"""
        return Component(name='time_management', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def termination(altitude_min: Optional[float] = None,
                    time_max: Optional[float] = None) -> Component:
        """Termination conditions"""
        comp = Component(name='termination', enabled_lifecycle=['def', 'exec'])
        if altitude_min is not None:
            comp.set_parameter('altitude_min', altitude_min)
        if time_max is not None:
            comp.set_parameter('time_max', time_max)
        return comp

    @staticmethod
    def gravity_constant(grav: float = 9.81) -> Component:
        """Constant gravity (g = 9.81 m/s²)"""
        return Component(name='gravity_constant', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('grav', grav)

    @staticmethod
    def gravity_wgs84_simple() -> Component:
        """Altitude-varying gravity"""
        return Component(name='gravity_wgs84_simple', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def atmosphere_constant(rho: float = 1.225) -> Component:
        """Constant density atmosphere"""
        return Component(name='atmosphere_constant', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('rho', rho)

    @staticmethod
    def atmosphere_us76() -> Component:
        """US Standard Atmosphere 1976"""
        return Component(name='atmosphere_us76', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def wind_none() -> Component:
        """No wind (calm air)"""
        return Component(name='wind_none', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def wind_constant(vx: float = 0, vy: float = 0, vz: float = 0) -> Component:
        """Constant wind vector"""
        return Component(name='wind_constant', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('dvae', vx) \
            .set_parameter('dvae', vy) \
            .set_parameter('dvae', vz)

    # ===== KINEMATICS COMPONENTS =====

    @staticmethod
    def kinematics_3dof_flat() -> Component:
        """3DoF kinematics on flat Earth"""
        return Component(name='kinematics_3dof_flat', enabled_lifecycle=['def', 'init', 'exec'])

    @staticmethod
    def kinematics_6dof(psi: float = 0, theta: float = 90, phi: float = 0) -> Component:
        """6DoF kinematics with DCM integration"""
        return Component(name='kinematics_6dof', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('psibdx', psi) \
            .set_parameter('thtbdx', theta) \
            .set_parameter('phibdx', phi)

    # ===== DYNAMICS COMPONENTS =====

    @staticmethod
    def forces_3dof() -> Component:
        """3DoF force summation"""
        return Component(name='forces_3dof', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def newton_6dof() -> Component:
        """6DoF translational dynamics"""
        return Component(name='newton_6dof', enabled_lifecycle=['def', 'init', 'exec'])

    @staticmethod
    def euler_6dof() -> Component:
        """6DoF rotational dynamics"""
        return Component(name='euler_6dof', enabled_lifecycle=['def', 'init', 'exec'])

    @staticmethod
    def forces_6dof() -> Component:
        """6DoF force and moment summation"""
        return Component(name='forces_6dof', enabled_lifecycle=['def', 'exec'])

    # ===== AERODYNAMICS COMPONENTS =====

    @staticmethod
    def drag_simple(cd: float, area: float) -> Component:
        """Simple drag-only aerodynamics"""
        return Component(name='drag_simple', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('cd', cd) \
            .set_parameter('area', area)

    @staticmethod
    def aero_3dof_table() -> Component:
        """3DoF aerodynamics from tables"""
        return Component(name='aero_3dof_table', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def aerodynamics_6dof(maero: int, refa: float, refd: float) -> Component:
        """6DoF aerodynamics from tables"""
        return Component(name='aerodynamics_6dof', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('maero', maero) \
            .set_parameter('refa', refa) \
            .set_parameter('refd', refd)

    # ===== PROPULSION COMPONENTS =====

    @staticmethod
    def thrust_constant(thrust: float) -> Component:
        """Constant thrust"""
        return Component(name='thrust_constant', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('thrust', thrust)

    @staticmethod
    def rocket_motor_simple(thrust: float, burntime: float, spi: float) -> Component:
        """Simple rocket motor"""
        return Component(name='rocket_motor_simple', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('thrust', thrust) \
            .set_parameter('burntime', burntime) \
            .set_parameter('spi', spi)

    @staticmethod
    def propulsion_staging(mprop: int, vmass0: float, fmass0: float,
                           spi: float, fuel_flow_rate: float) -> Component:
        """Multi-stage rocket propulsion"""
        comp = Component(name='propulsion_staging', enabled_lifecycle=['def', 'init', 'exec'])
        comp.set_parameter('mprop', mprop)
        comp.set_parameter('vmass0', vmass0)
        comp.set_parameter('fmass0', fmass0)
        comp.set_parameter('spi', spi)
        comp.set_parameter('fuel_flow_rate', fuel_flow_rate)
        return comp

    # ===== GUIDANCE COMPONENTS =====

    @staticmethod
    def guidance_none() -> Component:
        """No guidance (ballistic)"""
        return Component(name='guidance_none', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def guidance_proportional_nav(gnav: float = 3.0, gmax: float = 10.0) -> Component:
        """Proportional navigation guidance"""
        return Component(name='guidance_proportional_nav', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('gnav', gnav) \
            .set_parameter('gmax', gmax)

    @staticmethod
    def guidance_pitch_program(time_table: List[float], pitch_table: List[float]) -> Component:
        """Time-based pitch program"""
        comp = Component(name='guidance_pitch_program', enabled_lifecycle=['def', 'init', 'exec'])
        comp.set_parameter('npitch', len(time_table))
        comp.set_parameter('time_table', time_table)
        comp.set_parameter('pitch_table', pitch_table)
        return comp

    # ===== CONTROL COMPONENTS =====

    @staticmethod
    def control_none() -> Component:
        """No control"""
        return Component(name='control_none', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def control_rate_damping(gain: float = 0.5) -> Component:
        """Simple rate damping"""
        return Component(name='control_rate_damping', enabled_lifecycle=['def', 'exec']) \
            .set_parameter('gain', gain)

    @staticmethod
    def control_accel_autopilot(waclp: float, zaclp: float, paclp: float) -> Component:
        """3DoF acceleration autopilot"""
        return Component(name='control_accel_autopilot', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('waclp', waclp) \
            .set_parameter('zaclp', zaclp) \
            .set_parameter('paclp', paclp)

    @staticmethod
    def control_accel_6dof(waclp: float, zaclp: float, paclp: float) -> Component:
        """6DoF dual-channel acceleration autopilot"""
        return Component(name='control_accel_6dof', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('waclp', waclp) \
            .set_parameter('zaclp', zaclp) \
            .set_parameter('paclp', paclp)

    # ===== ACTUATOR COMPONENTS =====

    @staticmethod
    def actuator_first_order(tau: float = 0.1) -> Component:
        """First-order actuator lag"""
        return Component(name='actuator_first_order', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('tau', tau)

    @staticmethod
    def tvc_simple(wntvc: float, zettvc: float, tvclimx: float) -> Component:
        """Thrust vector control"""
        return Component(name='tvc_simple', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('wntvc', wntvc) \
            .set_parameter('zettvc', zettvc) \
            .set_parameter('tvclimx', tvclimx)

    @staticmethod
    def rcs_simple(rcs_zeta: float = 0.7, rcs_freq: float = 10.0) -> Component:
        """Reaction control system"""
        return Component(name='rcs_simple', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('rcs_zeta', rcs_zeta) \
            .set_parameter('rcs_freq', rcs_freq)

    # ===== SENSOR COMPONENTS =====

    @staticmethod
    def seeker_perfect() -> Component:
        """Perfect target seeker"""
        return Component(name='seeker_perfect', enabled_lifecycle=['def', 'exec'])

    @staticmethod
    def gps_perfect() -> Component:
        """Perfect GPS sensor"""
        return Component(name='gps_perfect', enabled_lifecycle=['def', 'exec'])

    # ===== NAVIGATION COMPONENTS =====

    @staticmethod
    def target_fixed(x: float, y: float, z: float) -> Component:
        """Stationary target"""
        return Component(name='target_fixed', enabled_lifecycle=['def', 'init', 'exec']) \
            .set_parameter('x', x) \
            .set_parameter('y', y) \
            .set_parameter('z', z)

    @staticmethod
    def target_const_velocity(x: float, y: float, z: float,
                               vx: float, vy: float, vz: float) -> Component:
        """Constant velocity target"""
        comp = Component(name='target_const_velocity', enabled_lifecycle=['def', 'init', 'exec'])
        comp.set_parameter('x', x).set_parameter('y', y).set_parameter('z', z)
        comp.set_parameter('vx', vx).set_parameter('vy', vy).set_parameter('vz', vz)
        return comp

    @staticmethod
    def intercept_simple() -> Component:
        """Simple miss distance calculation"""
        return Component(name='intercept_simple', enabled_lifecycle=['def', 'exec'])


# Expose factory methods at Component class level for convenience
# This allows: Component.drag_simple(cd=0.47, area=0.0314)
for method_name in dir(ComponentFactory):
    if not method_name.startswith('_'):
        setattr(Component, method_name, staticmethod(getattr(ComponentFactory, method_name)))
