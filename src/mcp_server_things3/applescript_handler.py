import subprocess
from typing import List, Dict, Any, Optional
import json
import re

class AppleScriptHandler:
    """Handles AppleScript execution for Things3 data retrieval."""

    @staticmethod
    def run_script(script: str) -> str:
        """
        Executes an AppleScript and returns its output.
        """
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

    @staticmethod
    def safe_string_for_applescript(text: str) -> str:
        """
        Safely escape a string for use in AppleScript by handling quotes and special characters.
        """
        if not text:
            return ""
        
        # Replace backslashes first to avoid double escaping
        text = text.replace("\\", "\\\\")
        # Replace quotes with escaped quotes
        text = text.replace('"', '\\"')
        # Replace newlines with \\n
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "\\r")
        
        return text

    @staticmethod
    def parse_applescript_record(record_str: str) -> Dict[str, Any]:
        """
        Parse an AppleScript record string into a Python dictionary.
        More robust than string concatenation for JSON.
        """
        result = {}
        
        # Remove outer braces if present
        record_str = record_str.strip()
        if record_str.startswith('{') and record_str.endswith('}'):
            record_str = record_str[1:-1]
        
        # Split by commas but be careful about nested structures
        parts = []
        current_part = ""
        brace_count = 0
        
        for char in record_str:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == ',' and brace_count == 0:
                parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Parse each key-value pair
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().strip('"\'')
                value = value.strip().strip('"\'')
                result[key] = value
        
        return result

    @staticmethod
    def get_inbox_tasks() -> List[Dict[str, Any]]:
        """
        Retrieves tasks from the Inbox using AppleScript with improved data handling.
        """
        script = '''
        tell application "Things3"
            set inboxTasks to to dos of list "Inbox"
            set resultList to {}
            
            repeat with t in inboxTasks
                set taskTitle to name of t
                
                set taskNotes to ""
                if notes of t is not missing value then
                    set taskNotes to notes of t
                end if
                
                set dueDate to ""
                if due date of t is not missing value then
                    set dueDate to ((due date of t) as string)
                end if
                
                set whenDate to ""
                if activation date of t is not missing value then
                    set whenDate to ((activation date of t) as string)
                end if
                
                set tagText to ""
                try
                    set tagList to tag names of t
                    if tagList is not {} then
                        set AppleScript's text item delimiters to ","
                        set tagText to tagList as string
                        set AppleScript's text item delimiters to ""
                    end if
                end try
                
                -- Create a record for this task
                set taskRecord to {title:taskTitle, notes:taskNotes, due_date:dueDate, when_date:whenDate, tags:tagText}
                set end of resultList to taskRecord
            end repeat
            
            return resultList
        end tell
        '''

        try:
            result = AppleScriptHandler.run_script(script)
            
            # If we get an empty result or AppleScript list, return empty list
            if not result or result == "{}" or result == "":
                return []
            
            # Parse AppleScript record format to extract task data
            tasks = []
            
            # Handle AppleScript list format: {{record1}, {record2}, ...}
            if result.startswith('{{') and result.endswith('}}'):
                # Remove outer braces and split by }, {
                records_str = result[2:-2]  # Remove {{ and }}
                record_strings = re.split(r'\}, \{', records_str)
                
                for record_str in record_strings:
                    # Clean up the record string
                    record_str = record_str.strip()
                    if not record_str.startswith('{'):
                        record_str = '{' + record_str
                    if not record_str.endswith('}'):
                        record_str = record_str + '}'
                    
                    # Parse the record
                    task_data = AppleScriptHandler.parse_applescript_record(record_str)
                    
                    # Convert to our expected format
                    task = {
                        "title": task_data.get("title", ""),
                        "notes": task_data.get("notes", ""),
                        "due_date": task_data.get("due_date", ""),
                        "when": task_data.get("when_date", ""),
                        "tags": task_data.get("tags", "")
                    }
                    tasks.append(task)
            
            return tasks
            
        except Exception as e:
            # Log the error but return empty list rather than crashing
            print(f"Error retrieving inbox tasks: {e}")
            return []

    @staticmethod
    def get_todays_tasks() -> List[Dict[str, Any]]:
        """
        Retrieves today's tasks from Things3 using AppleScript with improved data handling.
        """
        script = '''
        tell application "Things3"
            set todayTasks to to dos of list "Today"
            set resultList to {}
            
            repeat with t in todayTasks
                set taskTitle to name of t
                
                set taskNotes to ""
                if notes of t is not missing value then
                    set taskNotes to notes of t
                end if
                
                set dueDate to ""
                if due date of t is not missing value then
                    set dueDate to ((due date of t) as string)
                end if
                
                set startDate to ""
                try
                    if start date of t is not missing value then
                        set startDate to ((start date of t) as string)
                    end if
                on error
                    set startDate to ""
                end try
                
                set whenDate to ""
                if activation date of t is not missing value then
                    set whenDate to ((activation date of t) as string)
                end if
                
                set tagText to ""
                try
                    set tagList to tag names of t
                    if tagList is not {} then
                        set AppleScript's text item delimiters to ","
                        set tagText to tagList as string
                        set AppleScript's text item delimiters to ""
                    end if
                end try
                
                -- Create a record for this task
                set taskRecord to {title:taskTitle, notes:taskNotes, due_date:dueDate, start_date:startDate, when_date:whenDate, tags:tagText}
                set end of resultList to taskRecord
            end repeat
            
            return resultList
        end tell
        '''

        try:
            result = AppleScriptHandler.run_script(script)
            
            # If we get an empty result, return empty list
            if not result or result == "{}" or result == "":
                return []
            
            # Parse AppleScript record format to extract task data
            tasks = []
            
            # Handle AppleScript list format
            if result.startswith('{{') and result.endswith('}}'):
                records_str = result[2:-2]
                record_strings = re.split(r'\}, \{', records_str)
                
                for record_str in record_strings:
                    record_str = record_str.strip()
                    if not record_str.startswith('{'):
                        record_str = '{' + record_str
                    if not record_str.endswith('}'):
                        record_str = record_str + '}'
                    
                    task_data = AppleScriptHandler.parse_applescript_record(record_str)
                    
                    task = {
                        "title": task_data.get("title", ""),
                        "notes": task_data.get("notes", ""),
                        "due_date": task_data.get("due_date", ""),
                        "start_date": task_data.get("start_date", ""),
                        "when": task_data.get("when_date", ""),
                        "tags": task_data.get("tags", "")
                    }
                    tasks.append(task)
            
            return tasks
            
        except Exception as e:
            print(f"Error retrieving today's tasks: {e}")
            return []

    @staticmethod
    def get_projects() -> List[Dict[str, str]]:
        """
        Retrieves all projects from Things3 using AppleScript with improved data handling.
        """
        script = '''
        tell application "Things3"
            set projectList to projects
            set resultList to {}
            
            repeat with p in projectList
                set projectTitle to name of p
                set projectNotes to ""
                if notes of p is not missing value then
                    set projectNotes to notes of p
                end if
                
                -- Create a record for this project
                set projectRecord to {title:projectTitle, notes:projectNotes}
                set end of resultList to projectRecord
            end repeat
            
            return resultList
        end tell
        '''

        try:
            result = AppleScriptHandler.run_script(script)
            
            if not result or result == "{}" or result == "":
                return []
            
            projects = []
            
            # Handle AppleScript list format
            if result.startswith('{{') and result.endswith('}}'):
                records_str = result[2:-2]
                record_strings = re.split(r'\}, \{', records_str)
                
                for record_str in record_strings:
                    record_str = record_str.strip()
                    if not record_str.startswith('{'):
                        record_str = '{' + record_str
                    if not record_str.endswith('}'):
                        record_str = record_str + '}'
                    
                    project_data = AppleScriptHandler.parse_applescript_record(record_str)
                    
                    project = {
                        "title": project_data.get("title", ""),
                        "notes": project_data.get("notes", "")
                    }
                    projects.append(project)
            
            return projects
            
        except Exception as e:
            print(f"Error retrieving projects: {e}")
            return []

    @staticmethod
    def validate_things3_access() -> bool:
        """
        Validate that Things3 is accessible and responsive.
        """
        try:
            script = '''
            tell application "Things3"
                return name of application "Things3"
            end tell
            '''
            result = AppleScriptHandler.run_script(script)
            return "Things3" in result
        except Exception:
            return False

    @staticmethod
    def complete_todo_by_title(title_search: str) -> bool:
        """
        Mark a todo as completed by searching for its title.
        """
        script = f'''
        tell application "Things3"
            set foundTodo to missing value
            
            -- Search in Today list
            set todayTodos to to dos of list "Today"
            repeat with t in todayTodos
                if name of t contains "{AppleScriptHandler.safe_string_for_applescript(title_search)}" then
                    set foundTodo to t
                    exit repeat
                end if
            end repeat
            
            -- If not found in Today, search in Inbox
            if foundTodo is missing value then
                set inboxTodos to to dos of list "Inbox"
                repeat with t in inboxTodos
                    if name of t contains "{AppleScriptHandler.safe_string_for_applescript(title_search)}" then
                        set foundTodo to t
                        exit repeat
                    end if
                end repeat
            end if
            
            -- If not found in standard lists, search all todos
            if foundTodo is missing value then
                set allTodos to to dos
                repeat with t in allTodos
                    if name of t contains "{AppleScriptHandler.safe_string_for_applescript(title_search)}" and status of t is not completed then
                        set foundTodo to t
                        exit repeat
                    end if
                end repeat
            end if
            
            -- Complete the todo if found
            if foundTodo is not missing value then
                set status of foundTodo to completed
                return "COMPLETED:" & name of foundTodo
            else
                return "NOT_FOUND"
            end if
        end tell
        '''
        
        try:
            result = AppleScriptHandler.run_script(script)
            return result.startswith("COMPLETED:")
        except Exception:
            return False

    @staticmethod
    def search_todos(query: str) -> List[Dict[str, Any]]:
        """
        Search for todos by title or content.
        """
        script = f'''
        tell application "Things3"
            set searchQuery to "{AppleScriptHandler.safe_string_for_applescript(query)}"
            set foundTodos to {{}}
            set allTodos to to dos
            
            repeat with t in allTodos
                set taskTitle to name of t
                set taskNotes to ""
                if notes of t is not missing value then
                    set taskNotes to notes of t
                end if
                
                -- Check if query matches title or notes
                if taskTitle contains searchQuery or taskNotes contains searchQuery then
                    set taskStatus to "incomplete"
                    if status of t is completed then
                        set taskStatus to "completed"
                    end if
                    
                    set dueDate to ""
                    if due date of t is not missing value then
                        set dueDate to ((due date of t) as string)
                    end if
                    
                    set whenDate to ""
                    if activation date of t is not missing value then
                        set whenDate to ((activation date of t) as string)
                    end if
                    
                    set tagText to ""
                    try
                        set tagList to tag names of t
                        if tagList is not {{}} then
                            set AppleScript's text item delimiters to ","
                            set tagText to tagList as string
                            set AppleScript's text item delimiters to ""
                        end if
                    end try
                    
                    set taskRecord to {{title:taskTitle, notes:taskNotes, status:taskStatus, due_date:dueDate, when_date:whenDate, tags:tagText}}
                    set end of foundTodos to taskRecord
                end if
            end repeat
            
            return foundTodos
        end tell
        '''
        
        try:
            result = AppleScriptHandler.run_script(script)
            
            if not result or result == "{{}}" or result == "":
                return []
            
            todos = []
            
            # Handle AppleScript list format
            if result.startswith('{{{{') and result.endswith('}}}}'):
                records_str = result[4:-4]  # Remove outer {{ and }}
                record_strings = re.split(r'\}\}, \{\{', records_str)
                
                for record_str in record_strings:
                    record_str = record_str.strip()
                    if not record_str.startswith('{{'):
                        record_str = '{{' + record_str
                    if not record_str.endswith('}}'):
                        record_str = record_str + '}}'
                    
                    # Remove the outer braces for parsing
                    inner_record = record_str[2:-2]
                    task_data = AppleScriptHandler.parse_applescript_record('{' + inner_record + '}')
                    
                    todo = {
                        "title": task_data.get("title", ""),
                        "notes": task_data.get("notes", ""),
                        "status": task_data.get("status", "unknown"),
                        "due_date": task_data.get("due_date", ""),
                        "when": task_data.get("when_date", ""),
                        "tags": task_data.get("tags", "")
                    }
                    todos.append(todo)
            
            return todos
            
        except Exception as e:
            print(f"Error searching todos: {e}")
            return []
