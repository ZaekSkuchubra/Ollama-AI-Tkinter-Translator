import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import requests
import io
import contextlib
import os
import subprocess
import threading 

OLLAMA_API_URL = "http://localhost:11434/v1/completions"

def translate_code_to_python(input_code, source_language):
    try:
        prompt = (
            f"Translate the following {source_language} code into Python:\n\n"
            f"{input_code}\n\n"
            "Only provide the translated Python code without any explanations, comments, or formatting symbols like ```."
        )

        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.2
            }
        )

        if response.status_code == 200:
            try:
                response_json = response.json()
                translated_code = response_json['choices'][0]['text'].strip()
                translated_code = translated_code.replace("```python", "").replace("```", "").strip()
                return translated_code
            except ValueError as ve:
                print("Raw response:", response.text)
                return f"JSON Parsing Error: {ve}"
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Exception during translation: {e}"

def execute_python_code(code):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            exec(code, {"__builtins__": __builtins__, "tk": tk})
        except Exception as e:
            return f"Execution Error: {e}"
    return output.getvalue().strip()

def save_to_file(code):
    file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(code)
        return file_path
    return None

def translate_and_execute():
    input_code = input_text.get("1.0", tk.END).strip()
    source_language = source_lang_entry.get().strip()
    
    translated_code = translate_code_to_python(input_code, source_language)
    output_text.delete("1.0", tk.END)

    if translated_code.startswith("Error") or translated_code.startswith("Exception"):
        output_text.insert(tk.END, translated_code)
    else:
        output_text.insert(tk.END, f"Translated Python Code:\n{translated_code}\n\nExecution Result:\n")

        # Check if file exists; prompt to save if it doesn't
        execute_path = "translated_code.py"  # Default file name
        if not os.path.exists(execute_path):
            if messagebox.askyesno("Save File", "File doesn't exist. Would you like to save it before executing?"):
                execute_path = save_to_file(translated_code)
                if not execute_path:
                    output_text.insert(tk.END, "Execution canceled: file not saved.")
                    return
            else:
                with open(execute_path, "w") as file:
                    file.write(translated_code)

        # Execute the translated code and display the result
        execution_result = execute_python_code(translated_code)
        output_text.insert(tk.END, execution_result)
def startup():
    try:

        runmodelpath = os.path.join(os.path.dirname(__file__), 'RunModel.ps1')
        subprocess.run(["powershell.exe", "-File", runmodelpath])
    except Exception as e:
        print(f"Error running 'RunModel.ps1': {str(e)}")

def threadingmaster():
    threading.Thread(target=startup, daemon=True).start()

DEFAULT_SOURCE_LANGUAGE = "C++"
root = tk.Tk()
root.title("Code Translator and Executor")

source_lang_label = tk.Label(root, text="Source Language:")
source_lang_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
source_lang_entry = tk.Entry(root, width=30)
source_lang_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

input_label = tk.Label(root, text="Input Code:")
input_label.grid(row=1, column=0, padx=10, pady=5, sticky="nw")
input_text = scrolledtext.ScrolledText(root, width=80, height=10)
input_text.grid(row=1, column=1, padx=10, pady=5)

translate_button = tk.Button(root, text="Translate and Execute", command=translate_and_execute)
translate_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

cleaninput = tk.Button(root, text="Clear Input", command=lambda: input_text.delete("1.0", tk.END))
cleaninput.grid(row=1, column=2, sticky="ne")

cleanoutput = tk.Button(root, text="Clear Output", command=lambda: output_text.delete("1.0", tk.END))
cleanoutput.grid(row=1, column=3, sticky="nw")

output_label = tk.Label(root, text="Output:")
output_label.grid(row=3, column=0, padx=10, pady=5, sticky="nw")
output_text = scrolledtext.ScrolledText(root, width=80, height=10)
output_text.grid(row=3, column=1, padx=10, pady=5)

startupmodel = tk.Button(root, text="Start Model", command=threadingmaster)
startupmodel.grid(row=0, column=3, padx=10, pady=10, sticky="ne")

root.mainloop()
