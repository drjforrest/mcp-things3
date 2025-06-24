import asyncio
import logging
import subprocess
import sys
from urllib.parse import quote

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Handle both relative and absolute imports
try:
    from .applescript_handler import AppleScriptHandler
except ImportError:
    from applescript_handler import AppleScriptHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server
server = Server("mcp-server-things3")

class XCallbackURLHandler:
    """Handles x-callback-url execution for Things3."""

    @staticmethod
    def build_url(base_url: str, params: dict) -> str:
        """
        Builds a properly encoded x-callback-url.
        """
        if not params:
            return base_url
        
        encoded_params = []
        for key, value in params.items():
            if value is not None:
                # Handle list values (like tags)
                if isinstance(value, list):
                    value = ",".join(str(v) for v in value)
                # Use quote() instead of quote_plus() - Things3 prefers %20 over +
                encoded_params.append(f"{key}={quote(str(value), safe='')}")
        
        return f"{base_url}?{'&'.join(encoded_params)}"

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
    
    @staticmethod
    def validate_things3_available() -> bool:
        """
        Check if Things3 is available on the system.
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to exists application process "Things3"'],
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == "true"
        except subprocess.CalledProcessError:
            return False

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
        ),
        types.Tool(
            name="complete-things3-todo",
            description="Mark a Things3 todo as completed by searching for its title",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title or partial title of the todo to complete"},
                },
                "required": ["title"]
            },
        ),
        types.Tool(
            name="search-things3-todos",
            description="Search for todos in Things3 by title or content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term to look for in todo titles and notes"},
                },
                "required": ["query"]
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
            # Validate Things3 is accessible
            if not AppleScriptHandler.validate_things3_access():
                return [types.TextContent(type="text", text="Things3 is not available. Please ensure Things3 is installed and running.")]
            
            try:
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
            except Exception as e:
                logger.error(f"Error retrieving inbox tasks: {e}")
                return [types.TextContent(type="text", text=f"Failed to retrieve inbox tasks: {str(e)}")]

        if name == "view-projects":
            # Validate Things3 is accessible
            if not AppleScriptHandler.validate_things3_access():
                return [types.TextContent(type="text", text="Things3 is not available. Please ensure Things3 is installed and running.")]
            
            try:
                projects = AppleScriptHandler.get_projects() or []
                if not projects:
                    return [types.TextContent(type="text", text="No projects found in Things3.")]

                response = ["Projects in Things3:"]
                for project in projects:
                    title = (project.get("title", "Untitled Project")).strip()
                    response.append(f"\n• {title}")

                return [types.TextContent(type="text", text="\n".join(response))]
            except Exception as e:
                logger.error(f"Error retrieving projects: {e}")
                return [types.TextContent(type="text", text=f"Failed to retrieve projects: {str(e)}")]

        if name == "view-todos":
            # Validate Things3 is accessible
            if not AppleScriptHandler.validate_things3_access():
                return [types.TextContent(type="text", text="Things3 is not available. Please ensure Things3 is installed and running.")]
            
            try:
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
            except Exception as e:
                logger.error(f"Error retrieving todos: {e}")
                return [types.TextContent(type="text", text=f"Failed to retrieve todos: {str(e)}")]

        if name == "create-things3-project":
            if not arguments:
                raise ValueError("Missing arguments")

            # Validate Things3 is available
            if not XCallbackURLHandler.validate_things3_available():
                return [
                    types.TextContent(
                        type="text",
                        text="Things3 is not running or not installed. Please start Things3 and try again.",
                    )
                ]

            # Build the Things3 URL with proper encoding
            base_url = "things:///add-project"
            params = {
                "title": arguments["title"]
            }
            
            # Optional parameters
            if "notes" in arguments:
                params["notes"] = arguments["notes"]
            if "area" in arguments:
                params["area"] = arguments["area"]
            if "when" in arguments:
                params["when"] = arguments["when"]
            if "deadline" in arguments:
                params["deadline"] = arguments["deadline"]
            if "tags" in arguments:
                params["tags"] = arguments["tags"]
            
            url = XCallbackURLHandler.build_url(base_url, params)
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

            # Validate Things3 is available
            if not XCallbackURLHandler.validate_things3_available():
                return [
                    types.TextContent(
                        type="text",
                        text="Things3 is not running or not installed. Please start Things3 and try again.",
                    )
                ]

            # Build the Things3 URL with proper encoding
            base_url = "things:///add"
            params = {
                "title": arguments["title"]
            }
            
            # Optional parameters
            if "notes" in arguments:
                params["notes"] = arguments["notes"]
            if "when" in arguments:
                params["when"] = arguments["when"]
            if "deadline" in arguments:
                params["deadline"] = arguments["deadline"]
            if "checklist" in arguments:
                params["checklist"] = "\n".join(arguments["checklist"])
            if "tags" in arguments:
                params["tags"] = arguments["tags"]
            if "list" in arguments:
                params["list"] = arguments["list"]
            if "heading" in arguments:
                params["heading"] = arguments["heading"]
            
            url = XCallbackURLHandler.build_url(base_url, params)
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

        if name == "complete-things3-todo":
            if not arguments:
                raise ValueError("Missing arguments")

            # Validate Things3 is available
            if not AppleScriptHandler.validate_things3_access():
                return [
                    types.TextContent(
                        type="text",
                        text="Things3 is not available. Please ensure Things3 is installed and running.",
                    )
                ]

            try:
                success = AppleScriptHandler.complete_todo_by_title(arguments["title"])
                if success:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"Successfully completed todo containing '{arguments['title']}'",
                        )
                    ]
                else:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"No incomplete todo found containing '{arguments['title']}'",
                        )
                    ]
            except Exception as e:
                logger.error(f"Error completing todo: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Failed to complete todo: {str(e)}",
                    )
                ]

        if name == "search-things3-todos":
            if not arguments:
                raise ValueError("Missing arguments")

            # Validate Things3 is available
            if not AppleScriptHandler.validate_things3_access():
                return [
                    types.TextContent(
                        type="text",
                        text="Things3 is not available. Please ensure Things3 is installed and running.",
                    )
                ]

            try:
                todos = AppleScriptHandler.search_todos(arguments["query"])
                if not todos:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"No todos found matching '{arguments['query']}'",
                        )
                    ]

                response = [f"Found {len(todos)} todo(s) matching '{arguments['query']}':"]
                for todo in todos:
                    title = todo.get("title", "Untitled Todo")
                    status = todo.get("status", "unknown")
                    status_icon = "✅" if status == "completed" else "⏳"
                    due_date = todo.get("due_date", "No Due Date")
                    response.append(f"\n{status_icon} {title} (Due: {due_date})")

                return [types.TextContent(type="text", text="\n".join(response))]
            except Exception as e:
                logger.error(f"Error searching todos: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Failed to search todos: {str(e)}",
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