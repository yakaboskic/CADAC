"""
Trajectory - Parse and analyze CADAC trajectory output
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Trajectory:
    """CADAC trajectory data"""

    time: np.ndarray
    """Time vector (sec)"""

    data: Dict[str, np.ndarray]
    """Dictionary of variable name -> data array"""

    variables: List[str]
    """List of variable names"""

    def __init__(self, time: np.ndarray, data: Dict[str, np.ndarray]):
        self.time = time
        self.data = data
        self.variables = list(data.keys())

    @classmethod
    def from_file(cls, filepath: Path) -> 'Trajectory':
        """
        Load trajectory from CADAC output file

        Args:
            filepath: Path to traj.asc file

        Returns:
            Trajectory object
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Trajectory file not found: {filepath}")

        # Read the file
        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Parse header to get variable names
        variables = []
        data_start_line = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('//'):
                continue
            elif not variables:
                # First non-comment line should be variable names
                variables = line.strip().split()
                data_start_line = i + 1
                break

        # Parse data
        data_lines = [line.strip() for line in lines[data_start_line:]
                      if line.strip() and not line.startswith('//')]

        # Convert to numpy array
        raw_data = []
        for line in data_lines:
            try:
                values = [float(x) for x in line.split()]
                if len(values) == len(variables):
                    raw_data.append(values)
            except ValueError:
                continue

        if not raw_data:
            raise ValueError("No valid data found in trajectory file")

        data_array = np.array(raw_data)

        # Extract time and build data dictionary
        time = data_array[:, 0] if variables[0].lower() in ['time', 't'] else np.arange(len(data_array))

        data_dict = {}
        for i, var_name in enumerate(variables):
            data_dict[var_name] = data_array[:, i]

        return cls(time, data_dict)

    def get(self, variable: str) -> Optional[np.ndarray]:
        """Get data for a specific variable"""
        return self.data.get(variable)

    def plot(self, *variables: str, title: Optional[str] = None):
        """
        Plot trajectory variables

        Args:
            *variables: Variable names to plot
            title: Optional plot title
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available for plotting")
            return

        fig, axes = plt.subplots(len(variables), 1, figsize=(10, 3 * len(variables)))
        if len(variables) == 1:
            axes = [axes]

        for ax, var in zip(axes, variables):
            if var in self.data:
                ax.plot(self.time, self.data[var])
                ax.set_ylabel(var)
                ax.grid(True)
            else:
                ax.text(0.5, 0.5, f"Variable '{var}' not found",
                        ha='center', va='center')

        axes[-1].set_xlabel('Time (sec)')
        if title:
            fig.suptitle(title)

        plt.tight_layout()
        plt.show()

    def __repr__(self) -> str:
        return f"Trajectory({len(self.time)} points, {len(self.variables)} variables)"

    def __str__(self) -> str:
        lines = [f"Trajectory: {len(self.time)} time points"]
        lines.append(f"Duration: {self.time[0]:.3f} - {self.time[-1]:.3f} sec")
        lines.append(f"Variables ({len(self.variables)}): {', '.join(self.variables[:5])}...")
        return '\n'.join(lines)


class TrajectoryComparator:
    """Compare two trajectories for regression testing"""

    def __init__(self, test: Trajectory, reference: Trajectory):
        """
        Initialize comparator

        Args:
            test: Test trajectory
            reference: Reference trajectory
        """
        self.test = test
        self.reference = reference
        self._interpolate_reference()

    def _interpolate_reference(self):
        """Interpolate reference trajectory to match test time points"""
        # Find common variables
        self.common_vars = set(self.test.variables) & set(self.reference.variables)

        # Interpolate reference to test time points
        self.reference_interp = {}
        for var in self.common_vars:
            self.reference_interp[var] = np.interp(
                self.test.time,
                self.reference.time,
                self.reference.data[var]
            )

    def rms_error(self, variable: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate RMS error for variables

        Args:
            variable: Specific variable (if None, computes for all)

        Returns:
            Dictionary of variable -> RMS error
        """
        errors = {}

        vars_to_check = [variable] if variable else self.common_vars

        for var in vars_to_check:
            if var not in self.common_vars:
                continue

            test_data = self.test.data[var]
            ref_data = self.reference_interp[var]

            # RMS error
            diff = test_data - ref_data
            rms = np.sqrt(np.mean(diff ** 2))
            errors[var] = rms

        return errors

    def max_error(self, variable: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate maximum absolute error

        Args:
            variable: Specific variable (if None, computes for all)

        Returns:
            Dictionary of variable -> max absolute error
        """
        errors = {}

        vars_to_check = [variable] if variable else self.common_vars

        for var in vars_to_check:
            if var not in self.common_vars:
                continue

            test_data = self.test.data[var]
            ref_data = self.reference_interp[var]

            # Max absolute error
            max_err = np.max(np.abs(test_data - ref_data))
            errors[var] = max_err

        return errors

    def summary(self) -> str:
        """Generate comparison summary"""
        lines = ["Trajectory Comparison Summary"]
        lines.append("=" * 50)
        lines.append(f"Common variables: {len(self.common_vars)}")
        lines.append("")

        rms_errors = self.rms_error()
        max_errors = self.max_error()

        lines.append(f"{'Variable':<20} {'RMS Error':<15} {'Max Error':<15}")
        lines.append("-" * 50)

        for var in sorted(self.common_vars):
            if var == 'time':
                continue
            rms = rms_errors.get(var, 0)
            max_err = max_errors.get(var, 0)
            lines.append(f"{var:<20} {rms:<15.6e} {max_err:<15.6e}")

        return '\n'.join(lines)

    def plot_comparison(self, *variables: str):
        """
        Plot test vs reference for specified variables

        Args:
            *variables: Variables to plot
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available for plotting")
            return

        fig, axes = plt.subplots(len(variables), 1, figsize=(12, 4 * len(variables)))
        if len(variables) == 1:
            axes = [axes]

        for ax, var in zip(axes, variables):
            if var not in self.common_vars:
                ax.text(0.5, 0.5, f"Variable '{var}' not in both trajectories",
                        ha='center', va='center')
                continue

            ax.plot(self.test.time, self.test.data[var], 'b-', label='Test', linewidth=2)
            ax.plot(self.reference.time, self.reference.data[var], 'r--', label='Reference', linewidth=2)
            ax.set_ylabel(var)
            ax.legend()
            ax.grid(True)

            # Add error subplot
            ax2 = ax.twinx()
            error = self.test.data[var] - self.reference_interp[var]
            ax2.plot(self.test.time, error, 'g-', alpha=0.3, label='Error')
            ax2.set_ylabel('Error', color='g')
            ax2.tick_params(axis='y', labelcolor='g')

        axes[-1].set_xlabel('Time (sec)')
        fig.suptitle('Trajectory Comparison: Test vs Reference')
        plt.tight_layout()
        plt.show()
