#!/usr/bin/env python3
"""
Test script for all Chapito chat providers.
This script tests each chat provider individually to ensure they work correctly.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Import all chat functions
from chapito.deepseek_chat import chat_with_deepseek
from chapito.duckduckgo_chat import chat_with_duckduckgo
from chapito.gemini_chat import chat_with_gemini
from chapito.kimi_chat import chat_with_kimi
from chapito.mistral_chat import chat_with_mistral
from chapito.qwen_chat import chat_with_qwen
from chapito.perplexity_chat import chat_with_perplexity
from chapito.ai_studio_chat import chat_with_ai_studio
from chapito.grok_chat import chat_with_grok
from chapito.anthropic_chat import chat_with_claude
from chapito.openai_chat import chat_with_gpt

# Import tools
from chapito.tools.tools import create_driver, close_browser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data class."""
    provider: str
    success: bool
    response: str
    error: str
    duration: float
    driver_created: bool

class ChatProviderTester:
    """Test all chat providers."""
    
    def __init__(self):
        self.test_message = "Hello! Can you tell me what 2+2 equals?"
        self.expected_keywords = ["4", "four", "2+2", "equals"]
        self.results: List[TestResult] = []
        
    async def test_provider(self, provider_name: str, chat_function, driver) -> TestResult:
        """Test a single chat provider."""
        start_time = time.time()
        success = False
        response = ""
        error = ""
        driver_created = False
        
        try:
            logger.info(f"Testing {provider_name}...")
            
            # Test the chat function
            response = await chat_function(driver, self.test_message)
            
            if response and isinstance(response, str) and len(response.strip()) > 0:
                # Check if response contains expected keywords
                response_lower = response.lower()
                if any(keyword.lower() in response_lower for keyword in self.expected_keywords):
                    success = True
                    logger.info(f"✅ {provider_name}: Success - Response contains expected content")
                else:
                    logger.warning(f"⚠️  {provider_name}: Response received but doesn't contain expected keywords")
                    logger.debug(f"Response: {response[:200]}...")
            else:
                logger.error(f"❌ {provider_name}: No response received")
                
        except Exception as e:
            error = str(e)
            logger.error(f"❌ {provider_name}: Error - {error}")
            
        duration = time.time() - start_time
        driver_created = driver is not None
        
        result = TestResult(
            provider=provider_name,
            success=success,
            response=response[:200] + "..." if len(response) > 200 else response,
            error=error,
            duration=duration,
            driver_created=driver_created
        )
        
        self.results.append(result)
        return result
    
    async def run_all_tests(self) -> None:
        """Run tests for all chat providers."""
        logger.info("🚀 Starting Chat Provider Tests")
        logger.info("=" * 50)
        
        # Define all providers to test
        providers = [
            ("DeepSeek", chat_with_deepseek),
            ("DuckDuckGo", chat_with_duckduckgo),
            ("Gemini", chat_with_gemini),
            ("Kimi", chat_with_kimi),
            ("Mistral", chat_with_mistral),
            ("Qwen", chat_with_qwen),
            ("Perplexity", chat_with_perplexity),
            ("AI Studio", chat_with_ai_studio),
            ("Grok", chat_with_grok),
            ("Anthropic", chat_with_claude),
            ("OpenAI", chat_with_gpt),
        ]
        
        driver = None
        
        try:
            # Create a single driver for all tests
            logger.info("Creating browser driver...")
            driver = await create_driver()
            logger.info("Browser driver created successfully")
            
            # Test each provider
            for provider_name, chat_function in providers:
                await self.test_provider(provider_name, chat_function, driver)
                # Small delay between tests
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to create browser driver: {e}")
        finally:
            # Clean up
            if driver:
                logger.info("Cleaning up browser driver...")
                await close_browser(driver)
                logger.info("Browser driver cleaned up")
    
    def print_results(self) -> None:
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 50)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Successful: {successful_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        logger.info("\n📋 DETAILED RESULTS:")
        logger.info("-" * 50)
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            duration_str = f"{result.duration:.2f}s"
            
            logger.info(f"{status} {result.provider:<15} ({duration_str})")
            
            if not result.success and result.error:
                logger.info(f"    Error: {result.error}")
            elif result.success:
                logger.info(f"    Response: {result.response}")
        
        # Summary
        logger.info("\n" + "=" * 50)
        if failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! All chat providers are working correctly.")
        else:
            logger.warning(f"⚠️  {failed_tests} test(s) failed. Please check the errors above.")
        logger.info("=" * 50)
        
        # Return exit code for CI/CD
        return 0 if failed_tests == 0 else 1

async def main():
    """Main function."""
    tester = ChatProviderTester()
    
    try:
        await tester.run_all_tests()
        exit_code = tester.print_results()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())