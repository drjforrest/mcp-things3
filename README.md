# MCP Server for Things3

This MCP server provides integration with Things3, allowing you to create and manage tasks and projects through the MCP protocol. It includes special support for synchronization with Agenda projects.

## Features

- Create new projects in Things3
- Create new to-dos with detailed properties
- Synchronize projects between Agenda and Things3
- List current tasks and projects
- AppleScript integration for data retrieval

## Installation

1. Ensure you have Python 3.8+ and Things3 installed
2. Clone this repository
3. Install dependencies:
   ```bash
   pip install -e .
   ```

## Usage

The server provides several tools:

### create-things3-project
Creates a new project in Things3 with the following options:
- title (required)
- notes
- area
- when
- deadline
- tags
- completed
- canceled

### create-things3-todo
Creates a new to-do in Things3 with the following options:
- title (required)
- notes
- when
- deadline
- checklist
- tags
- list
- heading
- completed
- canceled
- reveal

### sync-agenda-project
Creates a Things3 project that mirrors an Agenda project:
- title (required)
- notes
- area

## Development

The server uses:
- x-callback-url for creating items in Things3
- AppleScript for retrieving data from Things3
- MCP protocol for communication

## License

MIT