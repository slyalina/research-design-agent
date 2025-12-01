import os
from google.adk import Agent
from google.adk.tools.function_tool import FunctionTool
from tools.r_execution import RExecutionTool
from tools.simulation_tool import run_simulation_power_analysis

# Initialize the R execution tool
r_tool = RExecutionTool(working_dir=os.getcwd())

def run_power_analysis(test_type: str, effect_size: float = None, n: int = None, alpha: float = 0.05, power: float = None, alternative: str = "two.sided", type: str = "two.sample") -> str:
    """
    Performs a statistical power analysis using R.
    
    Args:
        test_type: Type of test (t.test, anova, correlation, chisq, proportion).
        effect_size: Effect size (Cohen's d, f, r, w, h).
        n: Sample size.
        alpha: Significance level (default 0.05).
        power: Power of the test.
        alternative: Alternative hypothesis (two.sided, less, greater).
        type: Type of t-test (two.sample, one.sample, paired).
        
    Returns:
        The output of the R power analysis.
    """
    script_path = os.path.join("r_scripts", "power_analysis.R")
    args = {
        "test_type": test_type,
        "effect_size": effect_size,
        "n": n,
        "alpha": alpha,
        "power": power,
        "alternative": alternative,
        "type": type
    }
    return r_tool.execute_script(script_path, args)

# Define the tools for the agent
power_analysis_tool = FunctionTool(func=run_power_analysis)
simulation_power_tool = FunctionTool(func=run_simulation_power_analysis)

def create_power_analysis_agent(model: str = "gemini-2.0-flash-exp") -> Agent:
    """
    Creates and returns the Power Analysis Agent.
    """
    agent = Agent(
        name="power_analysis_agent",
        model=model,
        tools=[power_analysis_tool, simulation_power_tool],
        instruction="""You are a specialized agent for statistical power analysis.
Your goal is to help users determine the necessary sample size, power, or effect size for their experiments.
You have access to two tools:
1. `run_power_analysis`: For standard analytical power calculations (t-tests, correlations, etc.).
2. `run_simulation_power_analysis`: For complex designs requiring simulation (mixed effects, clustered data, survival analysis).

When a user asks for a power analysis, you should:
1. Identify the type of statistical test or study design.
2. Decide whether to use analytical methods (simple designs) or simulation (complex designs).
   - Use simulation for: repeated measures, clustered data, non-normal outcomes, survival analysis.
   - Use analytical methods for: simple t-tests, correlations, proportions.
3. Identify the known parameters (effect size, alpha, power, sample size, cluster size, etc.).
4. Call the appropriate tool with the correct arguments.
5. Interpret the result for the user.

If parameters are missing, ask the user for clarification. 
Standard defaults are alpha=0.05 and power=0.8 if not specified, but it's good to confirm.
For effect sizes, if the user doesn't know, explain Cohen's d conventions (small=0.2, medium=0.5, large=0.8 for t-tests).

IMPORTANT: When you run a simulation, the tool will return the path to the generated R script (e.g., "GENERATED_SCRIPT: ..."). 
You MUST explicitly mention this file path in your final response to the user, so they can inspect the code. 
Say something like: "I have generated the R script for this simulation at: [path]".
"""
    )
    return agent
