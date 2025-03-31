import asyncio
import logging
import subprocess
import sys
sys.path.append("/Users/hanbyulkim/MCP/mcp-things3")

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from src.mcp_server_things3.applescript_handler import AppleScriptHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server
server = Server("mcp-server-things3")

class XCallbackURLHandler:
    """Handles x-callback-url execution for Things3."""

    @staticmethod
    def call_url(url: str) -> str:
        """
        Executes an x-callback-url using the 'open' command.
        """
        try:
            result = subprocess.run(
                ['open', url],
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except FileNotFoundError:
            logger.error("'open' command not found")
            raise RuntimeError("Failed to execute x-callback-url: 'open' command not found")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to execute x-callback-url: {e}")
            raise RuntimeError(f"Failed to execute x-callback-url: {e}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available Things3 tools.
    """
    return [
        types.Tool(
            name="view-inbox",
            description="View all todos in the Things3 inbox",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="view-projects",
            description="View all projects in Things3",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="view-areas",
            description="View all areas in Things3",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="view-todos",
            description="View all todos in Things3",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="create-things3-project",
            description="Create a new project in Things3",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "notes": {"type": "string"},
                    "area": {"type": "string"},
                    "when": {"type": "string"},
                    "deadline": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title"]
            },
        ),
        types.Tool(
            name="create-things3-todo",
            description="Create a new to-do in Things3",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "notes": {"type": "string"},
                    "when": {"type": "string"},
                    "deadline": {"type": "string"},
                    "checklist": {"type": "array", "items": {"type": "string"}},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "list": {"type": "string"},
                    "heading": {"type": "string"},
                },
                "required": ["title"]
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    try:
        if name == "view-inbox":
            todos = AppleScriptHandler.get_inbox_tasks() or []
            if not todos:
                return [types.TextContent(type="text", text="No todos found in Things3 inbox.")]

            response = ["Todos in Things3 inbox:"]
            for todo in todos:
                title = (todo.get("title", "Untitled Todo")).strip()
                due_date = todo.get("due_date", "No Due Date")
                when_date = todo.get("when", "No Scheduled Date")
                response.append(f"\n• {title} (Due: {due_date}, When: {when_date})")

            return [types.TextContent(type="text", text="\n".join(response))]

        if name == "view-projects":
            projects = AppleScriptHandler.get_projects() or []
            if not projects:
                return [types.TextContent(type="text", text="No projects found in Things3.")]

            response = ["Projects in Things3:"]
            for project in projects:
                title = (project.get("title", "Untitled Project")).strip()
                response.append(f"\n• {title}")

            return [types.TextContent(type="text", text="\n".join(response))]

        if name == "view-areas":
            areas = AppleScriptHandler.get_areas() or []
            if not areas:
                return [types.TextContent(type="text", text="No projects found in Things3.")]

            response = ["Areas in Things3:"]
            for area in areas:
                title = (area.get("title", "Untitled Area")).strip()
                response.append(f"\n• {title}")

            return [types.TextContent(type="text", text="\n".join(response))]

        if name == "view-todos":
            todos = AppleScriptHandler.get_todays_tasks() or []
            if not todos:
                return [types.TextContent(type="text", text="No todos found in Things3.")]

            response = ["Todos in Things3:"]
            for todo in todos:
                title = (todo.get("title", "Untitled Todo")).strip()
                due_date = todo.get("due_date", "No Due Date")
                when_date = todo.get("when", "No Scheduled Date")
                response.append(f"\n• {title} (Due: {due_date}, When: {when_date})")

            return [types.TextContent(type="text", text="\n".join(response))]

        if name == "create-things3-project":
            if not arguments:
                raise ValueError("Missing arguments")

            # Build the Things3 URL
            base_url = "things:///add-project"
            params = []

            # Required parameters
            params.append(f'title="{arguments["title"]}"')

            # Optional parameters
            if "notes" in arguments:
                params.append(f'notes="{arguments["notes"]}"')
            if "area" in arguments:
                params.append(f'area="{arguments["area"]}"')
            if "when" in arguments:
                params.append(f'when="{arguments["when"]}"')
            if "deadline" in arguments:
                params.append(f'deadline="{arguments["deadline"]}"')
            if "tags" in arguments:
                tags = ",".join(arguments['tags'])
                params.append(f'tags="{tags}"')

            url = f"{base_url}?{'&'.join(params)}"
            logger.info(f"Creating project with URL: {url}")

            try:
                XCallbackURLHandler.call_url(url)
                return [
                    types.TextContent(
                        type="text",
                        text=f"Created project '{arguments['title']}' in Things3",
                    )
                ]
            except Exception as e:
                logger.error(f"Error creating project: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Failed to create project in Things3: {str(e)}",
                    )
                ]

        if name == "create-things3-todo":
            if not arguments:
                raise ValueError("Missing arguments")

            # Build the Things3 URL
            base_url = "things:///add"
            params = []

            # Required parameters
            params.append(f'title="{arguments["title"]}"')

            # Optional parameters
            if "notes" in arguments:
                params.append(f'notes="{arguments["notes"]}"')
            if "when" in arguments:
                params.append(f'when="{arguments["when"]}"')
            if "deadline" in arguments:
                params.append(f'deadline="{arguments["deadline"]}"')
            if "checklist" in arguments:
                checklist = "\n".join(arguments['checklist'])
                params.append(f'checklist="{checklist}"')
            if "tags" in arguments:
                tags = ",".join(arguments['tags'])
                params.append(f'tags="{tags}"')
            if "list" in arguments:
                params.append(f'list="{arguments["list"]}"')
            if "heading" in arguments:
                params.append(f'heading="{arguments["heading"]}"')

            url = f"{base_url}?{'&'.join(params)}"
            logger.info(f"Creating todo with URL: {url}")

            try:
                XCallbackURLHandler.call_url(url)
                return [
                    types.TextContent(
                        type="text",
                        text=f"Created to-do '{arguments['title']}' in Things3",
                    )
                ]
            except Exception as e:
                logger.error(f"Error creating todo: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Failed to create to-do in Things3: {str(e)}",
                    )
                ]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the server."""
    logger.info("Starting Things3 MCP server...")

    # Handle graceful shutdown
    def handle_signal(signum, frame):
        logger.info("Shutting down gracefully...")
        raise SystemExit(0)

    import signal
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Run the server using stdin/stdout streams
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-server-things3",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except SystemExit:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
