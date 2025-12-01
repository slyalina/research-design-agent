import unittest
from unittest.mock import patch, MagicMock
import os
from microbiome_agent import run_kneaddata, run_metaphlan2, run_humann2

class TestMicrobiomeAgent(unittest.TestCase):

    @patch('subprocess.run')
    def test_run_kneaddata(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Kneaddata output", returncode=0)
        
        result = run_kneaddata("input.fastq", "output_dir")
        
        self.assertIn("Kneaddata completed successfully", result)
        mock_run.assert_called_with(
            ["kneaddata", "--input", "input.fastq", "--output", "output_dir"],
            capture_output=True, text=True, check=True
        )

    @patch('subprocess.run')
    def test_run_metaphlan2(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock open to avoid actual file creation
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            result = run_metaphlan2("input.fastq", "output.txt")
            
            self.assertIn("MetaPhlAn2 completed successfully", result)
            # Check if subprocess was called with stdout redirection
            # Note: checking stdout arg is tricky with mock_open, but we can check the command list
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0], ["metaphlan2.py", "input.fastq", "--input_type", "fastq", "--nproc", "4"])
            self.assertTrue('stdout' in kwargs)

    @patch('subprocess.run')
    def test_run_humann2(self, mock_run):
        mock_run.return_value = MagicMock(stdout="HUMAnN2 output", returncode=0)
        
        result = run_humann2("input.fastq", "output_dir")
        
        self.assertIn("HUMAnN2 completed successfully", result)
        mock_run.assert_called_with(
            ["humann2", "--input", "input.fastq", "--output", "output_dir"],
            capture_output=True, text=True, check=True
        )

if __name__ == '__main__':
    unittest.main()
