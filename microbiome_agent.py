import subprocess
import os
from google.adk import Agent
from google.genai import types

def run_kneaddata(input_file: str, output_dir: str, reference_db: str = None) -> str:
    """
    Runs kneaddata on the input sequencing file for quality control and host decontamination.
    
    Args:
        input_file: Path to the input FASTQ file.
        output_dir: Directory to save the output.
        reference_db: Path to the reference database for decontamination (optional).
        
    Returns:
        A message indicating success or failure, including the output directory.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        command = ["kneaddata", "--input", input_file, "--output", output_dir]
        if reference_db:
            command.extend(["--reference-db", reference_db])
            
        # Run the command
        # Note: In a real environment, we would check for the executable.
        # Here we assume it's in the PATH.
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        return f"Kneaddata completed successfully. Output stored in {output_dir}. Stdout: {result.stdout[:200]}..."
    except subprocess.CalledProcessError as e:
        return f"Error running kneaddata: {e.stderr}"
    except FileNotFoundError:
        return "Error: kneaddata executable not found in PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def run_metaphlan2(input_file: str, output_file: str, input_type: str = "fastq") -> str:
    """
    Runs MetaPhlAn2 on the input file for taxonomic profiling.
    
    Args:
        input_file: Path to the input file (FASTQ or Bowtie2 output).
        output_file: Path to save the output profile.
        input_type: Type of input file ('fastq', 'bowtie2out', 'sam').
        
    Returns:
        A message indicating success or failure.
    """
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        command = ["metaphlan2.py", input_file, "--input_type", input_type, "--nproc", "4"]
        
        # Capture output to file as metaphlan writes to stdout by default usually, 
        # but modern versions might have -o. We'll use stdout redirection pattern for safety if wrapper handles it,
        # but here we'll assume the command line tool accepts output file redirection or we handle it.
        # Actually metaphlan2 usually takes input and writes to stdout, so we redirect.
        
        with open(output_file, "w") as outfile:
            result = subprocess.run(command, stdout=outfile, stderr=subprocess.PIPE, text=True, check=True)
            
        return f"MetaPhlAn2 completed successfully. Profile saved to {output_file}."
    except subprocess.CalledProcessError as e:
        return f"Error running MetaPhlAn2: {e.stderr}"
    except FileNotFoundError:
        return "Error: metaphlan2.py executable not found in PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def run_humann2(input_file: str, output_dir: str) -> str:
    """
    Runs HUMAnN2 on the input file for functional profiling.
    
    Args:
        input_file: Path to the input file (FASTQ or taxonomic profile).
        output_dir: Directory to save the output.
        
    Returns:
        A message indicating success or failure.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        command = ["humann2", "--input", input_file, "--output", output_dir]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        return f"HUMAnN2 completed successfully. Output stored in {output_dir}. Stdout: {result.stdout[:200]}..."
    except subprocess.CalledProcessError as e:
        return f"Error running HUMAnN2: {e.stderr}"
    except FileNotFoundError:
        return "Error: humann2 executable not found in PATH."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def create_microbiome_agent(model_name: str) -> Agent:
    return Agent(
        name="microbiome_tool_runner",
        model=model_name,
        tools=[run_kneaddata, run_metaphlan2, run_humann2],
        instruction="""You are a Microbiome Tool Runner.
Your goal is to execute standard bioinformatics tools for microbiome data processing.
You have access to:
- `kneaddata`: For quality control and host decontamination of raw sequencing data.
- `metaphlan2`: For taxonomic profiling of microbial communities.
- `humann2`: For functional profiling (pathways and gene families).

When a user asks to process data:
1. Identify which step of the pipeline is needed.
   - QC/Cleaning -> kneaddata
   - Taxonomy/Who is there? -> metaphlan2
   - Function/What are they doing? -> humann2
2. Ask for necessary file paths if not provided.
3. Execute the tool and report the results.

If the user wants to run a full pipeline, you can run them sequentially: kneaddata -> metaphlan2 -> humann2.
"""
    )
