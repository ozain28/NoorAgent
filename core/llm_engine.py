import json
import re
from groq import Groq
from config.settings import GROQ_API_KEY, SYSTEM_PROMPT
from core.tool_manager import TOOLS, execute_tool_call

client = Groq(api_key=GROQ_API_KEY)

def clean_to_roman(text: str) -> str:
    """Removes unwanted tags and Arabic/Urdu scripts"""
    if not text:
        return ""
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL)
    text = re.sub(r'<function=.*?>', '', text)
    text = re.sub(r'[\u0600-\u06FF]', '', text)
    return text.strip()

def get_available_tool_model():
    """Groq account par live valid models scan karta hai"""
    try:
        models_data = client.models.list()
        available_ids = [m.id for m in models_data.data]
        
        # Valid chat models filter
        valid_models = [
            m_id for m_id in available_ids 
            if not any(x in m_id.lower() for x in ["whisper", "vision", "guard", "embed", "orpheus", "allam"])
        ]
        
        if valid_models:
            return valid_models[0]
            
    except Exception as e:
        print(f"[Model Discovery Warning]: {e}")
        
    return "llama-3.3-70b-versatile"

def process_chat(messages: list) -> str:
    """Handles LLM chat with active tool-capable model"""
    active_model = get_available_tool_model()
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    try:
        response = client.chat.completions.create(
            model=active_model,
            messages=full_messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=300,
            temperature=0.2
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            full_messages.append(response_message)

            for tool_call in tool_calls:
                tool_result = execute_tool_call(tool_call)
                
                full_messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": str(tool_result)
                })

            # Pass tools again to allow multi-step tool execution without error
            final_response = client.chat.completions.create(
                model=active_model,
                messages=full_messages,
                tools=TOOLS,
                max_tokens=200,
                temperature=0.2
            )
            
            raw_reply = final_response.choices[0].message.content
        else:
            raw_reply = response_message.content

        clean_reply = clean_to_roman(raw_reply)
        return clean_reply if clean_reply else "Ji Ozain, main sun rahi hoon."

    except Exception as e:
        print(f"[LLM Engine Error Details]: {e}")
        return "Ozain, request process karne mein thoda masla aaya hai."