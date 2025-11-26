"""
Runner - Executes CADAC simulations
"""

import subprocess
from pathlib import Path


class Runner:
    """Runs compiled CADAC simulations"""

    def __init__(self, working_dir: Path):
        self.working_dir = Path(working_dir)

    def run(self, executable: Path, input_file: Path) -> Path:
        """
        Run simulation

        Args:
            executable: Path to compiled executable
            input_file: Path to input.asc file

        Returns:
            Path to trajectory output file

        Raises:
            RuntimeError: If execution fails
        """
        if not executable.exists():
            raise RuntimeError(f"Executable not found: {executable}")

        if not input_file.exists():
            raise RuntimeError(f"Input file not found: {input_file}")

        # Run simulation
        try:
            result = subprocess.run(
                [str(executable)],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )

            # Check for trajectory output
            traj_file = self.working_dir / 'traj.asc'
            if not traj_file.exists():
                # Try alternative names
                traj_file = self.working_dir / 'trajectory.asc'

            if not traj_file.exists():
                raise RuntimeError("Trajectory file not generated")

            return traj_file

        except subprocess.TimeoutExpired:
            raise RuntimeError("Simulation timed out (5 minutes)")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Simulation failed:\n{e.stderr}")
