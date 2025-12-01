from biomarker_agent import search_sra_metadata, search_geo_metadata, search_cellxgene_data
import unittest
from unittest.mock import MagicMock, patch

class TestBiomarkerTools(unittest.TestCase):

    @patch('biomarker_agent.SRAweb')
    def test_search_sra_metadata(self, mock_sraweb):
        # Mock SRAweb instance and search_sra method
        mock_db = MagicMock()
        mock_sraweb.return_value = mock_db
        
        # Mock DataFrame return
        mock_df = MagicMock()
        mock_db.search_sra.return_value = mock_df
        # Ensure df is not empty
        mock_df.empty = False
        
        # Mock head() and to_string()
        mock_head = MagicMock()
        mock_df.head.return_value = mock_head
        mock_head.to_string.return_value = "SRP12345  Test Study"
        
        result = search_sra_metadata("microbiome")
        self.assertIn("SRP12345", result)
        self.assertIn("Test Study", result)

    @patch('biomarker_agent.Entrez')
    def test_search_geo_metadata(self, mock_entrez):
        # Mock Entrez.esearch
        mock_handle_search = MagicMock()
        mock_entrez.esearch.return_value = mock_handle_search
        mock_entrez.read.side_effect = [
            {"IdList": ["12345"]}, # for esearch
            [{"Id": "12345", "Title": "Test GEO Dataset", "Accession": "GSE12345"}] # for esummary
        ]
        
        # Mock Entrez.esummary
        mock_handle_summary = MagicMock()
        mock_entrez.esummary.return_value = mock_handle_summary
        
        result = search_geo_metadata("cancer")
        self.assertIn("GSE12345", result)
        self.assertIn("Test GEO Dataset", result)

    @patch('biomarker_agent.cellxgene_census')
    def test_search_cellxgene_data(self, mock_census):
        # Mock open_soma
        mock_soma = MagicMock()
        mock_census.open_soma.return_value = mock_soma
        
        # Mock dataframe chain: census["census_info"]["datasets"].read().concat().to_pandas()
        mock_datasets = MagicMock()
        
        # Mock dictionary access for census["census_info"]
        # When census["census_info"] is called, it returns a dict-like object (or just a mock)
        # that contains "datasets".
        
        # If we make __getitem__ return a dict, then ["datasets"] works on that dict.
        mock_soma.__getitem__.return_value = {"datasets": mock_datasets}
        
        mock_read = MagicMock()
        mock_datasets.read.return_value = mock_read
        mock_concat = MagicMock()
        mock_read.concat.return_value = mock_concat
        
        # Mock pandas dataframe result
        mock_df = MagicMock()
        mock_concat.to_pandas.return_value = mock_df
        
        # Mock filtering
        mock_filtered_df = MagicMock()
        mock_filtered_df.empty = False
        
        mock_head = MagicMock()
        mock_filtered_df.head.return_value = mock_head
        mock_head.to_string.return_value = "dataset_id  dataset_title  collection_name\n123  Lung Cancer Single Cell  Test Collection"
        
        mock_series = MagicMock()
        mock_series.str.contains.return_value = "some_mask"
        
        def getitem_side_effect(arg):
            if arg == 'dataset_title':
                return mock_series
            else: # this is the mask
                return mock_filtered_df
                
        mock_df.__getitem__.side_effect = getitem_side_effect
        
        mock_filtered_df.__getitem__.return_value = mock_filtered_df 
        
        result = search_cellxgene_data("Lung Cancer")
        self.assertIn("Lung Cancer Single Cell", result)
        self.assertIn("Test Collection", result)

if __name__ == '__main__':
    unittest.main()
