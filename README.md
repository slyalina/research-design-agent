# Bioinformatics Research Design Agent

An AI agent that automates statistical power analysis and study design planning for pharmaceutical research and bioinformatics studies. Built with Google's Agent Development Kit (ADK) and R for statistical computations.

## The Pitch

### Problem Statement
Designing robust biomedical research studies is complex and error-prone. Researchers often struggle to:
1.  **Determine appropriate sample sizes**, leading to underpowered studies and wasted resources.
2.  **Navigate vast literature** to find relevant effect sizes and study parameters.
3.  **Integrate statistical rigor** into their initial study proposals.

### Solution
The **Bioinformatics Research Design Agent** is an intelligent orchestration system that acts as a virtual "Research Design Lead". It coordinates specialized sub-agents to automate the critical pre-clinical planning phase:
-   **Lead Agent**: Understands high-level research goals and orchestrates the workflow.
-   **Literature Specialist**: Scours PubMed/arXiv via MCP to find grounded parameters (effect sizes, variance).
-   **Power Analysis Specialist**: Uses R to perform rigorous statistical power calculations and simulations.

### Value Proposition
-   **Scientific Rigor**: Replaces "rule of thumb" guesses with calculation-backed study designs.
-   **Time Efficiency**: Reduces days of literature review and statistical coding to minutes.
-   **Reproducibility**: Generates code-backed analysis that can be audited and reproduced.

## Architecture

```mermaid
graph TD
    User[User] --> Main[Main Agent (Research Lead)]
    Main --> Lit[Literature Specialist]
    Main --> Power[Power Analysis Specialist]
    Lit -- "Effect Sizes & Parameters" --> Main
    Power -- "Sample Size & Power Curves" --> Main
    Main -- "Integrated Research Proposal" --> User
    
    subgraph "External Tools"
        Lit -.-> PubMed[PubMed/ArXiv (MCP)]
        Power -.-> R[R Statistical Engine]
    end
```

## Features

## Features

- **Statistical Power Analysis**: Calculate sample size, power, or effect size for various statistical tests
- **Simulation-Based Power Analysis**: Support for complex designs (mixed effects, clustered data, survival) via R simulations
- **Literature Search**: Search academic papers from arXiv, PubMed, bioRxiv, and other sources via MCP
- **R Integration**: Leverages R's `pwr`, `lme4`, and `simr` packages for robust computations
- **Multi-Agent Architecture**: Main research design agent delegates to specialized sub-agents (Power Analysis + Literature Review)
- **MCP Integration**: Uses Model Context Protocol for seamless literature search capabilities
- **Flexible Test Support**: Currently supports t-tests, with extensibility for ANOVA, correlation, and proportion tests

## Project Structure

```
research-design-agent/
├── main_agent.py              # Entry point and main agent
├── power_analysis_agent.py    # Power analysis sub-agent
├── literature_agent.py        # Literature review sub-agent (MCP)
├── tools/
│   ├── __init__.py
│   └── r_execution.py         # R script execution tool
├── r_scripts/
│   └── power_analysis.R       # R power analysis script
├── requirements.txt           # Python dependencies
└── README.md
```

## Installation

### Prerequisites
- Python 3.10+
- R 4.0+
- Google Cloud credentials or API key for Gemini models

### Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install R packages:
```bash
Rscript -e "install.packages(c('pwr', 'argparser', 'lme4', 'simr', 'survival', 'parallel'), repos='http://cran.us.r-project.org')"
```

3. Set up Google Cloud credentials:
```bash
export GOOGLE_API_KEY="your-api-key"
# OR
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

## Usage

### Running the Agent

```bash
python3 main_agent.py
```

### Example Interactions

**Power Analysis:**
```
User: I need to calculate sample size for a clinical trial comparing two treatments. 
      I expect a medium effect size and want 80% power.

Agent: I'll help you with that power analysis. For a two-sample t-test with:
       - Effect size (Cohen's d): 0.5 (medium)
       - Power: 0.8
       - Significance level: 0.05 (default)
       
       You would need approximately 64 participants in each group (128 total).
```

**Simulation-Based Power Analysis:**
```
User: I'm designing a study with 3 time points per subject. 
      How many subjects do I need to detect a small effect (d=0.3) with 80% power?

Agent: This requires simulation-based power analysis due to repeated measures.
       [Runs simulation with mixed effects model]
       
       Based on 1000 simulations:
       - Sample size: 45 subjects
       - Estimated Power: 0.82 (82.0%)
```

**Literature Search:**
```
User: Find papers about effect sizes in diabetes drug trials.

Agent: I'll search PubMed for relevant papers on diabetes drug trials and effect sizes.
       [Searches using MCP tools]
       
       Here are some relevant papers:
       1. "Meta-analysis of GLP-1 agonists..." - Effect size: Cohen's d = 0.65
       2. "Systematic review of SGLT2 inhibitors..." - Mean difference: -0.8% HbA1c
       ...
```

### Testing

Run the test suite:
```bash
python3 test_r_tool.py           # Test R execution tool
python3 test_agent_flow.py       # Test power analysis agent
python3 test_literature_agent.py # Test literature search MCP integration
```

## Technical Details

### Power Analysis Tool

The `run_power_analysis` function accepts:
- `test_type`: Type of statistical test (t.test, correlation, proportion)
- `effect_size`: Cohen's d, r, or h depending on test type
- `n`: Sample size (leave None to calculate)
- `alpha`: Significance level (default: 0.05)
- `power`: Statistical power (default: 0.8, leave None to calculate)
- `alternative`: Hypothesis type (two.sided, less, greater)
- `type`: For t-tests: two.sample, one.sample, or paired

### R Integration

The agent uses subprocess-based R execution for:
- **Reliability**: Isolated R process prevents memory leaks
- **Flexibility**: Easy to extend with custom R scripts
- **Compatibility**: Works across platforms without rpy2 dependencies

## Future Enhancements

- [ ] Interactive visualization of power curves
- [ ] Integration with study design databases
- [ ] Export to study protocol templates
- [ ] Data pulling for high dimensional biomarker data (e.g. SRA, GEO, ENA)
- [ ] Running of bioinformatics pipelines - Metaphlan2, Humann2, DESeq2, limma, etc.

## License

Apache 2.0 - See LICENSE file

## Acknowledgments

Built for the Google Agents Intensive Capstone Project using the Agent Development Kit (ADK).
