import customtkinter as ctk
from tkinter import filedialog
# from PIL import Image
import os
# import shutil
# import time
import threading

#PyLog Folder
from PyLog.function import parse_log_1
from PyLog.function import prepare_labels_2
from PyLog.function import features_3
from PyLog.function import train_semisup_4
from PyLog.function import predict_semisup_5
from PyLog.function import train_iforest_6
# ==========================================================
# COLOR CONFIGURATION
# ==========================================================
COLOR_APP_BG          = "#121212"  
COLOR_SIDEBAR_BG      = "#000000"  
COLOR_HEADER_BG       = "#121212"  
COLOR_VIZ_CONTAINER   = "#1A1A1A"  
COLOR_GRAPH_CARD      = "#000000"  
COLOR_TEXT_RESULT_BG  = "#000000"  

COLOR_PRIMARY_TEXT    = "#FFFFFF"  
COLOR_MATRIX_GREEN    = "#33FF33"  
COLOR_TITLE_BLUE      = "#1F77B4"  
COLOR_NAV_RED         = "#FF0000"  
# ==========================================================

ctk.set_appearance_mode("dark")

class SkillApp(ctk.CTk):
    def __init__(self, run_analysis_callback, show_result_callback):
        super().__init__()

        # --- Window Configuration ---
        self.title("Model Analysis Interface")
        self.geometry("1300x800")
        self.configure(fg_color=COLOR_APP_BG)

        self.run_analysis_callback = run_analysis_callback
        self.show_result_callback = show_result_callback
        self.selected_file_path = None
        
        self.result_cache = {"text": None, "graphs_ready": False} 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. Header Section ---
        self.header = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color=COLOR_HEADER_BG)
        self.header.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.title_label = ctk.CTkLabel(self.header, text="Model Analysis Interface", 
                                        font=("Arial", 20, "bold"), text_color=COLOR_TITLE_BLUE)
        self.title_label.pack(side="left", padx=20)

        # --- 2. Left Sidebar (Compact Navigation) ---
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=COLOR_SIDEBAR_BG, corner_radius=10)
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="Operations", font=("Arial", 15, "bold")).pack(pady=(10, 0))
        self.status_lbl = ctk.CTkLabel(self.sidebar, text="STATUS: Idle", text_color="grey", font=("Arial", 10, "italic"))
        self.status_lbl.pack(pady=(0, 5))

        self.btn_upload = ctk.CTkButton(self.sidebar, text="Log Upload", height=28, command=self.upload_file)
        self.btn_upload.pack(pady=2, padx=20)
        self.btn_run = ctk.CTkButton(self.sidebar, text="Run Analysis", height=28, state="disabled", command=self.start_analysis_thread)
        self.btn_run.pack(pady=2, padx=20)
        self.btn_show = ctk.CTkButton(self.sidebar, text="Show Result", height=28, state="disabled", command=self.start_result_thread)
        self.btn_show.pack(pady=2, padx=20)

        ctk.CTkLabel(self.sidebar, text="Graphs and Charts", font=("Arial", 13)).pack(pady=(10, 2))
        for name in ["Heat Map", "Bar Graph", "Pie Chart"]:
            btn = ctk.CTkButton(self.sidebar, text=name, height=28, fg_color=COLOR_NAV_RED, 
                                command=lambda n=name: self.load_single_view(n))
            btn.pack(pady=2, padx=20)

        ctk.CTkLabel(self.sidebar, text="Feedback", font=("Arial", 14, "bold")).pack(pady=(15, 2))
        self.feedback_box = ctk.CTkTextbox(self.sidebar, height=400, width=200, fg_color="#111111", 
                                           text_color="white", font=("Consolas", 11), activate_scrollbars=True)
        self.feedback_box.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        # --- 3. Visualization Area ---
        self.viz_main_area = ctk.CTkFrame(self, fg_color=COLOR_VIZ_CONTAINER, corner_radius=15)
        self.viz_main_area.grid(row=1, column=1, sticky="nsew", padx=5, pady=10)
        
        self.viz_top_label = ctk.CTkLabel(self.viz_main_area, text="Visualization Workspace", 
                                          font=("Arial", 13, "italic"), text_color="#555555")
        self.viz_top_label.pack(side="top", pady=5)

        self.viz_watermark = ctk.CTkLabel(self.viz_main_area, text="Visualization", 
                                          font=("Arial", 40, "bold"), text_color="#2A2A2A")
        self.viz_watermark.place(relx=0.5, rely=0.5, anchor="center")

        self.viz_scrollable = ctk.CTkScrollableFrame(self.viz_main_area, fg_color="transparent")
        self.viz_scrollable.pack(expand=True, fill="both", padx=10, pady=10)

        # --- 4. Right Panel ---
        self.result_text = ctk.CTkTextbox(self, width=250, fg_color=COLOR_TEXT_RESULT_BG, text_color=COLOR_MATRIX_GREEN)
        self.result_text.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        self.result_text.insert("0.0", "Result Format:\nWaiting...")
        self.result_text.configure(state="disabled")

        # Startup Messages
        self.update_feedback("SYSTEM: Ready.")
        self.update_feedback("SUGGESTION: Please upload a log file to begin the program.")

    # --- Methods ---

    def update_feedback(self, msg):
        self.feedback_box.insert("end", f"> {msg}\n")
        self.feedback_box.see("end")

    def upload_file(self):
        file = filedialog.askopenfilename()
        if not file:
            self.update_feedback("ERROR: No file selected.")
            self.update_feedback("SUGGESTION: Click 'Dataset Upload' to choose a log file.")
            return
        self.selected_file_path = file
        self.update_feedback(f"CONFIRMATION: {os.path.basename(file)} loaded.")
        self.update_feedback("SUGGESTION: Click 'Run Analysis' to process the log data.")
        self.btn_run.configure(state="normal")

    def start_analysis_thread(self):
        threading.Thread(target=self._run_analysis).start()
    def _run_analysis(self):
        success = self.run_analysis_callback(self.selected_file_path)

        #parse_log_1.py run
        result = parse_log_1.parser()
        if result:
            self.update_feedback("<-- Phase One OK -->\n")
        
        #prepare_labels_2.py run
        result = prepare_labels_2.prepare()
        if result:
            self.update_feedback("<-- Phase Two OK -->\n")

        #features_3.py run
        result=features_3.features()
        if result:
            self.update_feedback("<-- Phase Three OK-->\n")
        
        #train_semisup_4.py run
        result = train_semisup_4.train()
        if result:
            self.update_feedback("<-- Phase Four OK-->\n")

        #predict_semisup_5 run
        result = predict_semisup_5.predict()
        if result:
            self.update_feedback("<-- Phase five OK -->\n")

        #train_iforest_6 run
        result = train_iforest_6.iforest()
        if result:
            self.update_feedback("<-- Final Phase ok-->\n")

        if success:
            self.update_feedback("CONFIRMATION: Analysis complete.")
            self.update_feedback("SUGGESTION: Click 'Show Result' to generate visualizations.")
            self.btn_show.configure(state="normal")

    def start_result_thread(self):
        threading.Thread(target=self._show_results).start()

    def _show_results(self):
        """Loads all graphs vertically with 'Peeking' height for scrolling"""
        if not self.result_cache["text"]:
            text_data, _ = self.show_result_callback()
            self.result_cache["text"] = text_data
        
        self.result_text.configure(state="normal")
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", self.result_cache["text"])
        self.result_text.configure(state="disabled")

        if self.viz_watermark:
            self.viz_watermark.destroy()
            self.viz_watermark = None

        for widget in self.viz_scrollable.winfo_children():
            widget.destroy()

        self.update_feedback("CONFIRMATION: Loading vertical view.")
        graphs = [("Heat Map", "#1F77B4"), ("Bar Graph", "#FF7F0E"), ("Pie Chart", "#2CA02C")]
        
        for name, color in graphs:
            self._create_graph_box(name, color, peak_view=True)
            self.update() 
        
        self.update_feedback("SUGGESTION: Scroll down to see other graphs or use sidebar buttons.")

    def load_single_view(self, name):
        """Shows only one specific graph"""
        if not self.btn_show.cget("state") == "normal":
            self.update_feedback(f"ERROR: Analysis not found. Please upload and run analysis first.")
            return

        for widget in self.viz_scrollable.winfo_children():
            widget.destroy()

        if self.viz_watermark:
            self.viz_watermark.destroy()
            self.viz_watermark = None

        self.update_feedback(f"CONFIRMATION: Showing {name}.")
        color_map = {"Heat Map": "#1F77B4", "Bar Graph": "#FF7F0E", "Pie Chart": "#2CA02C"}
        self._create_graph_box(name, color_map[name], peak_view=True)
        self.update_feedback("SUGGESTION: Click 'Show Result' to restore the full list view.")

    def _create_graph_box(self, name, border_color, peak_view=False):
        """Helper to build a graph box with height set to allow peeking"""
        # 500px is the 'sweet spot' for a peeking effect in an 800px window
        box_height = 500 if peak_view else 450 
        
        box = ctk.CTkFrame(self.viz_scrollable, height=box_height, 
                           corner_radius=20, border_width=2, border_color=border_color, fg_color=COLOR_GRAPH_CARD)
        box.pack(pady=15, padx=10, fill="x")
        box.pack_propagate(False) 

        ctk.CTkLabel(box, text=f"--- {name} ---", font=("Arial", 16, "bold")).pack(pady=10)
        
        inner = ctk.CTkFrame(box, fg_color="#000000", corner_radius=15)
        inner.pack(expand=True, fill="both", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(inner, text=f"{name} Visualization Content", text_color="#555555").pack(expand=True)