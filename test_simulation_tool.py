import os
import sys
from tools.simulation_tool import run_simulation_power_analysis

def test_simulation_tool():
    """
    Test the simulation power analysis tool.
    """
    print("Testing Simulation Power Analysis Tool...")
    
    # Test 1: Mixed Effects Model Simulation
    print("\nTest 1: Mixed Effects Model (Repeated Measures)")
    # Small number of sims for testing speed
    try:
        result = run_simulation_power_analysis(
            design="mixed_effects",
            effect_size=0.5,
            n=30,
            n_sims=10, 
            alpha=0.05,
            n_timepoints=3
        )
        print("Result:")
        print(result)
        
        if "Estimated Power" in result:
            print("PASS: Mixed effects simulation returned power estimate")
        else:
            print("FAIL: Mixed effects simulation failed to return power estimate")
            
    except Exception as e:
        print(f"FAIL: Error running mixed effects simulation: {e}")

    # Test 2: Clustered Data Simulation
    print("\nTest 2: Clustered Data")
    try:
        result = run_simulation_power_analysis(
            design="clustered",
            effect_size=0.4,
            n=20, # 20 clusters
            n_sims=10,
            alpha=0.05,
            cluster_size=10,
            icc=0.05
        )
        print("Result:")
        print(result)
        
        if "Estimated Power" in result:
            print("PASS: Clustered simulation returned power estimate")
        else:
            print("FAIL: Clustered simulation failed to return power estimate")
            
    except Exception as e:
        print(f"FAIL: Error running clustered simulation: {e}")

if __name__ == "__main__":
    test_simulation_tool()
