import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from chapito.config import Config
from chapito.tools.tools import create_driver, close_browser
from chapito.openai_chat import chat_with_gpt
from chapito.anthropic_chat import chat_with_claude
from chapito.grok_chat import chat_with_grok

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chapito API", description="Free API access using web-based chatbots")

# Global browser instance
browser = None
page = None


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt"  # Default to GPT
    timeout: Optional[int] = 120


class ChatResponse(BaseModel):
    response: str
    model: str
    success: bool
    error: Optional[str] = None


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


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint that routes to different AI models."""
    try:
        # Ensure browser is initialized
        if not await initialize_browser():
            raise HTTPException(status_code=500, detail="Failed to initialize browser")
        
        # Route to appropriate chatbot based on model
        if request.model.lower() == "gpt":
            response = await chat_with_gpt(page, request.message)
        elif request.model.lower() == "claude":
            response = await chat_with_claude(page, request.message)
        elif request.model.lower() == "grok":
            response = await chat_with_grok(page, request.message)
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if browser and page:
            return {"status": "healthy", "browser": "connected"}
        else:
            return {"status": "unhealthy", "browser": "disconnected"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/models")
async def get_models():
    """Get available AI models."""
    return {
        "models": [
            {"id": "gpt", "name": "OpenAI GPT", "url": "https://chatgpt.com/"},
            {"id": "claude", "name": "Anthropic Claude", "url": "https://claude.ai/"},
            {"id": "grok", "name": "xAI Grok", "url": "https://grok.com/"}
        ]
    }


@app.post("/restart")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
