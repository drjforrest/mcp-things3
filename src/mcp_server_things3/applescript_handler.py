import subprocess
from typing import List, Dict, Any
import json

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
    def get_inbox_tasks() -> List[Dict[str, Any]]:
        """
        Retrieves tasks from the Inbox using AppleScript.
        """
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

        result = AppleScriptHandler.run_script(script)
        return json.loads(result)

    @staticmethod
    def get_todays_tasks() -> List[Dict[str, Any]]:
        """
        Retrieves today's tasks from Things3 using AppleScript.
        """
        script = '''
            tell application "Things3"
                -- Get today's tasks
                set todayTasks to to dos of list "Today"

                -- Initialize an empty list for JSON
                set tasksJSON to "["

                -- Loop through each task and collect details
                repeat with t in todayTasks
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

                    -- Start Date
                    set startDate to ""
                    try
                        if startDate of t is not missing value then
                            set startDate to ((startDate of t) as string)
                        end if
                    on error
                        set startDate to ""
                    end try

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
                        "\\"start_date\\": \\"" & startDate & "\\"," & ¬
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

        result = AppleScriptHandler.run_script(script)
        return json.loads(result)

    @staticmethod
    def get_projects() -> List[Dict[str, str]]:
        """
        Retrieves all projects from Things3 using AppleScript.
        """
        script = '''
            tell application "Things3"
                set projectList to projects
                set projectJSON to "["

                repeat with p in projectList
                    set projectTitle to name of p
                    set projectNotes to ""
                    if notes of p is not missing value then
                        set projectNotes to notes of p
                    end if

                    set projectJSON to projectJSON & "{\\"title\\": \\"" & projectTitle & "\\", \\"notes\\": \\"" & projectNotes & "\\"},"
                end repeat

                if length of projectJSON > 1 then
                    set projectJSON to text 1 thru -2 of projectJSON
                end if
                set projectJSON to projectJSON & "]"

                return projectJSON
            end tell
        '''

        result = AppleScriptHandler.run_script(script)
        return json.loads(result)
