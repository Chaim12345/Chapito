#!/usr/bin/env python3
"""
Comprehensive API testing script for Chapito.
Tests all API endpoints with real HTTP requests.
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import aiohttp
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class APITestResult:
    """API test result data class."""
    endpoint: str
    method: str
    success: bool
    status_code: Optional[int] = None
    response_time: float = 0.0
    error: Optional[str] = None
    response_data: Optional[Dict] = None

class ChapitoAPITester:
    """Comprehensive API tester for Chapito."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[APITestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, endpoint: str, 
                           expected_status: int = 200, 
                           data: Optional[Dict] = None,
                           headers: Optional[Dict] = None) -> APITestResult:
        """Test a single API endpoint."""
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status_code = response.status
                    response_data = await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    status_code = response.status
                    response_data = await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            success = status_code == expected_status
            
            result = APITestResult(
                endpoint=endpoint,
                method=method,
                success=success,
                status_code=status_code,
                response_time=response_time,
                response_data=response_data
            )
            
            if not success:
                result.error = f"Expected status {expected_status}, got {status_code}"
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            return APITestResult(
                endpoint=endpoint,
                method=method,
                success=False,
                response_time=response_time,
                error=str(e)
            )
    
    async def test_main_api(self) -> None:
        """Test the main API endpoints."""
        logger.info("🔌 Testing Main API endpoints...")
        
        # Test root endpoint
        result = await self.test_endpoint("GET", "/")
        self.results.append(result)
        logger.info(f"GET /: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test health endpoint
        result = await self.test_endpoint("GET", "/health")
        self.results.append(result)
        logger.info(f"GET /health: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test models endpoint
        result = await self.test_endpoint("GET", "/models")
        self.results.append(result)
        logger.info(f"GET /models: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test chat endpoint with sample data
        chat_data = {
            "messages": [
                {"role": "user", "content": "Hello! What is 2+2?"}
            ],
            "model": "grok",
            "stream": False
        }
        result = await self.test_endpoint("POST", "/chat", data=chat_data, expected_status=200)
        self.results.append(result)
        logger.info(f"POST /chat: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test openapi endpoint
        result = await self.test_endpoint("GET", "/openapi.json")
        self.results.append(result)
        logger.info(f"GET /openapi.json: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
    
    async def test_proxy_api(self) -> None:
        """Test the proxy API endpoints."""
        logger.info("🔌 Testing Proxy API endpoints...")
        
        # Test root endpoint
        result = await self.test_endpoint("GET", "/")
        self.results.append(result)
        logger.info(f"GET /: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test health endpoint
        result = await self.test_endpoint("GET", "/health")
        self.results.append(result)
        logger.info(f"GET /health: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test v1 health endpoint
        result = await self.test_endpoint("GET", "/v1/health")
        self.results.append(result)
        logger.info(f"GET /v1/health: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test models endpoint
        result = await self.test_endpoint("GET", "/models")
        self.results.append(result)
        logger.info(f"GET /models: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test v1 models endpoint
        result = await self.test_endpoint("GET", "/v1/models")
        self.results.append(result)
        logger.info(f"GET /v1/models: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test chat completions endpoint with OpenAI-compatible format
        chat_data = {
            "model": "grok",
            "messages": [
                {"role": "user", "content": "Hello! What is 2+2?"}
            ],
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": False
        }
        result = await self.test_endpoint("POST", "/chat/completions", data=chat_data, expected_status=200)
        self.results.append(result)
        logger.info(f"POST /chat/completions: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test v1 chat completions endpoint
        result = await self.test_endpoint("POST", "/v1/chat/completions", data=chat_data, expected_status=200)
        self.results.append(result)
        logger.info(f"POST /v1/chat/completions: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
        
        # Test openapi endpoint
        result = await self.test_endpoint("GET", "/openapi.json")
        self.results.append(result)
        logger.info(f"GET /openapi.json: {'✅ PASS' if result.success else '❌ FAIL'} ({result.status_code})")
    
    async def test_streaming(self) -> None:
        """Test streaming chat completions."""
        logger.info("🔌 Testing streaming chat completions...")
        
        chat_data = {
            "model": "grok",
            "messages": [
                {"role": "user", "content": "Count from 1 to 5 slowly."}
            ],
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": True
        }
        
        try:
            url = f"{self.base_url}/chat/completions"
            async with self.session.post(url, json=chat_data) as response:
                if response.status == 200:
                    # Check if response is streaming
                    content_type = response.headers.get('content-type', '')
                    if 'text/event-stream' in content_type:
                        logger.info("✅ Streaming response detected")
                        # Read a few lines to verify streaming
                        lines_read = 0
                        async for line in response.content:
                            if line.startswith(b'data: '):
                                lines_read += 1
                                if lines_read >= 3:  # Read at least 3 lines
                                    break
                        
                        result = APITestResult(
                            endpoint="/chat/completions (stream)",
                            method="POST",
                            success=True,
                            status_code=200,
                            response_time=0.0,
                            response_data={"streaming": True, "lines_read": lines_read}
                        )
                    else:
                        result = APITestResult(
                            endpoint="/chat/completions (stream)",
                            method="POST",
                            success=False,
                            status_code=response.status,
                            response_time=0.0,
                            error="Response is not streaming"
                        )
                else:
                    result = APITestResult(
                        endpoint="/chat/completions (stream)",
                        method="POST",
                        success=False,
                        status_code=response.status,
                        response_time=0.0,
                        error=f"Unexpected status code: {response.status}"
                    )
        except Exception as e:
            result = APITestResult(
                endpoint="/chat/completions (stream)",
                method="POST",
                success=False,
                response_time=0.0,
                error=str(e)
            )
        
        self.results.append(result)
        logger.info(f"POST /chat/completions (stream): {'✅ PASS' if result.success else '❌ FAIL'}")
    
    async def run_all_tests(self) -> None:
        """Run all API tests."""
        logger.info("🚀 Starting API Endpoint Tests")
        logger.info("=" * 50)
        
        try:
            # Test main API
            await self.test_main_api()
            
            # Test proxy API
            await self.test_proxy_api()
            
            # Test streaming
            await self.test_streaming()
            
        except Exception as e:
            logger.error(f"💥 Error during API testing: {e}")
        
        self.print_results()
    
    def print_results(self) -> None:
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("📊 API TEST RESULTS SUMMARY")
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
            duration_str = f"{result.response_time:.3f}s"
            status_info = f"({result.status_code})" if result.status_code else ""
            
            logger.info(f"{status} {result.method} {result.endpoint:<30} {status_info} ({duration_str})")
            
            if not result.success and result.error:
                logger.info(f"    Error: {result.error}")
            elif result.response_data:
                logger.info(f"    Response: {str(result.response_data)[:100]}...")
        
        # Summary
        logger.info("\n" + "=" * 50)
        if failed_tests == 0:
            logger.info("🎉 ALL API TESTS PASSED! API is working correctly.")
        else:
            logger.warning(f"⚠️  {failed_tests} API test(s) failed. Please check the errors above.")
        logger.info("=" * 50)
        
        # Return exit code for CI/CD
        return 0 if failed_tests == 0 else 1

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Chapito API endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000",
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Timeout for API requests in seconds (default: 30)")
    
    args = parser.parse_args()
    
    logger.info(f"🔌 Testing API at: {args.base_url}")
    
    async with ChapitoAPITester(args.base_url) as tester:
        try:
            await tester.run_all_tests()
            exit_code = 0 if all(r.success for r in tester.results) else 1
            sys.exit(exit_code)
        except KeyboardInterrupt:
            logger.info("\n🛑 API testing interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"💥 Unexpected error during API testing: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())