import os
import time
import base64
import subprocess
import psutil
import pyautogui
from io import BytesIO
from groq import Groq
from config.settings import GROQ_API_KEY, VISION_MODEL
from self_improver import agent, read_agent_file, update_agent_file

client = Groq(api_key=GROQ_API_KEY)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def execute_system_command(command: str) -> str:
    """Windows Terminal / PowerShell commands execution"""
    return agent.execute_powershell(command)


def window_control(action: str, target_app: str = "") -> str:
    """Windows actions: minimize, maximize, close applications"""
    action = action.lower().strip()
    if action == "minimize_all":
        return agent.gui_action("minimize_all")
    elif action == "close" and target_app:
        return agent.gui_action("close_app", target_app)
    elif action in ["maximize", "fullscreen"]:
        return agent.gui_action("hotkey", "alt, space")
    return agent.gui_action(action, target_app)


def open_anything(target: str, url: str = "") -> str:
    """Files, Folders, URLs, Apps navigate karne ke liye function"""
    if url:
        cmd = f'start chrome "{url}"'
    elif "file manager" in target.lower() or "explorer" in target.lower():
        cmd = "explorer.exe"
    elif "download" in target.lower():
        cmd = "explorer.exe shell:Downloads"
    elif "desktop" in target.lower():
        cmd = 'explorer.exe "%USERPROFILE%\\Desktop"'
    elif "d drive" in target.lower() or "drive d" in target.lower():
        cmd = 'explorer.exe "D:\\"'
    else:
        cmd = f'start "" "{target}"'
        
    return agent.execute_powershell(cmd)


def gui_action(action_type: str, details: str = "") -> str:
    """Mouse click, typing, hotkey execution"""
    return agent.gui_action(action_type, details)


def capture_screen_and_analyze() -> str:
    """Screen live screenshot le kar active Groq vision model se analyze karta hai"""
    try:
        # High quality screenshot using pyautogui
        screenshot = pyautogui.screenshot()
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Direct Groq Vision API call using standard active vision model
        response = client.chat.completions.create(
            model=VISION_MODEL,  # llama-3.2-11b-vision-preview
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this screenshot and describe any errors, open windows, or key details visible on screen in 2 short Roman Urdu sentences."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[Fallback to agent analyze due to]: {e}")
        try:
            return agent.analyze_screen()
        except Exception as err:
            return f"Screen analyze karne mein masla aaya: {str(err)}"


def run_autonomous_task(task_description: str) -> str:
    """Autonomous tasks runs via Agent"""
    return agent.autonomous_task_execution(task_description)


def get_system_status() -> str:
    """System status return karta hai (CPU, RAM, Battery)"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        battery_pct = f"{battery.percent}%" if battery else "Unknown"
        return f"CPU: {cpu_usage}%, RAM: {ram.percent}%, Battery: {battery_pct}"
    except Exception as e:
        return f"Status check error: {str(e)}"


def create_and_run_python_code(filename: str, code_content: str) -> str:
    """Python code files write aur execute karta hai"""
    try:
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
            
        result = subprocess.run(["python", file_path], capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        errors = result.stderr.strip()
        
        if errors:
            return f"Code runtime errors: {errors}"
        return f"Code executed successfully. Output:\n{output}"
    except Exception as e:
        return f"Execution error: {str(e)}"