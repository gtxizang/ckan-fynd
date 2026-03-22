# ckan-fynd

Standalone MCP server for any CKAN portal. Connects to a CKAN instance over
HTTP and exposes datasets, DataStore queries, and portal metadata to AI
assistants through the [Model Context Protocol](https://modelcontextprotocol.io/).

For CKAN 2.10+ portals, consider [ckanext-fynd](https://github.com/gtxizang/ckanext-fynd)
instead — a CKAN extension that serves MCP from inside CKAN with native auth.

## Quick Start

```bash
docker compose up -d
```

By default, connects to [data.gov.ie](https://data.gov.ie). To point at a
different portal:

```bash
CKAN_URL=https://your-ckan-portal.com docker compose up -d
```

The landing page is at `http://localhost:8000` and the MCP endpoint is at
`http://localhost:8000/mcp`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CKAN_URL` | `https://data.gov.ie` | Base URL of the CKAN instance |
| `CKAN_API_KEY` | *(none)* | API key for authenticated access |
| `DATASTORE_MAX_ROWS` | `100` | Max rows returned from DataStore queries |
| `PORT` | `8000` | Listen port |

## Available Tools

| Tool | Description |
|------|-------------|
| `dataset_search` | Search datasets by keyword, filter, or facet |
| `dataset_show` | Get full metadata for a specific dataset |
| `dataset_list` | List all dataset names/IDs |
| `datastore_search` | Query records in a DataStore resource |
| `datastore_fields` | Get field definitions for a DataStore resource |
| `resource_show` | Get metadata for a specific resource |
| `organization_list` | List all organisations |
| `organization_show` | Get organisation details |
| `group_list` | List all groups/themes |
| `group_show` | Get group details |
| `tag_list` | List all tags |

## Deployment

For production behind a reverse proxy:

```bash
docker compose up -d --build
```

The health check endpoint is at `GET /health`.

## License

AGPL-3.0
