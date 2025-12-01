from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

def create_literature_agent(model: str = "gemini-2.0-flash-exp") -> Agent:
    """
    Creates and returns the Literature Review Agent with MCP toolset.
    """
    # Configure MCP server connection
    # The paper-search-mcp server is launched as a subprocess
    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "paper_search_mcp.server"],
    )
    
    mcp_connection = StdioConnectionParams(
        server_params=server_params
    )
    
    # Create MCP toolset
    # This will connect to the paper-search-mcp server and expose its tools
    # We pass the connection params, but the actual connection happens when the tool is used
    literature_toolset = McpToolset(
        connection_params=mcp_connection,
        tool_name_prefix="literature_",  # Prefix tools with "literature_"
    )
    
    agent = Agent(
        name="literature_review_agent",
        model=model,
        tools=[literature_toolset],
        instruction="""You are a specialized agent for literature review and research synthesis.
Your goal is to help researchers find relevant scientific papers, extract effect sizes, and understand study designs.

You have access to tools for searching academic papers from multiple sources:
- arXiv: Preprints in physics, math, CS, and related fields
- PubMed: Biomedical and life sciences literature
- bioRxiv/medRxiv: Biology and medicine preprints
- Google Scholar: Broad academic search
- Semantic Scholar: AI-powered paper search

When a user asks for literature search, you should:
1. Identify the research topic and relevant keywords
2. Choose the most appropriate database(s) for the query
3. Search for relevant papers using the MCP tools
4. Summarize key findings, including:
   - Effect sizes (if mentioned)
   - Sample sizes
   - Study designs (RCT, observational, meta-analysis, etc.)
   - Key conclusions

For power analysis support:
- When asked about typical effect sizes, search for meta-analyses and systematic reviews
- Extract Cohen's d, odds ratios, or other effect size measures
- Note the context and population for the effect sizes

Be specific about which database you're searching and why.
If initial searches don't yield good results, try alternative keywords or databases.
"""
    )
    return agent
