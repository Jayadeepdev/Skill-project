import shutil
import os

def process_log_file(file_path):
    """
    Saves the file to intermediate and returns True to signal success.
    """
    try:
        # Define where the intermediate signal file will go
        filename = os.path.basename(file_path)
        inter_dir = os.path.join("data", "input")
        os.makedirs(inter_dir, exist_ok=True)
        
        dest = os.path.join(inter_dir, "input.log")
        
        # Copy the file to simulate processing
        shutil.copy(file_path, dest)
        
        print(f"Model I: File saved to intermediate folder.")
        return True 
    except Exception as e:
        print(f"Model I Error: {e}")
        return False