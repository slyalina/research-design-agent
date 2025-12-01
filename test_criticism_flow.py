import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from google.genai import types
from main_agent import main

class TestCriticismFlow(unittest.TestCase):
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('main_agent.Runner')
    @patch('main_agent.InMemorySessionService')
    def test_criticism_workflow(self, mock_session_service_cls, mock_runner, mock_print, mock_input):
        # Setup mocks
        mock_input.side_effect = ["Create a research proposal for a study on caffeine and sleep", "exit"]
        
        # Mock session service instance and async create_session
        mock_session_service = mock_session_service_cls.return_value
        mock_session_service.create_session = AsyncMock()
        
        # Mock runner instances
        mock_power_runner = MagicMock()
        mock_lit_runner = MagicMock()
        mock_proposal_runner = MagicMock()
        mock_biomarker_runner = MagicMock()
        mock_criticism_runner = MagicMock()
        mock_main_runner = MagicMock()
        
        # Configure runner.run to return dummy events
        mock_lit_runner.run.return_value = [types.Part(text="Literature context found.")]
        mock_power_runner.run.return_value = [types.Part(text="Power analysis calculated.")]
        mock_proposal_runner.run.return_value = [types.Part(text="# Research Proposal\n\nTitle: Caffeine and Sleep...")]
        mock_criticism_runner.run.return_value = [types.Part(text="## Critical Assessment\n\nMethodologically sound.")]
        
        # Mock Runner constructor to return specific mocks based on agent name
        # Order in main: Power, Literature, Proposal, Biomarker, Criticism, Main
        mock_runner.side_effect = [
            mock_power_runner, 
            mock_lit_runner, 
            mock_proposal_runner, 
            mock_biomarker_runner,
            mock_criticism_runner, 
            mock_main_runner
        ]

        # Run main
        try:
            main()
        except StopIteration:
            pass

        # Verify flow
        # 1. Check if "proposal" keyword triggered the workflow
        print_calls = [str(call) for call in mock_print.mock_calls]
        workflow_started = any("Initiating Research Proposal Generation Workflow" in call for call in print_calls)
        self.assertTrue(workflow_started, "Proposal workflow did not start")

        # 2. Verify Literature Agent was called
        self.assertTrue(mock_lit_runner.run.called, "Literature agent was not called")
        
        # 3. Verify Power Agent was called
        self.assertTrue(mock_power_runner.run.called, "Power agent was not called")
        
        # 4. Verify Proposal Agent was called
        self.assertTrue(mock_proposal_runner.run.called, "Proposal agent was not called")

        # 5. Verify Criticism Agent was called
        self.assertTrue(mock_criticism_runner.run.called, "Criticism agent was not called")
        
        # Check if the proposal text was passed to the criticism agent
        # We can check the arguments passed to mock_criticism_runner.run
        call_args = mock_criticism_runner.run.call_args
        self.assertIsNotNone(call_args, "Criticism runner was not called")
        
        # The 'new_message' argument should contain the proposal text
        kwargs = call_args.kwargs
        new_message = kwargs.get('new_message')
        self.assertIsNotNone(new_message, "new_message not passed to criticism runner")
        
        # Check if the message contains the proposal text we mocked
        message_text = new_message.parts[0].text
        self.assertIn("Caffeine and Sleep", message_text, "Proposal text not passed to criticism agent")

if __name__ == '__main__':
    unittest.main()
