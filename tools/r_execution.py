import subprocess
import os
from typing import Optional, Dict, Any

class RExecutionTool:
    """
    A tool to execute R scripts or commands.
    """
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir

    def execute_script(self, script_path: str, args: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes an R script with the provided arguments.

        Args:
            script_path: Path to the R script.
            args: Dictionary of command line arguments to pass to the script.
                  Keys should match the argument names expected by the script (without --).

        Returns:
            The stdout output of the R script execution.
        """
        command = ["Rscript", script_path]
        
        if args:
            for key, value in args.items():
                if value is not None:
                    command.append(f"--{key}")
                    command.append(str(value))

        try:
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error executing R script:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    def execute_code(self, r_code: str) -> str:
        """
        Executes a snippet of R code directly.
        
        Args:
            r_code: The R code to execute.
            
        Returns:
            The stdout output.
        """
        try:
            result = subprocess.run(
                ["Rscript", "-e", r_code],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
             return f"Error executing R code:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
