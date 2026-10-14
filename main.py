import time
from core.llm_engine import process_chat
from services.voice_engine import speak, listen_mic

def start_agent():
    print("==================================================")
    print("🤖 Noor AI Active (System & Execution Control Agent)")
    print("==================================================\n")
    
    messages = []
    MAX_HISTORY = 12  # Context window overflow se bachne ke liye limit

    while True:
        try:
            user_text = listen_mic()
            
            # Validation for valid user input
            if not user_text or not isinstance(user_text, str) or not user_text.strip():
                continue

            messages.append({"role": "user", "content": user_text.strip()})

            start_time = time.time()
            print("\n🤖 Noor thinking & checking tools...")

            reply = process_chat(messages)

            print(f"🤖 Noor ({round(time.time() - start_time, 1)}s): {reply}\n")
            
            speak(reply)

            messages.append({"role": "assistant", "content": reply})
            
            # Keep history within reasonable token bounds
            if len(messages) > MAX_HISTORY:
                messages = messages[-MAX_HISTORY:]

            print("-" * 50)

        except KeyboardInterrupt:
            print("\nSession stopped naturally by user.")
            break
        except Exception as e:
            print(f"[Main Execution Loop Error]: {e}")
            time.sleep(1)  # CPU spiking se bachne ke liye brief sleep

if __name__ == "__main__":
    start_agent()