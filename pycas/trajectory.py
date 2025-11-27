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

        # Parse CADAC format:
        # Line 1: Title and metadata
        # Line 2: Header numbers
        # Lines 3+: Variable names (may wrap)
        # Lines N+: Data (may wrap)

        # Skip first 2 lines (title and header)
        i = 2

        # Collect variable names (may be wrapped across multiple lines)
        variables = []
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('//'):
                i += 1
                continue

            tokens = line.split()
            # Check if this looks like variable names (not all numeric)
            try:
                # Try to convert to float - if it succeeds, it's data not variables
                [float(x) for x in tokens]
                # All numeric - this is the start of data
                break
            except ValueError:
                # Has non-numeric tokens - still variable names
                variables.extend(tokens)
                i += 1

        data_start_line = i

        if not variables:
            raise ValueError("No variable names found in trajectory file")

        # Collect all remaining tokens as data values
        all_values = []
        for line in lines[data_start_line:]:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            try:
                values = [float(x) for x in line.split()]
                all_values.extend(values)
            except ValueError:
                continue

        if not all_values:
            raise ValueError("No valid data found in trajectory file")

        # Group values into rows of len(variables) each
        num_vars = len(variables)
        raw_data = []
        for i in range(0, len(all_values), num_vars):
            if i + num_vars <= len(all_values):
                raw_data.append(all_values[i:i+num_vars])

        if not raw_data:
            raise ValueError("No complete data rows found in trajectory file")

        data_array = np.array(raw_data)

        # Build data dictionary
        data_dict = {}
        for i, var_name in enumerate(variables):
            data_dict[var_name] = data_array[:, i]

        # Try to find time variable
        # Check for common time variable names
        time = None
        for time_name in ['time', 'Time', 'TIME', 't']:
            if time_name in data_dict:
                time = data_dict[time_name]
                break

        # If no time variable found, generate synthetic time array
        if time is None:
            # Generate time based on number of points
            # Assume uniform sampling at 0.05s intervals (typical plot_step)
            time = np.arange(len(raw_data), dtype=float) * 0.05

        return cls(time, data_dict)

    def get(self, variable: str) -> Optional[np.ndarray]:
        """Get data for a specific variable"""
        return self.data.get(variable)

    def to_dataframe(self):
        """
        Convert trajectory to Pandas DataFrame

        Returns:
            pd.DataFrame with time index and all variables as columns

        Raises:
            ImportError: If pandas is not installed
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is required for DataFrame conversion. "
                "Install with: pip install pandas"
            )

        # Create DataFrame with time as index
        df = pd.DataFrame(self.data, index=self.time)
        df.index.name = 'time'

        return df

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
