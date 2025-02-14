#!/usr/bin/env python3

import subprocess
import json
from typing import Optional

class Things3Handler:
    """Handles Things3 integration through both x-callback-urls and AppleScript."""
    
    @staticmethod
    def call_url(url: str) -> str:
        """Executes an x-callback-url on macOS."""
        try:
            result = subprocess.run(
                ['open', url],
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to execute x-callback-url: {e}")
    
    @staticmethod
    def run_applescript(script: str) -> str:
        """Executes an AppleScript and returns its output."""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to execute AppleScript: {e}")

def test_create_project():
    """Test creating a project in Things3."""
    handler = Things3Handler()
    url = 'things:///add-project?title="MCP Test Project"&notes="Testing MCP integration"'
    print(f"Creating project with URL: {url}")
    response = handler.call_url(url)
    print(f"Response: {response}")

def test_create_todo():
    """Test creating a todo in Things3."""
    handler = Things3Handler()
    url = 'things:///add?title="Test Todo"&notes="Created via MCP test"&list="MCP Test Project"'
    print(f"Creating todo with URL: {url}")
    response = handler.call_url(url)
    print(f"Response: {response}")

def test_get_inbox_tasks():
    """Test retrieving tasks from the Inbox using AppleScript."""
    handler = Things3Handler()
    script = '''
    tell application "Things3"
        -- Get inbox tasks
        set inboxTasks to to dos of list "Inbox"
        
        -- Initialize an empty list for JSON
        set tasksJSON to "["
        
        -- Loop through each task and collect details
        repeat with t in inboxTasks
            set taskTitle to name of t
            
            -- Notes
            set taskNotes to ""
            if notes of t is not missing value then
                set taskNotes to notes of t
            end if
            
            -- Due Date
            set dueDate to ""
            if due date of t is not missing value then
                set dueDate to ((due date of t) as string)
            end if
            
            -- When (Soft Reminder)
            set whenDate to ""
            if activation date of t is not missing value then
                set whenDate to ((activation date of t) as string)
            end if
            
            -- Tags
            set tagText to ""
            try
                set tagList to tag names of t
                if tagList is not {} then
                    set tagText to tagList as string
                end if
            end try
            
            -- Construct JSON entry
            set tasksJSON to tasksJSON & "{\\"title\\": \\"" & taskTitle & "\\"," & ¬
                "\\"notes\\": \\"" & taskNotes & "\\"," & ¬
                "\\"due_date\\": \\"" & dueDate & "\\"," & ¬
                "\\"tags\\": \\"" & tagText & "\\"," & ¬
                "\\"when\\": \\"" & whenDate & "\\"},"
        end repeat
        
        -- Remove trailing comma and close JSON array
        if length of tasksJSON > 1 then
            set tasksJSON to text 1 thru -2 of tasksJSON
        end if
        set tasksJSON to tasksJSON & "]"
        
        return tasksJSON
    end tell
    '''
    
    print("Retrieving tasks from Inbox...")
    response = handler.run_applescript(script)
    tasks = json.loads(response)
    
    if not tasks:
        print("No tasks found in Inbox")
        return
        
    print("\nInbox tasks:")
    for task in tasks:
        print(f"\nTitle: {task['title']}")
        if task['notes']:
            print(f"Notes: {task['notes']}")
        if task['due_date']:
            print(f"Due: {task['due_date']}")
        if task['when']:
            print(f"When: {task['when']}")
        if task['tags']:
            print(f"Tags: {task['tags']}")

if __name__ == "__main__":
    print("Things3 MCP Integration Test")
    print("==========================")
    
    while True:
        print("\nChoose a test:")
        print("1. Create test project")
        print("2. Create test todo in project")
        print("3. View today's tasks")
        print("4. View inbox tasks")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        try:
            if choice == "1":
                test_create_project()
            elif choice == "2":
                test_create_todo()
            elif choice == "3":
                test_get_today_tasks()
            elif choice == "4":
                test_get_inbox_tasks()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}")
