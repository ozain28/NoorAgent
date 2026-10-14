import json
from services.system_control import (
    open_anything,
    capture_screen_and_analyze,
    run_autonomous_task
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_autonomous_task",
            "description": "User ki kisi bhi complex request par screen analyze karke system par autonomously action leta hai (e.g., 'sab minimize karo', 'Chrome close karo', 'D drive kholo').",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "User ki exact request ya system task instruction"
                    }
                },
                "required": ["task_description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_anything",
            "description": "App, folder, D drive, ya URL open karta hai.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "url": {"type": "string"}
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capture_screen_and_analyze",
            "description": "Live screenshot le kar screen condition read karta hai.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

def execute_tool_call(tool_call):
    """Executes the tool function dynamically called by LLM."""
    function_name = tool_call.function.name
    
    # Empty args ya invalid json handling
    try:
        arguments = json.loads(tool_call.function.arguments or "{}")
    except Exception:
        arguments = {}

    print(f"⚙️ [Autonomous Tool Triggered]: {function_name} | Args: {arguments}")

    if function_name == "run_autonomous_task":
        task_desc = arguments.get("task_description", "System check")
        return run_autonomous_task(task_description=task_desc)
        
    elif function_name == "open_anything":
        target = arguments.get("target", "")
        url = arguments.get("url", "")
        return open_anything(target=target, url=url)
        
    elif function_name == "capture_screen_and_analyze":
        return capture_screen_and_analyze()

    return "Unknown tool call"