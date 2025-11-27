"""
Runner - Executes CADAC simulations
"""

import subprocess
import shutil
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

        # CADAC executables expect input.asc in their directory
        # Copy input file to executable directory
        exec_dir = executable.parent
        exec_input = exec_dir / 'input.asc'
        shutil.copy(input_file, exec_input)
        print(f"  Copied input file to {exec_input}")

        # Run simulation from executable directory
        print(f"  Running {executable.name}...")
        try:
            result = subprocess.run(
                [f'./{executable.name}'],
                cwd=exec_dir,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )

            print(f"  ✓ Simulation completed")

            # Check for trajectory output in executable directory
            traj_file = exec_dir / 'plot1.asc'
            if not traj_file.exists():
                traj_file = exec_dir / 'traj.asc'

            if not traj_file.exists():
                raise RuntimeError("Trajectory file not generated")

            return traj_file

        except subprocess.TimeoutExpired:
            raise RuntimeError("Simulation timed out (5 minutes)")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Simulation failed:\n{e.stderr}")
