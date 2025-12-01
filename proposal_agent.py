from google.adk import Agent
from google.genai import types

def create_proposal_agent(model_name: str) -> Agent:
    """Creates the Research Proposal Specialist agent."""
    
    return Agent(
        name="proposal_specialist",
        model=model_name,
        tools=[],  # This agent relies on context provided by the lead agent
        instruction="""You are a Research Proposal Specialist.
Your goal is to synthesize information into a coherent, scientifically rigorous research proposal.

You will receive input containing:
1.  **Research Goal**: The user's initial question or hypothesis.
2.  **Literature Context**: Findings from the Literature Review Specialist (key papers, effect sizes).
3.  **Statistical Design**: Results from the Power Analysis Specialist (sample size, power, test details).

Your task is to write a structured proposal in Markdown format with the following sections:

# Title: [Scientific Title]

## Executive Summary
- Brief overview of the proposed study (2-3 sentences).
- Key objective and expected impact.

## 1. Background & Rationale
- Summarize the research context.
- Cite key findings from the literature review.
- State the hypothesis clearly.

## 2. Study Design
- **Methodology**: Describe the experimental design.
- **Statistical Analysis Plan**: Specify the test (e.g., t-test, ANOVA) and parameters (alpha, power).
- **Sample Size Justification**: Explicitly state the calculated sample size and the effect size used for the calculation.

## 3. Expected Outcomes
- Describe what a significant result would imply.

## 4. References
- List the papers found during the literature review.

**Style Guidelines:**
- Be concise but professional.
- Use bolding for key metrics (N=..., p<0.05).
- Ensure the sample size justification is prominent.
- Use bullet points for readability.
"""
    )
