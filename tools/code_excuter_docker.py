from langchain.tools import tool
import os
import subprocess
import shlex


@tool
def Code_Executor(language: str, code: str, packages: str = "", filepaths: str = "", output_dir: str = "agent_outputs", step_name: str = "default_step") -> str:
    """
    Executes a code block in a container, saves the code and results to a structured output directory.
    Args:
    - language (str): 'python', 'r', or 'bash'.
    - code (str): The code block to execute.
    - packages (str, optional): Space-separated string of dependency packages to install if not present in the base image.
    - filepaths (str, optional): Space-separated string of local file paths that the code needs to access.
    - output_dir (str, optional): The main directory to store all outputs for the task. Defaults to 'agent_outputs'.
    - step_name (str, optional): A descriptive name for the current execution step (e.g., 'step1_data_cleaning').
    """
    image = "lengyang/pb_bio_tools:2.0.1"
    if language not in ['python', 'r', 'bash']:
        return f"Error: Unsupported language '{language}'. Available options: 'python', 'r', 'bash'"

    extensions = {'python': '.py', 'r': '.R', 'bash': '.sh'}
    
    # 1. Setup host paths for outputs and scripts
    host_step_dir = os.path.abspath(os.path.join(output_dir, step_name))
    os.makedirs(host_step_dir, exist_ok=True)
    
    host_code_filename = f"script{extensions[language]}"
    host_code_filepath = os.path.join(host_step_dir, host_code_filename)
    entrypoint_filename = "entrypoint.sh"
    host_entrypoint_filepath = os.path.join(host_step_dir, entrypoint_filename)

    try:
        # --- File mounting and path rewriting logic ---
        docker_mounts = [
            "-v", f"{host_step_dir}:/app", # Mount the step-specific directory as the workdir
            "-v", f"{os.path.abspath(output_dir)}:/outputs" # Mount the parent output dir for inter-step communication
        ]
        final_code = code
        
        if filepaths:
            path_list = shlex.split(filepaths)
            unique_dirs = {}
            path_mapping = {}

            # First, identify all unique directories and their container mount points
            for host_path in path_list:
                expanded_host_path = os.path.expanduser(host_path)
                if not os.path.exists(expanded_host_path):
                    return f"Error: File path '{host_path}' does not exist. Please provide a valid file path."
                
                host_abs_path = os.path.abspath(expanded_host_path)
                host_dir = os.path.dirname(host_abs_path)

                if host_dir not in unique_dirs:
                    container_dir = f"/data{len(unique_dirs)}"
                    unique_dirs[host_dir] = container_dir
            
            # Build mount commands and the path mapping for code replacement
            for host_dir, container_dir in unique_dirs.items():
                docker_mounts.extend(["-v", f"{host_dir}:{container_dir}"])

            for host_path in path_list:
                expanded_host_path = os.path.expanduser(host_path)
                host_abs_path = os.path.abspath(expanded_host_path)
                host_dir = os.path.dirname(host_abs_path)
                filename = os.path.basename(host_abs_path)
                
                container_dir = unique_dirs[host_dir]
                container_path = os.path.join(container_dir, filename)
                path_mapping[host_path] = container_path

            # Replace paths in the code, starting with the longest to avoid substring issues
            for host_path in sorted(path_mapping.keys(), key=len, reverse=True):
                final_code = final_code.replace(host_path, path_mapping[host_path])
        # --- End of file mounting logic ---

        with open(host_code_filepath, "w", encoding="utf-8") as f:
            f.write(final_code)

        # 2. Create an entrypoint script based on language and packages
        install_cmd = ""
        if packages:
            if language == 'python':
                install_cmd = f"pip install {packages}"
            elif language == 'r':
                # R's package installation command is specific
                install_cmd = f"R -e \"install.packages(c({', '.join([f'{repr(p)}' for p in packages.split()])}), repos='http://cran.us.r-project.org')\""
            elif language == 'bash':
                install_cmd = f"apt-get update && apt-get install -y {packages}"
        
        run_cmd = {'python': f'python {host_code_filename}', 'r': f'Rscript {host_code_filename}', 'bash': f'bash {host_code_filename}'}[language]

        entrypoint_content = f"""#!/bin/bash
set -e
echo "--- Starting dependency installation ---"
{install_cmd if install_cmd else 'echo "No packages to install."'}
echo "--- Dependency installation complete ---"
echo "--- Starting main script execution ---"
{run_cmd}
echo "--- Main script execution complete ---"
"""
        with open(host_entrypoint_filepath, "w", encoding="utf-8") as f:
            f.write(entrypoint_content)
        os.chmod(host_entrypoint_filepath, 0o755) # Grant execute permissions

        # 3. Build and execute the Docker command
        docker_command = [
            "docker", "run", "--rm",
            *docker_mounts,
            "--workdir", "/app",
            image,
            "bash", f"./{entrypoint_filename}"
        ]
        
        result = subprocess.run(docker_command, capture_output=True, text=True, check = False, encoding="utf-8")

        if result.returncode == 0:
            return f"Successfully executed code in Docker image '{image}'. Outputs are saved in '{host_step_dir}'.\n\nScript Output:\n{result.stdout}"
        else:
            return f"Error executing code in Docker image '{image}'. Check logs in '{host_step_dir}'.\n\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    except FileNotFoundError:
        return "Docker execution error: 'docker' command not found. Please ensure Docker is installed and running."
    except Exception as e:
        return f"An unknown error occurred during Docker execution: {str(e)}"