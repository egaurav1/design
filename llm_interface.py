# src/llm/llm_interface.py
"""Abstract interface for LLM operations"""

from abc import ABC, abstractmethod
from typing import Optional

class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text based on prompt"""
        pass
    
    @abstractmethod
    def summarize(self, text: str, length: str = "medium") -> str:
        """Summarize text"""
        pass
    
    @abstractmethod
    def analyze(self, text: str, question: str) -> str:
        """Analyze text and answer question"""
        pass


# ============================================================================
# src/llm/ollama_client.py
# ============================================================================
"""Local LLM client using Ollama"""

import requests
import json
from typing import Optional
from ..logger import setup_logger
from ..config import settings

logger = setup_logger(__name__)

class OllamaClient(BaseLLMClient):
    """Local LLM client using Ollama"""
    
    def __init__(self, model: str = "mistral:7b", 
                 base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client
        
        Args:
            model: Model name (mistral:7b, llama2, neural-chat, etc.)
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
        
        logger.info(f"🤖 Initializing Ollama client")
        logger.info(f"   Model: {model}")
        logger.info(f"   URL: {base_url}")
        
        # Check if Ollama is running
        try:
            self._check_connection()
            logger.info("✅ Ollama connection successful")
        except Exception as e:
            logger.error(f"❌ Cannot connect to Ollama: {e}")
            logger.error("   Make sure Ollama is running: ollama serve")
            logger.error("   Download model: ollama pull mistral:7b")
            raise
    
    def _check_connection(self):
        """Check if Ollama server is running"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Ollama"""
        
        logger.debug(f"🔄 Generating with {self.model}...")
        
        try:
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": max_tokens,
                },
                timeout=300  # Long timeout for large generations
            )
            response.raise_for_status()
            
            result = response.json()
            text = result.get("response", "").strip()
            
            logger.debug(f"✅ Generation complete ({len(text)} chars)")
            return text
        
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            raise
    
    def summarize(self, text: str, length: str = "medium") -> str:
        """Summarize text"""
        
        length_guidance = {
            "short": "2-3 sentences",
            "medium": "1 paragraph (5-7 sentences)",
            "long": "2-3 paragraphs"
        }
        
        prompt = f"""Please summarize the following text in {length_guidance.get(length, 'a paragraph')}:

TEXT:
{text}

SUMMARY:"""
        
        logger.info(f"📋 Creating {length} summary...")
        return self.generate(prompt, max_tokens=500)
    
    def analyze(self, text: str, question: str) -> str:
        """Analyze text and answer question"""
        
        prompt = f"""Analyze the following text and answer the question.

TEXT:
{text}

QUESTION: {question}

ANSWER:"""
        
        logger.info(f"🔍 Analyzing text...")
        return self.generate(prompt, max_tokens=300)


# ============================================================================
# src/llm/anthropic_client.py
# ============================================================================
"""Claude LLM client using Anthropic API"""

from anthropic import Anthropic as AnthropicAPI
from ..logger import setup_logger
from ..config import settings

logger = setup_logger(__name__)

class ClaudeClient(BaseLLMClient):
    """Claude LLM client using Anthropic API"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 model: str = "claude-opus-4-1-20250805"):
        """
        Initialize Claude client
        
        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            model: Model name
        """
        if not api_key:
            api_key = settings.ANTHROPIC_API_KEY
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        self.client = AnthropicAPI(api_key=api_key)
        self.model = model
        
        logger.info(f"🤖 Initializing Claude client")
        logger.info(f"   Model: {model}")
        logger.info("✅ Claude client ready")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using Claude"""
        
        logger.debug(f"🔄 Generating with {self.model}...")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            text = message.content[0].text.strip()
            logger.debug(f"✅ Generation complete ({len(text)} chars)")
            return text
        
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            raise
    
    def summarize(self, text: str, length: str = "medium") -> str:
        """Summarize text"""
        
        length_guidance = {
            "short": "2-3 sentences",
            "medium": "1 paragraph (5-7 sentences)",
            "long": "2-3 paragraphs"
        }
        
        prompt = f"""Please summarize the following text in {length_guidance.get(length, 'a paragraph')}:

TEXT:
{text}

SUMMARY:"""
        
        logger.info(f"📋 Creating {length} summary with Claude...")
        return self.generate(prompt, max_tokens=500)
    
    def analyze(self, text: str, question: str) -> str:
        """Analyze text and answer question"""
        
        prompt = f"""Analyze the following text and answer the question.

TEXT:
{text}

QUESTION: {question}

ANSWER:"""
        
        logger.info(f"🔍 Analyzing text with Claude...")
        return self.generate(prompt, max_tokens=300)


# ============================================================================
# Factory function
# ============================================================================

def create_llm_client(use_local: bool = True) -> BaseLLMClient:
    """Create LLM client based on configuration"""
    
    logger.info("🤖 Initializing LLM client...")
    
    try:
        if use_local:
            logger.info("   Using local Ollama model (offline)")
            return OllamaClient(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL
            )
        else:
            logger.info("   Using Claude API (requires API key)")
            return ClaudeClient()
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM: {e}")
        
        # Try to fallback
        if use_local:
            logger.warning("Falling back to Claude API...")
            try:
                return ClaudeClient()
            except:
                raise RuntimeError("Could not initialize either Ollama or Claude")
        else:
            raise

if __name__ == "__main__":
    # Test local Ollama
    try:
        client = create_llm_client(use_local=True)
        result = client.summarize("The quick brown fox jumps over the lazy dog.")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
