import os
import sys
import subprocess
from pathlib import Path


CONFIG = {
    'PYTORCH_DOWNLOAD_LINK': "pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu132",
    'REQUIREMENT_FILES': ["backend/requirements.txt", 'frontend/requirements.txt', 'training/requirements.txt']
}

def run_command(cmd: str):
    print(f"Running {cmd}")

    process = subprocess.run(
        cmd,
        shell=True,
        text=True
    )

    if process.returncode != 0:
        raise Exception(f"Command Failed: {cmd}")
    

def install_pytorch():
    print("\nInstalling PyTorch...\n")

    cmd = (
        f"pip install torch torchvision torchaudio "
        f"--index-url {CONFIG['PYTORCH_DOWNLOAD_LINK']}"
    )

    run_command(cmd)


def install_requirements():
    print("\nInstalling requirements...\n")

    for req in CONFIG['REQUIREMENT_FILES']:

        if os.path.exists(req):
            run_command(f"pip install -r {req}")
        else:
            print(f"[WARNING] Missing: {req}")


def clone_llama_cpp():
    print("\nChecking llama.cpp...\n")

    if os.path.exists("llama.cpp"):
        print("[INFO] llama.cpp already exists")
        return

    run_command(
        "git clone https://github.com/ggml-org/llama.cpp"
    )


def verify_ollama():
    print("\nVerifying Ollama...\n")

    try:
        run_command("ollama list")

    except Exception:
        print(
            "\n[WARNING] Ollama is not installed "
            "or not available in PATH"
        )


def verify_torch():

    print("\nVerifying PyTorch...\n")

    code = """
import torch

print("CUDA Available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

print("Torch CUDA:", torch.version.cuda)
"""

    run_command(f'python -c "{code}"')


def create_python_environment(venv_name: str):
    command = f"python -m venv {venv_name}"

    run_command(command)


def activate_environment():
    command = str(".venv\Scripts\activate")

    run_command(command)


if __name__ == "__main__":
    venv_name = input("Enter your venv name: ")

    create_python_environment(venv_name=venv_name)

    activate_environment()

    install_pytorch()

    install_requirements()

    clone_llama_cpp()

    verify_ollama()

    verify_torch()

    print(f"Successfully initiated venv")