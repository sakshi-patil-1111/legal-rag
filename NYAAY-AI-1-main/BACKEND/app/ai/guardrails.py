import logging

logger = logging.getLogger(__name__)

class GuardrailsEngine:
    def validate_input(self, question: str) -> bool:
        """
        Validates the user's input before processing.
        Returns True if valid, False if it violates guardrails.
        """
        if not question or len(question.strip()) < 3:
            logger.warning("Guardrail tripped: Input too short or empty")
            return False
            
        if len(question) > 2000:
            logger.warning("Guardrail tripped: Input too long")
            return False
            
        # Check for prompt injection keywords
        lower_q = question.lower()
        blocklist = [
            "ignore previous instructions", "system prompt", "forget all instructions",
            "you are now", "jailbreak", "override your instructions", "disregard previous",
            "developer mode", "do not follow", "new instructions:"
        ]
        if any(phrase in lower_q for phrase in blocklist):
            logger.warning("Guardrail tripped: Potential prompt injection")
            return False
            
        return True

    def validate_retrieval(self, chunks: list) -> bool:
        """
        Validates that sufficient context was retrieved.
        """
        if not chunks or len(chunks) == 0:
            logger.warning("Guardrail tripped: No relevant chunks retrieved")
            return False
            
        # Optional: check if the top chunk has a high enough confidence/distance
        # For cosine distance, smaller is better. If all distances > threshold, return False
        
        return True
        
    def validate_output(self, response: str) -> bool:
        """
        Validates the LLM output before sending to user.
        """
        if not response:
            return False
            
        return True

guardrails = GuardrailsEngine()
