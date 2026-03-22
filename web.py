"""Web wrapper: serves the landing page alongside the MCP endpoint."""
import os

import uvicorn
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

from server import mcp

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


async def landing(request):
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


async def health(request):
    return JSONResponse({"status": "ok"})


# The MCP server's Starlette app handles /mcp internally
mcp_app = mcp.streamable_http_app()

# Add our landing page and health routes to the MCP app
mcp_app.routes.insert(0, Route("/", landing))
mcp_app.routes.insert(1, Route("/health", health))


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(mcp_app, host=host, port=port)
