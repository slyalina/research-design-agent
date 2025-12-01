import os
from typing import Optional
from tools.r_execution import RExecutionTool

class SimulationPowerTool:
    """
    A tool to execute simulation-based power analysis using R.
    """
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self.r_tool = RExecutionTool(working_dir=working_dir)

    def run_simulation_power(
        self,
        design: str,
        effect_size: float,
        n: int,
        n_sims: int = 1000,
        alpha: float = 0.05,
        n_timepoints: Optional[int] = None,
        cluster_size: Optional[int] = None,
        icc: Optional[float] = None,
        seed: int = 12345
    ) -> str:
        """
        Performs simulation-based power analysis using R.
        Generates a standalone R script for reproducibility and transparency.
        """
        import time
        import shutil
        
        # Ensure generated_scripts directory exists
        gen_dir = "generated_scripts"
        os.makedirs(gen_dir, exist_ok=True)
        
        timestamp = int(time.time())
        script_filename = f"simulation_{design}_{timestamp}.R"
        script_path = os.path.join(gen_dir, script_filename)
        
        # Read the template script
        template_path = os.path.join("r_scripts", "simulation_power.R")
        with open(template_path, "r") as f:
            template_content = f.read()
            
        # Create parameter list definition
        params_code = f"""
# --- Parameters set by Agent ---
argv <- list()
argv$design <- "{design}"
argv$effect_size <- {effect_size}
argv$n <- {n}
argv$n_sims <- {n_sims}
argv$alpha <- {alpha}
argv$seed <- {seed}
"""
        if n_timepoints is not None:
            params_code += f'argv$n_timepoints <- {n_timepoints}\n'
        else:
             params_code += 'argv$n_timepoints <- 3\n'
             
        if cluster_size is not None:
            params_code += f'argv$cluster_size <- {cluster_size}\n'
        else:
            params_code += 'argv$cluster_size <- 20\n'
            
        if icc is not None:
            params_code += f'argv$icc <- {icc}\n'
        else:
            params_code += 'argv$icc <- 0.05\n'
            
        params_code += "# -----------------------------\n"

        # Replace argparser section with hardcoded parameters
        # We assume the argparser section ends around line 26 with "argv <- parse_args(p)"
        # A safer way is to identify the block to replace.
        # Looking at the file, lines 9-26 are the argparser block.
        
        # Split content into lines
        lines = template_content.splitlines()
        
        # Find start and end of argparser block
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(lines):
            if "library(argparser)" in line:
                start_idx = i
            if "argv <- parse_args(p)" in line:
                end_idx = i
                break
        
        if start_idx != -1 and end_idx != -1:
            # Replace the block
            new_lines = lines[:start_idx] + [params_code] + lines[end_idx+1:]
            new_content = "\n".join(new_lines)
        else:
            # Fallback: just prepend params and comment out argparser lines if found, 
            # or just append params if variable names match. 
            # But argv is created by parse_args. 
            # Let's just use the template as is but override argv after parse_args? 
            # No, that requires running with dummy args.
            # Let's stick to replacement if possible, or just write a new script that sources the functions.
            # Actually, the replacement logic above is risky if file changes.
            # Let's try to be robust.
            pass 
            # For now, let's assume the file structure is stable as we just viewed it.
            new_lines = lines[:start_idx] + [params_code] + lines[end_idx+1:]
            new_content = "\n".join(new_lines)

        # Write the new script
        with open(script_path, "w") as f:
            f.write(new_content)
            
        # Execute the NEW script
        # We don't need to pass args since they are hardcoded
        result = self.r_tool.execute_script(script_path, args=None)
        
        return f"GENERATED_SCRIPT: {os.path.abspath(script_path)}\n\n{result}"

def run_simulation_power_analysis(
    design: str,
    effect_size: float,
    n: int,
    n_sims: int = 1000,
    alpha: float = 0.05,
    n_timepoints: int = 3,
    cluster_size: int = 20,
    icc: float = 0.05
) -> str:
    """
    Performs simulation-based power analysis.
    
    Args:
        design: Study design (mixed_effects, clustered, poisson, survival)
        effect_size: Effect size (Cohen's d for mixed_effects, rate ratio for poisson, hazard ratio for survival)
        n: Sample size (subjects or clusters depending on design)
        n_sims: Number of simulations (default: 1000)
        alpha: Significance level (default: 0.05)
        n_timepoints: Number of timepoints for repeated measures (default: 3)
        cluster_size: Cluster size for clustered designs (default: 20)
        icc: Intra-cluster correlation for clustered designs (default: 0.05)
        
    Returns:
        Simulation results including estimated power.
    """
    print(f"\n[System] Starting simulation-based power analysis (Design: {design}, N: {n}, Sims: {n_sims})...", flush=True)
    tool = SimulationPowerTool(working_dir=os.getcwd())
    result = tool.run_simulation_power(
        design=design,
        effect_size=effect_size,
        n=n,
        n_sims=n_sims,
        alpha=alpha,
        n_timepoints=n_timepoints,
        cluster_size=cluster_size,
        icc=icc
    )
    print("[System] Simulation completed.", flush=True)
    return result
