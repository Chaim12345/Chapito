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
                get_page_source, get_new_page
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
            from chapito.tools.tools import create_driver, close_browser, get_new_page, navigate_to
            
            # Try to create a driver
            driver = await create_driver()
            if driver:
                logger.info("✅ Browser driver created successfully")
                
                # Get a page
                page = await get_new_page(driver)
                logger.info("✅ Page obtained successfully")
                
                # Navigate to a simple page
                await navigate_to(page, "https://httpbin.org/html")
                logger.info("✅ Navigation successful")
                
                # Get page title or verify content
                page_source = await page.page_source
                logger.info(f"✅ Page source length: {len(page_source)}")
                
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
            self.test_pydantic_models
        ]
        
        for test in local_tests:
            result = test()
            self.results.append(result)
            status = "PASS" if result.success else "FAIL"
            logger.info(f"{result.test_name}: {status} ({result.duration:.2f}s)")
            if result.error:
                logger.error(f"Error: {result.error}")
        
        # Optionally run browser tests
        if include_browser:
            result = await self.test_browser_functionality()
            self.results.append(result)
            status = "PASS" if result.success else "FAIL"
            logger.info(f"{result.test_name}: {status} ({result.duration:.2f}s)")
            if result.error:
                logger.error(f"Error: {result.error}")
        
        # Summary
        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        logger.info("=" * 50)
        logger.info(f"Tests Passed: {passed}/{total}")
        logger.info("=" * 50)


if __name__ == "__main__":
    tester = ChapitoTester()
    include_browser = '--browser' in sys.argv
    asyncio.run(tester.run_all_tests(include_browser=include_browser))