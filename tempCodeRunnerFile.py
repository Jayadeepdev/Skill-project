import os
import shutil
from src.interface.app_ui import SkillApp
from src.backend.model_ii import generate_results

def initialize_analysis(file_path):
    """Moves the selected log to the location PyLog expects."""
    try:
        os.makedirs("data/input", exist_ok=True)
        destination = os.path.join("data", "input", "input.log")
        shutil.copy(file_path, destination)
        return True # This sends the 'success' signal to the UI
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    app = SkillApp(
        run_analysis_callback=initialize_analysis, 
        show_result_callback=generate_results
    )
    app.mainloop()