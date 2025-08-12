import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from chapito.config import Config
from chapito.tools.tools import create_driver, close_browser
from chapito.openai_chat import chat_with_gpt
from chapito.anthropic_chat import chat_with_claude
from chapito.grok_chat import chat_with_grok
from chapito.ai_studio_chat import chat_with_ai_studio
from chapito.deepseek_chat import chat_with_deepseek
from chapito.duckduckgo_chat import chat_with_duckduckgo
from chapito.gemini_chat import chat_with_gemini
from chapito.kimi_chat import chat_with_kimi
from chapito.mistral_chat import chat_with_mistral
from chapito.perplexity_chat import chat_with_perplexity
from chapito.qwen_chat import chat_with_qwen

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chapito API", 
    description="Free API access using web-based chatbots",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global browser instance
browser = None
page = None


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    model: str


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    model: str
    success: bool
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    browser: str


class ModelsResponse(BaseModel):
    """Models list response model."""
    supported_models: List[str]


class RestartResponse(BaseModel):
    """Restart response model."""
    message: str


async def initialize_browser():
    """Initialize the browser and page."""
    global browser, page
    try:
        if browser is None:
            browser = await create_driver()
            page = await browser.get_page()
            logger.info("Browser initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize browser: {e}")
        return False


async def cleanup_browser():
    """Clean up browser resources."""
    global browser, page
    try:
        if browser:
            await close_browser(browser)
            browser = None
            page = None
            logger.info("Browser cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up browser: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize browser on startup."""
    await initialize_browser()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up browser on shutdown."""
    await cleanup_browser()


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint that routes to different AI models."""
    try:
        # Ensure browser is initialized
        if not await initialize_browser():
            raise HTTPException(status_code=500, detail="Failed to initialize browser")
        
        model_lower = request.model.lower()
        
        # Route to appropriate chatbot based on model
        if model_lower == "gpt":
            response = await chat_with_gpt(page, request.message)
        elif model_lower == "claude":
            response = await chat_with_claude(page, request.message)
        elif model_lower == "grok":
            response = await chat_with_grok(page, request.message)
        elif model_lower == "ai_studio":
            response = await chat_with_ai_studio(page, request.message)
        elif model_lower == "deepseek":
            response = await chat_with_deepseek(page, request.message)
        elif model_lower == "duckduckgo":
            response = await chat_with_duckduckgo(page, request.message)
        elif model_lower == "gemini":
            response = await chat_with_gemini(page, request.message)
        elif model_lower == "kimi":
            response = await chat_with_kimi(page, request.message)
        elif model_lower == "mistral":
            response = await chat_with_mistral(page, request.message)
        elif model_lower == "perplexity":
            response = await chat_with_perplexity(page, request.message)
        elif model_lower == "qwen":
            response = await chat_with_qwen(page, request.message)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model: {request.model}")
        
        # Check if response indicates an error
        if response.startswith("Error:"):
            return ChatResponse(
                response="",
                model=request.model,
                success=False,
                error=response
            )
        
        return ChatResponse(
            response=response,
            model=request.model,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        if browser and page:
            return {"status": "healthy", "browser": "connected"}
        else:
            return {"status": "unhealthy", "browser": "disconnected"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/models", response_model=ModelsResponse, tags=["Models"])
async def get_models():
    """Get available AI models."""
    return {
        "supported_models": [
            "gpt",
            "claude", 
            "grok",
            "ai_studio",
            "deepseek",
            "duckduckgo",
            "gemini",
            "kimi",
            "mistral",
            "perplexity",
            "qwen"
        ]
    }


@app.post("/restart", response_model=RestartResponse, tags=["System"])
async def restart_browser():
    """Restart the browser instance."""
    try:
        await cleanup_browser()
        await asyncio.sleep(2)  # Wait a bit before restarting
        success = await initialize_browser()
        if success:
            return {"message": "Browser restarted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to restart browser")
    except Exception as e:
        logger.error(f"Error restarting browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "Chapito API",
        "version": "1.0.0",
        "description": "Free API access using web-based chatbots",
        "endpoints": {
            "chat": "/chat",
            "models": "/models",
            "health": "/health",
            "restart": "/restart",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


@app.get("/openapi.json", tags=["API"])
async def get_openapi_json():
    """Get the OpenAPI specification in JSON format."""
    return app.openapi()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
