#!/usr/bin/env python3
"""
Comprehensive test script for all Chapito chat providers.
Tests both local functionality and API endpoints.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProviderTestResult:
    """Provider test result data class."""
    provider_name: str
    success: bool
    response_length: int
    duration: float
    error: Optional[str] = None
    response_preview: Optional[str] = None

class ChapitoProviderTester:
    """Comprehensive tester for all Chapito chat providers."""
    
    def __init__(self):
        self.results: List[ProviderTestResult] = []
        self.driver = None
        
    async def setup_browser(self) -> bool:
        """Set up browser driver for testing."""
        try:
            from chapito.tools.tools import create_driver
            self.driver = await create_driver()
            if self.driver:
                logger.info("✅ Browser driver created successfully")
                return True
            else:
                logger.warning("⚠️  Failed to create browser driver")
                return False
        except Exception as e:
            logger.warning(f"⚠️  Browser setup failed: {e}")
            return False
    
    async def cleanup_browser(self):
        """Clean up browser driver."""
        if self.driver:
            try:
                from chapito.tools.tools import close_browser
                await close_browser(self.driver)
                logger.info("✅ Browser driver cleaned up")
            except Exception as e:
                logger.warning(f"⚠️  Browser cleanup failed: {e}")
    
    async def test_provider(self, provider_name: str, function_name: str, 
                           test_message: str = "Hello! What is 2+2?") -> ProviderTestResult:
        """Test a single chat provider."""
        start_time = time.time()
        
        try:
            # Import the provider module
            module = __import__(f'chapito.{provider_name}', fromlist=[provider_name])
            chat_function = getattr(module, function_name)
            
            if not self.driver:
                return ProviderTestResult(
                    provider_name=provider_name,
                    success=False,
                    response_length=0,
                    duration=time.time() - start_time,
                    error="No browser driver available"
                )
            
            # Test the chat function
            response = await chat_function(test_message, self.driver)
            
            duration = time.time() - start_time
            
            if response and len(response) > 0:
                result = ProviderTestResult(
                    provider_name=provider_name,
                    success=True,
                    response_length=len(response),
                    duration=duration,
                    response_preview=response[:100] + "..." if len(response) > 100 else response
                )
                logger.info(f"✅ {provider_name}: Success ({len(response)} chars, {duration:.2f}s)")
            else:
                result = ProviderTestResult(
                    provider_name=provider_name,
                    success=False,
                    response_length=0,
                    duration=duration,
                    error="Empty response received"
                )
                logger.warning(f"⚠️  {provider_name}: Empty response ({duration:.2f}s)")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = ProviderTestResult(
                provider_name=provider_name,
                success=False,
                response_length=0,
                duration=duration,
                error=str(e)
            )
            logger.error(f"❌ {provider_name}: Failed ({duration:.2f}s) - {e}")
            return result
    
    async def test_all_providers(self) -> None:
        """Test all chat providers."""
        logger.info("🚀 Starting Chat Provider Tests")
        logger.info("=" * 50)
        
        # Define all providers and their chat functions
        providers = [
            ('deepseek_chat', 'chat_with_deepseek'),
            ('duckduckgo_chat', 'chat_with_duckduckgo'),
            ('gemini_chat', 'chat_with_gemini'),
            ('kimi_chat', 'chat_with_kimi'),
            ('mistral_chat', 'chat_with_mistral'),
            ('qwen_chat', 'chat_with_qwen'),
            ('perplexity_chat', 'chat_with_perplexity'),
            ('ai_studio_chat', 'chat_with_ai_studio'),
            ('grok_chat', 'chat_with_grok'),
            ('anthropic_chat', 'chat_with_claude'),
            ('openai_chat', 'chat_with_gpt')
        ]
        
        # Set up browser if possible
        browser_available = await self.setup_browser()
        
        if not browser_available:
            logger.warning("⚠️  Browser not available, skipping provider tests")
            logger.info("💡 To test providers, ensure a browser is available")
            return
        
        # Test each provider
        for provider_name, function_name in providers:
            logger.info(f"🧪 Testing {provider_name}...")
            result = await self.test_provider(provider_name, function_name)
            self.results.append(result)
            
            # Small delay between tests to avoid overwhelming services
            await asyncio.sleep(2)
        
        # Clean up browser
        await self.cleanup_browser()
        
        self.print_results()
    
    def print_results(self) -> None:
        """Print test results summary."""
        if not self.results:
            logger.info("📊 No provider tests were run")
            return
            
        logger.info("\n" + "=" * 50)
        logger.info("📊 CHAT PROVIDER TEST RESULTS")
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
            response_info = f"({result.response_length} chars)" if result.success else ""
            
            logger.info(f"{status} {result.provider_name:<20} {response_info} ({duration_str})")
            
            if result.success and result.response_preview:
                logger.info(f"    Response: {result.response_preview}")
            elif not result.success and result.error:
                logger.info(f"    Error: {result.error}")
        
        # Summary
        logger.info("\n" + "=" * 50)
        if failed_tests == 0:
            logger.info("🎉 ALL PROVIDER TESTS PASSED! All chat providers are working.")
        else:
            logger.warning(f"⚠️  {failed_tests} provider test(s) failed. Some providers may have issues.")
        logger.info("=" * 50)
        
        # Return exit code for CI/CD
        return 0 if failed_tests == 0 else 1

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test all Chapito chat providers")
    parser.add_argument("--test-message", default="Hello! What is 2+2?",
                       help="Test message to send to providers (default: Hello! What is 2+2?)")
    parser.add_argument("--timeout", type=int, default=300,
                       help="Timeout for tests in seconds (default: 300)")
    
    args = parser.parse_args()
    
    logger.info(f"🧪 Testing with message: {args.test_message}")
    
    tester = ChapitoProviderTester()
    
    try:
        await tester.test_all_providers()
        exit_code = 0 if all(r.success for r in tester.results) else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Provider testing interrupted by user")
        await tester.cleanup_browser()
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error during provider testing: {e}")
        await tester.cleanup_browser()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())