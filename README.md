# MCP Server for Things3

A robust MCP (Model Context Protocol) server providing comprehensive integration with Things3, allowing you to create, manage, and search tasks and projects through the MCP protocol. Features improved error handling, secure URL encoding, and enhanced AppleScript integration.

## Features

- ✅ **Create Projects**: Create new projects in Things3 with full metadata support
- ✅ **Create Todos**: Create new to-dos with detailed properties including checklists, tags, and dates
- ✅ **View Tasks**: List tasks from inbox, today's list, or all projects
- ✅ **Complete Tasks**: Mark todos as completed by searching for their title
- ✅ **Search Functionality**: Search through all todos by title or content
- ✅ **Robust Error Handling**: Comprehensive validation and error recovery
- ✅ **Secure URL Encoding**: Proper handling of special characters and unicode
- ✅ **AppleScript Integration**: Safe, non-JSON string concatenation approach

## Installation

### Prerequisites
- macOS with Things3 installed
- Python 3.8+ 
- Things3 running (for real-time operations)

### Install the Server

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd mcp-things3
   ```

2. Install using pip:
   ```bash
   pip install -e .
   ```

3. The server will be available as `mcp-server-things3`

## Tools Available

### View Operations

#### `view-inbox`
View all todos in the Things3 inbox.
- **Parameters**: None
- **Returns**: List of inbox todos with due dates and scheduling info

#### `view-projects`
View all projects in Things3.
- **Parameters**: None  
- **Returns**: List of all projects with their titles

#### `view-todos`
View all todos in today's list.
- **Parameters**: None
- **Returns**: List of today's todos with metadata

### Creation Operations

#### `create-things3-project`
Creates a new project in Things3.
- **Required**: `title` (string)
- **Optional**: 
  - `notes` (string)
  - `area` (string) 
  - `when` (string) - Date/time to start
  - `deadline` (string) - Due date
  - `tags` (array of strings)

**Example**:
```json
{
  "title": "Website Redesign",
  "notes": "Complete overhaul of company website",
  "area": "Work",
  "deadline": "2024-03-15",
  "tags": ["urgent", "web-dev"]
}
```

#### `create-things3-todo`
Creates a new to-do in Things3.
- **Required**: `title` (string)
- **Optional**:
  - `notes` (string)
  - `when` (string) - Date/time to start  
  - `deadline` (string) - Due date
  - `checklist` (array of strings)
  - `tags` (array of strings)
  - `list` (string) - Project or area to assign to
  - `heading` (string) - Group under this heading

**Example**:
```json
{
  "title": "Review design mockups",
  "notes": "Check the new homepage designs",
  "list": "Website Redesign", 
  "deadline": "2024-02-20",
  "tags": ["review"],
  "checklist": ["Check mobile responsiveness", "Verify brand guidelines", "Test accessibility"]
}
```

### Management Operations

#### `complete-things3-todo`
Mark a todo as completed by searching for its title.
- **Required**: `title` (string) - Title or partial title to search for
- **Returns**: Success/failure message

**Example**:
```json
{
  "title": "Review design"
}
```

#### `search-things3-todos`
Search for todos by title or content.
- **Required**: `query` (string) - Search term
- **Returns**: List of matching todos with status and metadata

**Example**:
```json
{
  "query": "website"
}
```

## Integration with Claude

This MCP server is designed to work seamlessly with Claude AI. Once configured, you can use natural language to manage your Things3 tasks:

- "Create a project called 'Q1 Planning' with a deadline of March 31st"
- "Add a todo to review the budget with a checklist of tasks"
- "Show me all my tasks for today"
- "Mark the 'Call client' task as completed"
- "Search for all todos related to the website project"

## Configuration

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "things3": {
      "command": "mcp-server-things3",
      "args": []
    }
  }
}
```

### Things3 Setup

1. Ensure Things3 is installed and running
2. Grant necessary permissions when prompted for AppleScript access
3. The server will validate Things3 availability before operations

## Architecture

### Components

- **`server.py`**: Main MCP server implementation with tool definitions and handlers
- **`applescript_handler.py`**: Robust AppleScript integration with safe data parsing
- **URL Encoding**: Proper x-callback-url parameter encoding for special characters
- **Error Handling**: Comprehensive validation and graceful error recovery

### Security Features

- **Input Sanitization**: All user inputs are properly escaped for AppleScript
- **URL Encoding**: Special characters and unicode properly handled in URLs
- **Validation**: Things3 availability checked before operations
- **Error Recovery**: Graceful handling of AppleScript and system errors

## Development

### Running Tests

```bash
python test_things3.py
```

### Debugging

The server includes comprehensive logging. Set log level for debugging:

```bash
export PYTHONPATH="."
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from src.mcp_server_things3.server import main
import asyncio
asyncio.run(main())
"
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Troubleshooting

### Common Issues

**"Things3 is not available"**
- Ensure Things3 is installed and running
- Grant AppleScript permissions when prompted
- Check Things3 is not in a permission-restricted mode

**"Failed to execute AppleScript"**
- Verify macOS security settings allow AppleScript
- Ensure Things3 has necessary accessibility permissions
- Try restarting Things3

**URL encoding issues with special characters**
- The server now properly handles unicode and special characters
- If issues persist, check the logs for specific URL construction errors

### Performance Notes

- AppleScript operations may have slight delays
- Large todo lists (1000+ items) may take longer to search
- Consider using specific searches rather than broad queries for better performance

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0
- Initial release with basic CRUD operations
- Comprehensive error handling and validation
- Secure URL encoding and AppleScript integration
- Search and completion functionality
- Robust data parsing without JSON string concatenation
