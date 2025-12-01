import os
import sys
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from power_analysis_agent import create_power_analysis_agent
from literature_agent import create_literature_agent
from proposal_agent import create_proposal_agent
from biomarker_agent import create_biomarker_agent
from criticism_agent import create_criticism_agent
from microbiome_agent import create_microbiome_agent

def main():
    # Initialize the model name
    model_name = "gemini-2.5-flash-lite"

    # Create the sub-agents
    power_agent = create_power_analysis_agent(model_name)
    literature_agent = create_literature_agent(model_name)
    proposal_agent = create_proposal_agent(model_name)
    biomarker_agent = create_biomarker_agent(model_name)
    criticism_agent = create_criticism_agent(model_name)
    microbiome_agent = create_microbiome_agent(model_name)

    # Create the main agent
    main_agent = Agent(
        name="research_design_lead",
        model=model_name,
        tools=[], 
        instruction="""You are a Bioinformatics Research Design Lead.
Your goal is to assist researchers in designing robust experiments.
You can help with:
- Defining research questions.
- Selecting appropriate statistical tests.
- Performing power analysis (by delegating to the Power Analysis Specialist).
- Searching scientific literature (by delegating to the Literature Review Specialist).
- Finding public biomarker datasets (by delegating to the Biomarker Data Specialist).
- Processing microbiome data (by delegating to the Microbiome Tool Runner).
- Generating full research proposals (by orchestrating all specialists).

If the user needs a power analysis or sample size calculation, delegate the task to the Power Analysis Specialist.
If the user needs to search for papers, effect sizes, or study designs in the literature, delegate to the Literature Review Specialist.
If the user needs to find public datasets (SRA, GEO, Cell x Gene), delegate to the Biomarker Data Specialist.
If the user needs to run kneaddata, metaphlan2, humann2, or process microbiome sequencing data, delegate to the Microbiome Tool Runner.
If the user asks for a "proposal", "protocol", or "study design", initiate the proposal generation workflow.
"""
    )
    
    # Create session service and runners
    # IMPORTANT: All runners must use the same app_name to share the same session
    app_name = "research_design_app"
    session_service = InMemorySessionService()
    power_runner = Runner(app_name=app_name, agent=power_agent, session_service=session_service)
    literature_runner = Runner(app_name=app_name, agent=literature_agent, session_service=session_service)
    proposal_runner = Runner(app_name=app_name, agent=proposal_agent, session_service=session_service)
    biomarker_runner = Runner(app_name=app_name, agent=biomarker_agent, session_service=session_service)
    criticism_runner = Runner(app_name=app_name, agent=criticism_agent, session_service=session_service)
    microbiome_runner = Runner(app_name=app_name, agent=microbiome_agent, session_service=session_service)
    main_runner = Runner(app_name=app_name, agent=main_agent, session_service=session_service)
    
    print("Bioinformatics Research Design Agent Initialized.")
    print("Type 'exit' to quit.")
    
    # Create sessions for each runner
    user_id = "user_1"
    session_id = "session_1"
    
    # Create a session in the session service using async create_session
    import asyncio
    asyncio.run(session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    ))
    
    # Simple REPL loop
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # Create Content object from user input
            user_content = types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )
            
            # Simple routing logic
            user_lower = user_input.lower()
            
            if "proposal" in user_lower or "protocol" in user_lower:
                # Orchestration Mode: Proposal Generation
                print(f"Agent (Lead): Initiating Research Proposal Generation Workflow...", flush=True)
                
                # Step 1: Literature Search (Context Gathering)
                print(f"\n[Step 1/3] Agent (Literature Specialist): Searching for context...", flush=True)
                lit_context = ""
                try:
                    # Create a specific prompt for the literature agent based on the user's request
                    lit_prompt = types.Content(role="user", parts=[types.Part(text=f"Find key papers and effect sizes relevant to: {user_input}")])
                    for event in literature_runner.run(user_id=user_id, session_id=session_id, new_message=lit_prompt):
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                            lit_context += event.text
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                                    lit_context += part.text
                except Exception as e:
                    print(f"\nWarning: Literature search had issues: {e}")

                # Step 2: Power Analysis (Statistical Design)
                print(f"\n\n[Step 2/3] Agent (Power Specialist): Calculating sample size...", flush=True)
                power_context = ""
                try:
                    # Create a prompt that asks for a standard power analysis based on the user's input
                    # We append a hint to extract parameters from the literature if possible, but for now we'll rely on the user's input or defaults
                    power_prompt = types.Content(role="user", parts=[types.Part(text=f"Perform a power analysis for this study design: {user_input}. If effect size is unknown, assume a medium effect size.")])
                    for event in power_runner.run(user_id=user_id, session_id=session_id, new_message=power_prompt):
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                            power_context += event.text
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                                    power_context += part.text
                except Exception as e:
                    print(f"\nWarning: Power analysis had issues: {e}")

                # Step 2.5: Human-in-the-Loop Feedback
                print(f"\n[Step 2.5/4] Human-in-the-Loop: Reviewing Power Analysis...", flush=True)
                print("-" * 40)
                print(f"Current Power Analysis Context:\n{power_context}")
                print("-" * 40)
                
                print("\nAgent (Lead): Do you want to proceed with these parameters? (yes/no/adjust)")
                feedback = input("User (Feedback): ").strip().lower()
                
                if feedback not in ["yes", "y", "proceed"]:
                    print(f"\nAgent (Lead): Understood. Please provide your feedback or adjustments (e.g., 'Increase power to 0.9' or 'Change effect size to 0.8').")
                    adjustment_input = input("User (Adjustments): ")
                    
                    print(f"\nAgent (Power Specialist): Re-calculating based on feedback...", flush=True)
                    try:
                        # Re-run power analysis with the new feedback
                        # We create a new prompt that includes the previous context and the new adjustment
                        adjustment_prompt = types.Content(role="user", parts=[types.Part(text=f"The user wants to adjust the previous power analysis. Feedback: {adjustment_input}. Please re-calculate.")])
                        
                        # Clear previous context to avoid duplication if we want, or just append. 
                        # For a cleaner proposal, let's reset power_context and capture the new result.
                        power_context = "" 
                        for event in power_runner.run(user_id=user_id, session_id=session_id, new_message=adjustment_prompt):
                            if hasattr(event, 'text'):
                                print(event.text, end="", flush=True)
                                power_context += event.text
                            elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                                for part in event.content.parts:
                                    if hasattr(part, 'text'):
                                        print(part.text, end="", flush=True)
                                        power_context += part.text
                    except Exception as e:
                        print(f"\nWarning: Re-calculation had issues: {e}")

                # Step 3: Proposal Synthesis
                print(f"\n\n[Step 3/4] Agent (Proposal Specialist): Synthesizing proposal...", flush=True)
                proposal_text = ""
                try:
                    # Combine contexts into a prompt for the proposal agent
                    synthesis_prompt = f"""
                    Please generate a research proposal based on the following:
                    
                    USER REQUEST: {user_input}
                    
                    LITERATURE FINDINGS:
                    {lit_context}
                    
                    POWER ANALYSIS RESULTS:
                    {power_context}
                    """
                    proposal_message = types.Content(role="user", parts=[types.Part(text=synthesis_prompt)])
                    
                    for event in proposal_runner.run(user_id=user_id, session_id=session_id, new_message=proposal_message):
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                            proposal_text += event.text
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                                    proposal_text += part.text
                except Exception as e:
                    print(f"\nError generating proposal: {e}")

                # Step 4: Methodological Review (Criticism)
                print(f"\n\n[Step 4/4] Agent (Methodological Reviewer): Critiquing proposal...", flush=True)
                try:
                    criticism_prompt = f"""
                    Please review the following research proposal for statistical rigor, bias, and methodological issues:
                    
                    {proposal_text}
                    """
                    criticism_message = types.Content(role="user", parts=[types.Part(text=criticism_prompt)])
                    
                    for event in criticism_runner.run(user_id=user_id, session_id=session_id, new_message=criticism_message):
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                except Exception as e:
                    print(f"\nError in methodological review: {e}")
                
                print("\n\n[Workflow Complete]")


            elif "power" in user_lower or "sample size" in user_lower:
                # Delegate to power agent
                print(f"Agent (Power Specialist): [Delegating...]", end="", flush=True)
                print(f"\nDEBUG: Starting power_runner.run...", file=sys.stderr)
                try:
                    for event in power_runner.run(user_id=user_id, session_id=session_id, new_message=user_content):
                        print(f"\nDEBUG: Received event from power_runner: {type(event)}", file=sys.stderr)
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                        elif hasattr(event, 'parts'):
                             for part in event.parts:
                                 if hasattr(part, 'text'):
                                     print(part.text, end="", flush=True)
                    print(f"\nDEBUG: power_runner.run completed.", file=sys.stderr)
                except Exception as e:
                    print(f"\nDEBUG: Error in power_runner.run: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                print()
            elif any(keyword in user_lower for keyword in ["paper", "literature", "search", "study", "pubmed", "arxiv", "effect size"]):
                # Delegate to literature agent
                print(f"Agent (Literature Specialist): ", end="", flush=True)
                try:
                    for event in literature_runner.run(user_id=user_id, session_id=session_id, new_message=user_content):
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                        elif hasattr(event, 'parts'):
                             for part in event.parts:
                                 if hasattr(part, 'text'):
                                     print(part.text, end="", flush=True)
                except RuntimeError as e:
                    if "Attempted to exit cancel scope" in str(e):
                        # Ignore known MCP cleanup error
                        pass
                    else:
                        raise e
                print()
            elif any(keyword in user_lower for keyword in ["dataset", "sra", "ena", "geo", "microbiome data", "rnaseq data", "single cell", "cellxgene", "expression atlas"]):
                # Delegate to biomarker agent
                print(f"Agent (Biomarker Specialist): ", end="", flush=True)
                try:
                    for event in biomarker_runner.run(user_id=user_id, session_id=session_id, new_message=user_content):
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                        elif hasattr(event, 'parts'):
                             for part in event.parts:
                                 if hasattr(part, 'text'):
                                     print(part.text, end="", flush=True)
                except Exception as e:
                    print(f"\nError in biomarker search: {e}")
                print()
            elif any(keyword in user_lower for keyword in ["kneaddata", "metaphlan", "humann", "process microbiome", "run pipeline"]):
                # Delegate to microbiome agent
                print(f"Agent (Microbiome Tool Runner): ", end="", flush=True)
                try:
                    for event in microbiome_runner.run(user_id=user_id, session_id=session_id, new_message=user_content):
                        if hasattr(event, 'text'):
                            print(event.text, end="", flush=True)
                        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text'):
                                    print(part.text, end="", flush=True)
                        elif hasattr(event, 'parts'):
                             for part in event.parts:
                                 if hasattr(part, 'text'):
                                     print(part.text, end="", flush=True)
                except Exception as e:
                    print(f"\nError in microbiome processing: {e}")
                print()
            else:
                # Handle with main agent
                print(f"Agent (Lead): ", end="", flush=True)
                for event in main_runner.run(user_id=user_id, session_id=session_id, new_message=user_content):
                    if hasattr(event, 'text'):
                        print(event.text, end="", flush=True)
                    elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text'):
                                print(part.text, end="", flush=True)
                    elif hasattr(event, 'parts'):
                         for part in event.parts:
                             if hasattr(part, 'text'):
                                 print(part.text, end="", flush=True)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
