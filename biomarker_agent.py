from google.adk import Agent
from google.genai import types
import json

# Placeholder imports - these will be used when the packages are installed
try:
    from pysradb.sraweb import SRAweb
    from Bio import Entrez
    import cellxgene_census
except ImportError:
    # Allow code to load even if dependencies aren't installed yet (for initial setup)
    SRAweb = None
    Entrez = None
    cellxgene_census = None

def search_sra_metadata(query: str) -> str:
    """
    Searches the Sequence Read Archive (SRA) for metadata relevant to the query.
    Useful for finding microbiome or other high-throughput sequencing data.
    """
    try:
        db = SRAweb()
        df = db.search_sra(query, detailed=True)
        if df is None or df.empty:
            return "No results found in SRA."
        # Return top 5 results as a string representation
        return df.head(5).to_string()
    except Exception as e:
        return f"Error searching SRA: {e}"

def search_geo_metadata(query: str) -> str:
    """
    Searches the Gene Expression Omnibus (GEO) for datasets.
    Useful for finding RNA-seq or microarray data.
    """
    try:
        Entrez.email = "your.email@example.com" # Ideally this should be configured
        handle = Entrez.esearch(db="gds", term=query, retmax=5)
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        if not id_list:
            return "No results found in GEO."
            
        results = []
        for geo_id in id_list:
            summary_handle = Entrez.esummary(db="gds", id=geo_id)
            summary_record = Entrez.read(summary_handle)
            summary_handle.close()
            for item in summary_record:
                results.append(f"ID: {item['Id']}, Title: {item['Title']}, Accession: {item['Accession']}")
                
        return "\n".join(results)
    except Exception as e:
        return f"Error searching GEO: {e}"

def search_cellxgene_data(query: str) -> str:
    """
    Searches the CZ Cell x Gene Census for single-cell data.
    """
    try:
        # This is a simplified search. Real usage might involve more complex filtering.
        # For now, we'll just list available datasets or try to filter if the API allows simple text search
        # The census API is more about opening data. We might need to use the metadata to search.
        
        census = cellxgene_census.open_soma()
        datasets_df = census["census_info"]["datasets"].read().concat().to_pandas()
        
        # Simple case-insensitive filter on title or description
        mask = datasets_df['dataset_title'].str.contains(query, case=False, na=False)
        filtered_df = datasets_df[mask]
        
        if filtered_df.empty:
             return "No results found in Cell x Gene Census."
             
        # Return top 5 results
        return filtered_df[['dataset_id', 'dataset_title', 'collection_name']].head(5).to_string()

    except Exception as e:
        return f"Error searching Cell x Gene: {e}"

def create_biomarker_agent(model_name: str) -> Agent:
    return Agent(
        name="biomarker_specialist",
        model=model_name,
        tools=[search_sra_metadata, search_geo_metadata, search_cellxgene_data],
        instruction="""You are a Biomarker Data Specialist.
Your goal is to find high-dimensional biomarker datasets from public repositories.
You have access to:
- SRA/ENA (via search_sra_metadata): Good for raw sequencing data, microbiome, metagenomics.
- GEO (via search_geo_metadata): Good for gene expression data (RNA-seq, microarray).
- CZ Cell x Gene (via search_cellxgene_data): Good for single-cell transcriptomics data.

When asked to find data, choose the most appropriate tool based on the data type requested.
If the user asks for "microbiome" or "sequencing" data, check SRA.
If the user asks for "expression" or "RNA-seq", check GEO.
If the user asks for "single cell", check Cell x Gene.
Always summarize the findings clearly for the user, providing IDs or Accession numbers where possible.
"""
    )
