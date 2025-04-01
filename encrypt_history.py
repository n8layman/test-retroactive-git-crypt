#!/usr/bin/env python3
import subprocess
import os
import sys
import time
import shutil

encrypted_folder = 'test2'

def ensure_git_crypt_setup():
    """Ensure .gitattributes is configured for encryption in the root directory."""
    try:
        # Get the git repository root directory
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                            capture_output=True, text=True, check=True)
        repo_root = result.stdout.strip()
        original_dir = os.getcwd()
        
        # Change to the repository root directory
        os.chdir(repo_root)
        print(f"Changed to repository root: {repo_root}")
        
        # Create backup of any existing .gitattributes
        if os.path.exists('.gitattributes'):
            print("Backing up existing .gitattributes")
            shutil.copy('.gitattributes', '.gitattributes.bak')
        
        # Create .gitattributes with special naming first to avoid any potential hooks
        temp_filename = f'.gitattributes.new.{int(time.time())}'
        print(f"Creating temporary file: {temp_filename}")
        with open(temp_filename, 'w') as f:
            f.write(f"{encrypted_folder}/**/* filter=git-crypt diff=git-crypt\n")
        
        # Rename to the actual file
        print(f"Renaming to .gitattributes")
        shutil.move(temp_filename, '.gitattributes')
        
        # Explicitly check if the file exists and show its contents
        if os.path.exists('.gitattributes'):
            print(f".gitattributes successfully created at {os.path.join(repo_root, '.gitattributes')}")
            with open('.gitattributes', 'r') as f:
                print(f"Content: {f.read().strip()}")
        else:
            print("ERROR: .gitattributes was not created!")
            
        # Add and commit the .gitattributes file
        print("Adding .gitattributes to git")
        add_result = subprocess.run(['git', 'add', '.gitattributes'], capture_output=True, text=True)
        print(f"git add output: {add_result.stdout}")
        if add_result.stderr:
            print(f"git add error: {add_result.stderr}")
            
        print("Committing .gitattributes")
        commit_result = subprocess.run(['git', 'commit', '-m', 'Configure git-crypt for encryption of test folder'], 
                                      capture_output=True, text=True)
        print(f"git commit output: {commit_result.stdout}")
        if commit_result.stderr:
            print(f"git commit error: {commit_result.stderr}")
        
        # Change back to the original directory
        os.chdir(original_dir)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def rewrite_history():
    """Use git-filter-repo to rewrite history with encrypted files."""
    # Instead of using --path which keeps ONLY that path, use --path-glob for the files
    # we want to encrypt while preserving the structure of the repo
    command = ['git', 'filter-repo', '--path-glob', f'{encrypted_folder}/**/*', '--path', '.gitattributes']
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")

def main():
    print("\033[92mEnsuring git-crypt is properly configured for 'test' folder...\033[0m")
    ensure_git_crypt_setup()
    
    print("\033[92mRewriting repository history to encrypt files in 'test' folder...\033[0m")
    rewrite_history()
    
    print("\033[92mOperation completed. Check the output to verify file locations.\033[0m")
    print("\033[93mIf everything looks good, you can force push to update the remote repository:\033[0m")
    print("  git push --force-with-lease --set-upstream origin main")

if __name__ == "__main__":
    main()
