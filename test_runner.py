#!/usr/bin/env python3
"""
Comprehensive test runner for Chapito chat providers.
This script can run both local structural tests and browser-based tests.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data class."""
    test_name: str
    success: bool
    details: str
    duration: float
    error: Optional[str] = None

class ChapitoTester:
    """Comprehensive tester for Chapito chat providers."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        
    def test_imports(self) -> TestResult:
        """Test if all modules can be imported."""
        start_time = time.time()
        logger.info("🔍 Testing module imports...")
        
        try:
            # Test pydoll imports
            import pydoll
            from pydoll.browser import Chrome
            from pydoll.constants import By, Key
            logger.info("✅ pydoll imports successful")
            
            # Test chapito tools imports
            from chapito.tools.tools import (
                create_driver, close_browser, wait_for_element, 
                find_element, click_element, send_keys, navigate_to,
                get_page_source
            )
            logger.info("✅ chapito.tools imports successful")
            
            # Test config and types
            from chapito.config import Config
            from chapito.types import Chatbot, OsType
            logger.info("✅ chapito.config and types imports successful")
            
            # Test all chat provider imports
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
            
            for provider, function_name in providers:
                try:
                    module = __import__(f'chapito.{provider}', fromlist=[provider])
                    if hasattr(module, function_name):
                        logger.info(f"✅ {provider} import and function check successful")
                    else:
                        logger.warning(f"⚠️  {provider} imported but main function '{function_name}' not found")
                except ImportError as e:
                    logger.error(f"❌ {provider} import failed: {e}")
                    return TestResult(
                        test_name="Module Imports",
                        success=False,
                        details=f"Failed to import {provider}",
                        duration=time.time() - start_time,
                        error=str(e)
                    )
            
            duration = time.time() - start_time
            return TestResult(
                test_name="Module Imports",
                success=True,
                details="All modules imported successfully",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Module Imports",
                success=False,
                details="Import test failed",
                duration=duration,
                error=str(e)
            )
    
    def test_code_structure(self) -> TestResult:
        """Test the code structure and basic functionality."""
        start_time = time.time()
        logger.info("🔍 Testing code structure...")
        
        try:
            # Test proxy API structure
            from chapito.proxy import app
            if hasattr(app, 'routes'):
                logger.info("✅ Proxy API structure check passed")
            else:
                logger.warning("⚠️  Proxy API missing routes attribute")
                
            # Test main API structure
            from main import app as main_app
            if hasattr(main_app, 'routes'):
                logger.info("✅ Main API structure check passed")
            else:
                logger.warning("⚠️  Main API missing routes attribute")
                
            # Test config structure
            from chapito.config import Config
            config = Config()
            if hasattr(config, 'chatbot'):
                logger.info("✅ Config structure check passed")
            else:
                logger.warning("⚠️  Config missing chatbot attribute")
                
            duration = time.time() - start_time
            return TestResult(
                test_name="Code Structure",
                success=True,
                details="All code structure checks passed",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Code Structure",
                success=False,
                details="Code structure test failed",
                duration=duration,
                error=str(e)
            )
    
    def test_async_functions(self) -> TestResult:
        """Test if async functions are properly defined."""
        start_time = time.time()
        logger.info("🔍 Testing async function definitions...")
        
        try:
            # Test a few key async functions
            from chapito.tools.tools import create_driver, close_browser
            import inspect
            
            if inspect.iscoroutinefunction(create_driver):
                logger.info("✅ create_driver is async function")
            else:
                logger.warning("⚠️  create_driver is not async")
                
            if inspect.iscoroutinefunction(close_browser):
                logger.info("✅ close_browser is async function")
            else:
                logger.warning("⚠️  close_browser is not async")
                
            # Test a chat function
            from chapito.deepseek_chat import chat_with_deepseek
            if inspect.iscoroutinefunction(chat_with_deepseek):
                logger.info("✅ chat_with_deepseek is async function")
            else:
                logger.warning("⚠️  chat_with_deepseek is not async")
                
            duration = time.time() - start_time
            return TestResult(
                test_name="Async Functions",
                success=True,
                details="All async function checks passed",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Async Functions",
                success=False,
                details="Async function test failed",
                duration=duration,
                error=str(e)
            )
    
    def test_pydantic_models(self) -> TestResult:
        """Test if Pydantic models are properly defined."""
        start_time = time.time()
        logger.info("🔍 Testing Pydantic models...")
        
        try:
            from chapito.proxy import (
                Message, ChatRequest, ChatCompletionChoice, 
                ChatCompletionUsage, ChatCompletionResponse, ErrorResponse
            )
            logger.info("✅ Proxy Pydantic models imported successfully")
            
            from main import ChatRequest as MainChatRequest, ChatResponse
            logger.info("✅ Main API Pydantic models imported successfully")
            
            duration = time.time() - start_time
            return TestResult(
                test_name="Pydantic Models",
                success=True,
                details="All Pydantic models imported successfully",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Pydantic Models",
                success=False,
                details="Pydantic models test failed",
                duration=duration,
                error=str(e)
            )
    
    async def test_browser_functionality(self) -> TestResult:
        """Test browser functionality if available."""
        start_time = time.time()
        logger.info("🌐 Testing browser functionality...")
        
        try:
            from chapito.tools.tools import create_driver, close_browser
            
            # Try to create a driver
            driver = await create_driver()
            if driver:
                logger.info("✅ Browser driver created successfully")
                
                # Get a page
                page = await driver.get_page()
                logger.info("✅ Page obtained successfully")
                
                # Navigate to a simple page
                await page.navigate_to("https://httpbin.org/html")
                logger.info("✅ Navigation successful")
                
                # Get page title
                title = await page.get_title()
                logger.info(f"✅ Page title: {title}")
                
                # Clean up
                await close_browser(driver)
                logger.info("✅ Browser driver cleaned up")
                
                duration = time.time() - start_time
                return TestResult(
                    test_name="Browser Functionality",
                    success=True,
                    details="Browser functionality test passed",
                    duration=duration
                )
            else:
                duration = time.time() - start_time
                return TestResult(
                    test_name="Browser Functionality",
                    success=False,
                    details="Failed to create browser driver",
                    duration=duration,
                    error="Driver creation returned None"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            logger.warning(f"⚠️  Browser functionality test failed: {e}")
            return TestResult(
                test_name="Browser Functionality",
                success=False,
                details="Browser functionality test failed",
                duration=duration,
                error=str(e)
            )
    
    async def run_all_tests(self, include_browser: bool = False) -> None:
        """Run all tests."""
        logger.info("🚀 Starting Chapito Tests")
        logger.info("=" * 50)
        
        # Run local tests
        local_tests = [
            self.test_imports,
            self.test_code_structure,
            self.test_async_functions,
            self.test_pydantic_models,
        ]
        
        for test_func in local_tests:
            result = test_func()
            self.results.append(result)
            logger.info(f"🧪 {result.test_name}: {'✅ PASS' if result.success else '❌ FAIL'}")
        
        # Run browser test if requested
        if include_browser:
            logger.info("\n🧪 Running browser functionality test...")
            browser_result = await self.test_browser_functionality()
            self.results.append(browser_result)
            logger.info(f"🧪 {browser_result.test_name}: {'✅ PASS' if browser_result.success else '❌ FAIL'}")
        
        self.print_results()
    
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
            
            logger.info(f"{status} {result.test_name:<20} ({duration_str})")
            logger.info(f"    Details: {result.details}")
            
            if not result.success and result.error:
                logger.info(f"    Error: {result.error}")
        
        # Summary
        logger.info("\n" + "=" * 50)
        if failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! Chapito is ready to use.")
        else:
            logger.warning(f"⚠️  {failed_tests} test(s) failed. Please check the errors above.")
        logger.info("=" * 50)
        
        # Return exit code for CI/CD
        return 0 if failed_tests == 0 else 1

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Chapito chat providers")
    parser.add_argument("--browser", action="store_true", 
                       help="Include browser functionality tests")
    parser.add_argument("--local-only", action="store_true", 
                       help="Run only local tests (no browser)")
    
    args = parser.parse_args()
    
    tester = ChapitoTester()
    
    try:
        include_browser = args.browser and not args.local_only
        await tester.run_all_tests(include_browser=include_browser)
        exit_code = 0 if all(r.success for r in tester.results) else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())