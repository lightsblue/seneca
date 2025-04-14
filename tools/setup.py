import os
import subprocess


def install_dependencies():
    """Install project dependencies."""
    print("Installing dependencies...")
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])


def setup_virtualenv():
    """Set up a virtual environment."""
    print("Setting up virtual environment...")
    subprocess.check_call(["python", "-m", "venv", ".venv"])
    print("Virtual environment created. Activate it with 'source .venv/bin/activate'.")


def main():
    """Main setup function."""
    setup_virtualenv()
    install_dependencies()
    print("Setup complete.")


if __name__ == "__main__":
    main() 