import os
import time
import base64
import json
import subprocess
import pyautogui
from PIL import ImageGrab
from groq import Groq
from config.settings import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def read_agent_file(file_path: str) -> str:
    """Project ki specific code file ko read karta hai."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return f"File '{file_path}' nahi mili."
    except Exception as e:
        return f"File read error: {str(e)}"


def update_agent_file(file_path: str, new_code: str) -> str:
    """Project ki file ko user permission ke sath rewrite/update karta hai."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_code)
        return f"File '{file_path}' successfully update ho gayi hai."
    except Exception as e:
        return f"File update error: {str(e)}"


class AutonomousAgent:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.screenshot_path = os.path.join(self.output_dir, "current_screen.png")

    def capture_screen(self):
        screenshot = ImageGrab.grab()
        screenshot.save(self.screenshot_path)
        with open(self.screenshot_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def analyze_screen(self, query="What is visible on the screen right now? Summarize in 1-2 short Roman Urdu sentences."):
        try:
            base64_img = self.capture_screen()
            response = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview", # Active Groq Vision Model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
                        ]
                    }
                ],
                max_tokens=150
            )
            analysis = response.choices[0].message.content
            print(f"👀 [Vision Analysis]: {analysis}")
            return analysis
        except Exception as e:
            print(f"[Vision Error]: {e}")
            return f"Vision processing error: {str(e)}"

    def execute_powershell(self, command: str) -> str:
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=25
            )
            out = result.stdout.strip()
            err = result.stderr.strip()
            return out if out else (f"Error: {err}" if err else "Command executed successfully.")
        except Exception as e:
            return f"PowerShell execution failed: {str(e)}"

    def gui_action(self, action_type: str, details: str = "") -> str:
        try:
            action = action_type.lower().strip()
            if action == "minimize_all":
                pyautogui.hotkey("win", "d")
                return "All windows minimized."
            elif action == "click":
                if details and "," in details:
                    x, y = map(int, details.split(","))
                    pyautogui.click(x, y)
                else:
                    pyautogui.click()
                return "Mouse click performed."
            elif action == "type":
                pyautogui.write(details, interval=0.04)
                return f"Typed: {details}"
            elif action == "press":
                pyautogui.press(details)
                return f"Key pressed: {details}"
            elif action == "hotkey":
                keys = [k.strip() for k in details.split(",")]
                pyautogui.hotkey(*keys)
                return f"Hotkey executed: {details}"
            elif action == "close_app":
                os.system(f"taskkill /IM {details}.exe /F")
                return f"Closed process {details}."
            return "Action executed."
        except Exception as e:
            return f"GUI action error: {str(e)}"

    def autonomous_task_execution(self, user_prompt: str) -> str:
        """User prompt ke base par screen dekhta hai aur system action leta hai"""
        screen_state = self.analyze_screen(f"Check screen state to satisfy user request: '{user_prompt}'")
        
        prompt = f"""
User Goal: {user_prompt}
Current Screen State: {screen_state}

Decide the best command or GUI action to execute this goal on Windows.
Respond ONLY in valid JSON format:
{{
  "action_type": "powershell" OR "gui" OR "vision",
  "command": "PowerShell command string if action_type is powershell",
  "gui_action": "minimize_all/click/type/press/hotkey/close_app",
  "details": "arguments for gui action if needed",
  "response_message": "Short Roman Urdu response to user"
}}
"""
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # <-- Text Reasoning Model (Fixed)
                messages=[{"role": "system", "content": "You are a Windows System Control Agent. Respond ONLY in valid JSON."},
                          {"role": "user", "content": prompt}],
                temperature=0.1
            )
            res_text = response.choices[0].message.content.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(res_text)
            
            act_type = data.get("action_type")
            if act_type == "powershell":
                self.execute_powershell(data.get("command", ""))
            elif act_type == "gui":
                self.gui_action(data.get("gui_action", ""), data.get("details", ""))
            
            return data.get("response_message", "Task execute ho gaya hai.")
        except Exception as e:
            print(f"[Autonomous Execution Error]: {e}")
            return f"Autonomous execution error: {str(e)}"

agent = AutonomousAgent()