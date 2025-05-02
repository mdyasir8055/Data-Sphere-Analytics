import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and print the output"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Command: {command}")
        print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return False

def setup_git_repository():
    """Set up a Git repository with proper .gitignore configuration"""
    print("Setting up Git repository...")
    
    # Check if Git is installed
    if not run_command("git --version"):
        print("Git is not installed or not in PATH. Please install Git first.")
        return False
    
    # Check if .git directory already exists
    if os.path.exists(".git"):
        print("Git repository already initialized.")
    else:
        # Initialize Git repository
        if not run_command("git init"):
            return False
        print("Git repository initialized successfully.")
    
    # Check if .gitignore exists
    if not os.path.exists(".gitignore"):
        print("Error: .gitignore file not found. Please create it first.")
        return False
    
    # Add .gitignore to Git
    if not run_command("git add .gitignore"):
        return False
    
    # Commit .gitignore
    if not run_command('git commit -m "Add .gitignore file to exclude cache and temp files"'):
        return False
    
    print("\nGit repository setup complete!")
    print("\nTo add your files to Git (excluding those in .gitignore), run:")
    print("git add .")
    print('git commit -m "Initial commit"')
    print("\nTo connect to GitHub, run:")
    print("git remote add origin https://github.com/yourusername/yourrepository.git")
    print("git branch -M main")
    print("git push -u origin main")
    
    return True

if __name__ == "__main__":
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    setup_git_repository()import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and print the output"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Command: {command}")
        print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return False

def setup_git_repository():
    """Set up a Git repository with proper .gitignore configuration"""
    print("Setting up Git repository...")
    
    # Check if Git is installed
    if not run_command("git --version"):
        print("Git is not installed or not in PATH. Please install Git first.")
        return False
    
    # Check if .git directory already exists
    if os.path.exists(".git"):
        print("Git repository already initialized.")
    else:
        # Initialize Git repository
        if not run_command("git init"):
            return False
        print("Git repository initialized successfully.")
    
    # Check if .gitignore exists
    if not os.path.exists(".gitignore"):
        print("Error: .gitignore file not found. Please create it first.")
        return False
    
    # Add .gitignore to Git
    if not run_command("git add .gitignore"):
        return False
    
    # Commit .gitignore
    if not run_command('git commit -m "Add .gitignore file to exclude cache and temp files"'):
        return False
    
    print("\nGit repository setup complete!")
    print("\nTo add your files to Git (excluding those in .gitignore), run:")
    print("git add .")
    print('git commit -m "Initial commit"')
    print("\nTo connect to GitHub, run:")
    print("git remote add origin https://github.com/yourusername/yourrepository.git")
    print("git branch -M main")
    print("git push -u origin main")
    
    return True

if __name__ == "__main__":
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    setup_git_repository()