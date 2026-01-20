import os
from src.interface.app_ui import SkillApp
# Make sure these two lines are present:
from src.backend.model_i import process_log_file
from src.backend.model_ii import generate_results


def init_folders():
    folders = ["data/input", "data/output", "assets"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

if __name__ == "__main__":
    init_folders()
    app = SkillApp(
        run_analysis_callback=process_log_file,
        show_result_callback=generate_results
    )
    app.mainloop()