import pytest
from unittest.mock import patch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ai.orchestrator import rag_orchestrator

def test_generate_with_fallback_exhaustion():
    # Test that the backoff logic correctly iterates 3 times and returns None 
    # when an error with 429 or RESOURCE_EXHAUSTED is raised repeatedly.
    with patch("app.ai.orchestrator.concurrent.futures.ThreadPoolExecutor") as mock_executor:
        mock_future = mock_executor.return_value.__enter__.return_value.submit.return_value
        # Simulate API throwing 429 Error continuously
        mock_future.result.side_effect = Exception("429 RESOURCE_EXHAUSTED: Quota Exceeded")
        
        # We patch time.sleep so the test doesn't actually wait 5 + 10 + 20 seconds = 35s.
        with patch("time.sleep") as mock_sleep:
            result, retry_sleep = rag_orchestrator._generate_with_fallback("system instruction", "user prompt")
            
            assert result is None
            assert mock_sleep.call_count == 3
            # The backoff is 2**0 * 5 = 5, 2**1 * 5 = 10, 2**2 * 5 = 20
            # Total retry_sleep should be 35
            assert retry_sleep == 35.0

def test_generate_with_fallback_success_after_retry():
    with patch("app.ai.orchestrator.concurrent.futures.ThreadPoolExecutor") as mock_executor:
        mock_future = mock_executor.return_value.__enter__.return_value.submit.return_value
        
        # We need a mock object that has a `.text` attribute for the successful return
        class MockResponse:
            @property
            def text(self):
                return "Successful text."
        
        # First call raises Exception, second call succeeds
        mock_future.result.side_effect = [Exception("429 RESOURCE_EXHAUSTED"), MockResponse()]
        
        with patch("time.sleep") as mock_sleep:
            result, retry_sleep = rag_orchestrator._generate_with_fallback("system", "user")
            
            assert result == "Successful text."
            assert mock_sleep.call_count == 1
            # Backoff for first attempt (attempt 0): 2**0 * 5 = 5
            assert retry_sleep == 5.0
