from tkinter import *
from tkinter import ttk
import threading
import requests
from agents import triage_agent
from swarm.repl import run_demo_loop


root = Tk()

root.geometry("700x700")
root.title("AI Chatbot")
# Dark theme colors
background_color = "#2C3E50"  
text_color = "#D3D3D3"        
button_color = "#FFA07A"      
enter_bg_color = "#34495E"    
enter_text_color = "#FFFFFF"  




import json
from openai import OpenAI
from swarm import Swarm


def process_and_print_streaming_response(response):
    content = ""
    last_sender = ""

    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]

        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]

        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")

        if "delim" in chunk and chunk["delim"] == "end" and content:
            print()  # End of response message
            content = ""

        if "response" in chunk:
            return chunk["response"]


def pretty_print_messages(messages) -> None:
    for message in messages:
        if message["role"] != "assistant":
            continue

        # print agent name in blue
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # print response, if any
        if message["content"]:
            print(message["content"])
            text_box.insert(END, message["content"])

        # print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")


def run_demo_loop(
    starting_agent, context_variables=None, stream=False, debug=False
) -> None:
    ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",        
    api_key="ollama"            
)
    print("Starting of run demo loop")
    client = Swarm(client=ollama_client)
    print("Starting Swarm CLI 🐝")

    messages = []
    agent = starting_agent


    user_input = question_var.get()
    messages.append({"role": "user", "content": user_input})
    print("before client run")
    response = client.run(
        agent=agent,
        messages=messages,
        context_variables=context_variables or {},
        stream=stream,
        debug=debug,
    )
    print("after client run")

    if stream:
        response = process_and_print_streaming_response(response)
    else:
        pretty_print_messages(response.messages)

    messages.extend(response.messages)
    agent = response.agent






root.configure(background=background_color)

question_var = StringVar()

progressbar = ttk.Progressbar(root, mode="indeterminate")

def start_progress():
    progressbar.start()

def stop_progress():
    progressbar.stop()

def fetch_answer():
    user_input = question_var.get()
    stop_progress()


def generate_answer():
    threading.Thread(target=start_progress).start()
    threading.Thread(target=fetch_answer).start()
    run_demo_loop(triage_agent)



scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

text_box = Text(root, height=30, width=0, font=('Microsoft YaHei Light', 14, "bold"),yscrollcommand=scrollbar.set, bg=enter_bg_color, fg=text_color, insertbackground=text_color)
text_box.pack(pady=10, fill=BOTH, expand=True)

scrollbar.config(command=text_box.yview)

question_label = Label(root, text="Enter your question:", font=('Microsoft YaHei Light', 14, "bold"),bg=background_color, fg=text_color)
question_label.pack(pady=5)

question_entry = Entry( root, textvariable=question_var, font=('Microsoft YaHei Light', 14, "bold"),bg=enter_bg_color, fg=enter_text_color, insertbackground=enter_text_color)
question_entry.pack(pady=5)

ask_button = Button(root, text="Generate Response", command=generate_answer,font=("Microsoft YaHei Light", 14, "bold"), bg=button_color, fg=text_color)
ask_button.pack(pady=10)

progressbar.pack(pady=10)

root.mainloop()





