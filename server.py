"""Standalone MCP server for any CKAN portal.

Connects to a CKAN instance over HTTP and exposes its data through
the Model Context Protocol. Configure via environment variables:

    CKAN_URL        Base URL of the CKAN instance (required)
    CKAN_API_KEY    API key for authenticated access (optional)
    HOST            Listen address (default: 0.0.0.0)
    PORT            Listen port (default: 8000)
"""
import json
import logging
import os

import aiohttp
from mcp.server.fastmcp import FastMCP

log = logging.getLogger(__name__)

CKAN_URL = os.environ.get("CKAN_URL", "").rstrip("/")
CKAN_API_KEY = os.environ.get("CKAN_API_KEY", "")
DATASTORE_MAX_ROWS = int(os.environ.get("DATASTORE_MAX_ROWS", "100"))

mcp = FastMCP(
    "ckan-fynd",
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
)


async def _ckan_action(action, params=None):
    url = f"{CKAN_URL}/api/3/action/{action}"
    headers = {"Content-Type": "application/json"}
    if CKAN_API_KEY:
        headers["Authorization"] = CKAN_API_KEY
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=params or {}, headers=headers) as resp:
            data = await resp.json()
            if not data.get("success"):
                raise Exception(data.get("error", {}).get("message", "CKAN API error"))
            return data["result"]


def _summarise_dataset(ds):
    """Trim a dataset dict to the fields useful for an AI assistant."""
    org = ds.get("organization") or {}
    return {
        "name": ds.get("name"),
        "title": ds.get("title"),
        "notes": (ds.get("notes") or "")[:300],
        "organization": org.get("title"),
        "num_resources": ds.get("num_resources", 0),
        "tags": [t["name"] for t in ds.get("tags", [])],
        "metadata_modified": ds.get("metadata_modified"),
    }


# --- Tools ---

@mcp.tool()
async def dataset_search(
    q: str = "",
    fq: str = "",
    rows: int = 10,
    start: int = 0,
    sort: str = "",
) -> str:
    """Search datasets by keyword, filter, or facet. Returns summaries; use dataset_show for full metadata."""
    params = {k: v for k, v in {"q": q, "fq": fq, "rows": rows, "start": start, "sort": sort}.items() if v}
    result = await _ckan_action("package_search", params)
    return json.dumps({
        "count": result.get("count", 0),
        "results": [_summarise_dataset(ds) for ds in result.get("results", [])],
    }, default=str)


@mcp.tool()
async def dataset_show(id: str) -> str:
    """Get full metadata for a specific dataset by ID or name."""
    result = await _ckan_action("package_show", {"id": id})
    return json.dumps(result, default=str)


@mcp.tool()
async def dataset_list(limit: int = 100, offset: int = 0) -> str:
    """List all dataset names/IDs on the portal."""
    result = await _ckan_action("package_list", {"limit": limit, "offset": offset})
    return json.dumps(result, default=str)


@mcp.tool()
async def datastore_search(
    resource_id: str,
    q: str = "",
    limit: int = 100,
    offset: int = 0,
    sort: str = "",
    fields: str = "",
) -> str:
    """Search records in a DataStore resource."""
    params = {"resource_id": resource_id}
    if q:
        params["q"] = q
    params["limit"] = min(limit, DATASTORE_MAX_ROWS)
    if offset:
        params["offset"] = offset
    if sort:
        params["sort"] = sort
    if fields:
        params["fields"] = fields
    result = await _ckan_action("datastore_search", params)
    return json.dumps(result, default=str)


@mcp.tool()
async def datastore_fields(resource_id: str) -> str:
    """Get field definitions (names, types) for a DataStore resource."""
    result = await _ckan_action("datastore_search", {"resource_id": resource_id, "limit": 0})
    return json.dumps({"fields": result.get("fields", [])}, default=str)


@mcp.tool()
async def resource_show(id: str) -> str:
    """Get metadata for a specific resource within a dataset."""
    result = await _ckan_action("resource_show", {"id": id})
    return json.dumps(result, default=str)


@mcp.tool()
async def organization_list(all_fields: bool = False) -> str:
    """List all organisations on the portal."""
    result = await _ckan_action("organization_list", {"all_fields": all_fields})
    return json.dumps(result, default=str)


@mcp.tool()
async def organization_show(id: str) -> str:
    """Get details for a specific organisation, including its datasets."""
    result = await _ckan_action("organization_show", {"id": id})
    return json.dumps(result, default=str)


@mcp.tool()
async def group_list(all_fields: bool = False) -> str:
    """List all groups (themes/topics) on the portal."""
    result = await _ckan_action("group_list", {"all_fields": all_fields})
    return json.dumps(result, default=str)


@mcp.tool()
async def group_show(id: str) -> str:
    """Get details for a specific group, including its datasets."""
    result = await _ckan_action("group_show", {"id": id})
    return json.dumps(result, default=str)


@mcp.tool()
async def tag_list(query: str = "") -> str:
    """List all tags on the portal."""
    params = {}
    if query:
        params["query"] = query
    result = await _ckan_action("tag_list", params)
    return json.dumps(result, default=str)


if __name__ == "__main__":
    if not CKAN_URL:
        print("Error: CKAN_URL environment variable is required")
        raise SystemExit(1)
    mcp.run(transport="streamable-http")
