from tools.r_execution import RExecutionTool
import os

def test_r_execution():
    tool = RExecutionTool(working_dir=os.getcwd())
    
    # Test 1: Simple R code execution
    print("Test 1: Simple R code execution")
    output = tool.execute_code('print("Hello from R")')
    print(f"Output: {output}")
    if '[1] "Hello from R"' in output:
        print("PASS")
    else:
        print("FAIL")
        
    # Test 2: Power Analysis Script execution (t-test)
    print("\nTest 2: Power Analysis Script execution (t-test)")
    script_path = os.path.join("r_scripts", "power_analysis.R")
    args = {
        "test_type": "t.test",
        "effect_size": 0.5,
        "power": 0.8,
        "alpha": 0.05,
        "type": "two.sample",
        "alternative": "two.sided"
    }
    output = tool.execute_script(script_path, args)
    print(f"Output: {output}")
    if "n = 63.76561" in output:
        print("PASS")
    else:
        print("FAIL")

if __name__ == "__main__":
    test_r_execution()
