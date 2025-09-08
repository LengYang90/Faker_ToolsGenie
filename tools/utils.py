import os
import subprocess
import sys
from langchain.tools import Tool

def run_python_script(script: str) -> str:
    """
    Write the Python code string to a temporary file and execute it, then return the output.
    Suitable for independent Python script tasks. Note: This environment is not persistent, and each execution is independent.
    """
    script_filename = "temp_script.py"
    try:
        # clean the possible Markdown code tags
        clean_script = script.strip().strip("```python").strip("```").strip()
        with open(script_filename, "w", encoding="utf-8") as f:
            f.write(clean_script)
        
        # execute the script
        result = subprocess.run(
            [sys.executable, script_filename],
            capture_output=True, text=True, check=False, encoding="utf-8"
        )
        
        if result.returncode == 0:
            return f"Python script execution successful:\n{result.stdout}"
        else:
            return f"Python script execution error:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    except Exception as e:
        return f"Unknown error occurred while executing Python script: {str(e)}"


def run_shell_script(script: str) -> str:
    """
    Write the Shell command string to a temporary script file and execute it, then return the output.
    Suitable for multi-line or complex shell operations.
    """
    script_filename = "temp_script.sh"
    try:
        clean_script = script.strip().strip("```bash").strip("```").strip()
        with open(script_filename, "w", encoding="utf-8") as f:
            f.write(clean_script)
        
        # give execute permission
        os.chmod(script_filename, 0o755)

        # execute the script
        result = subprocess.run(
            ["/bin/bash", script_filename], 
            capture_output=True, text=True, check=False, encoding="utf-8"
        )

        if result.returncode == 0:
            return f"Shell script output:\n{result.stdout}"
        else:
            return f"Shell script execution error:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    except Exception as e:
        return f"Unknown error occurred while executing Shell script: {str(e)}"



def run_r_script(script: str) -> str:
    """
    Write the R code string to a temporary file and execute it, then return the output.
    """
    script_filename = "temp_script.R"
    try:
        clean_script = script.strip().strip("```R").strip("```").strip()
        with open(script_filename, "w", encoding="utf-8") as f:
            f.write(clean_script)

        # use Rscript to execute the file
        result = subprocess.run(
            ["Rscript", script_filename],
            capture_output=True, text=True, check=False, encoding="utf-8"
        )
        
        if result.returncode == 0:
            return f"R script output:\n{result.stdout}"
        else:
            return f"R script execution error:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    except FileNotFoundError:
        return "R script execution error: 'Rscript' command not found. Please ensure R language is installed and configured in the system path."
    except Exception as e:
        return f"Unknown error occurred while executing R script: {str(e)}"

def read_file(filename: str) -> str:
    """
    Read the content of the specified file and return it.
    Suitable for scenarios where data or text needs to be obtained from a file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Successfully read the content of file '{filename}'.\n\nFile content:\n{content}"
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error occurred while reading file '{filename}': {str(e)}"

def view_file_head(filename: str) -> str:
    """
    Read and return the first 10 lines of the file.
    When you need to write code to process a file, use this tool to preview the structure of the file,
    such as viewing column names, row numbers, separators (comma, tab, or other) and column types.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            head_lines = [next(f) for _ in range(10)]
        return f"Successfully read the first 10 lines of file '{filename}'.\n\nFile head content:\n{''.join(head_lines)}"
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except StopIteration:
        # if the file has less than 10 lines, it can be handled normally
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Successfully read the entire content of file '{filename}' (file has less than 10 lines).\n\nFile content:\n{content}"
    except Exception as e:
        return f"Error occurred while reading file '{filename}': {str(e)}"

view_file_header = Tool(
        name="View_File_Head",
        func=view_file_head,
        description="A tool for viewing the first 10 lines of a file. When you need to write code to process a file, please use this tool to preview the structure of the file, such as viewing column names, row numbers, separators (comma, tab, or other) and column types."
    )

file_reader = Tool(
        name="File_Reader",
        func=read_file,
        description="A tool for reading the content of a file. When you need to process data from a local file, please use this tool to read the file first."
    )
    
python_script_runner = Tool(
        name="Python_Script_Runner",
        func=run_python_script,
        description="A tool for running Python scripts. When you need to run a Python script, please use this tool to run the script."
    )

shell_script_runner = Tool(
        name="Shell_Script_Runner",
        func=run_shell_script,
        description="A tool for running Shell scripts. When you need to run a Shell script, please use this tool to run the script."
    )
    
r_script_runner = Tool(
        name="R_Script_Runner",
        func=run_r_script,
        description="A tool for running R scripts. When you need to run an R script, please use this tool to run the script."
    )