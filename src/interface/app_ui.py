import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import os
import threading
import time

# Visualization & Plotting Imports
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================================
# STYLE & COLOR CONFIGURATION
# ==========================================================
COLOR_APP_BG          = "#000000"  
COLOR_BOX_BG          = "#0d0d0d"  
COLOR_MATRIX_GREEN    = "#33FF33"  
COLOR_TITLE_BLUE      = "#1F77B4"  
COLOR_CYAN            = "#00FFFF"
COLOR_BORDER          = "#1a1a1a"  

TAG_SYSTEM_COLOR      = "#5DADE2" 
TAG_CONFIRM_COLOR     = "#58D68D" 
TAG_SUGGEST_COLOR     = "#F5B041" 
TAG_ERROR_COLOR       = "#EC7063" 
# ==========================================================

ctk.set_appearance_mode("dark")

class SkillApp(ctk.CTk):
    def __init__(self, run_analysis_callback, show_result_callback):
        super().__init__()

        # --- Window Setup ---
        self.title("Digit Skill Project")
        self.geometry("1450x900")
        self.configure(fg_color=COLOR_APP_BG)

        self.run_analysis_callback = run_analysis_callback
        self.show_result_callback = show_result_callback
        self.selected_file_path = None
        self.result_cache = {"text": None, "df": None} 
        self.is_processing = False

        # Grid Configuration: (0) Sidebar (1) Viz (2) Text Results
        self.grid_columnconfigure(1, weight=3) 
        self.grid_columnconfigure(2, weight=1) 
        self.grid_rowconfigure(1, weight=1)

        # --- 1. Header (Logo + Title) ---
        self.header = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=COLOR_APP_BG)
        self.header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(10, 0))
        
        logo_path = r"C:\Users\jayad\OneDrive\Desktop\Skill project\Skill-project\assets\logo.png"
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            self.logo_img = ctk.CTkImage(img, size=(45, 45))
            ctk.CTkLabel(self.header, image=self.logo_img, text="").pack(side="left", padx=(10, 15))
        
        self.title_label = ctk.CTkLabel(self.header, text="Digit Skill Project", 
                                        font=("Arial", 32, "bold"), text_color=COLOR_TITLE_BLUE)
        self.title_label.pack(side="left")

        # --- 2. Sidebar (Operations + Graphs + Feedback) ---
        self.sidebar_container = ctk.CTkFrame(self, width=280, fg_color=COLOR_APP_BG)
        self.sidebar_container.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20)

        # A. Operations
        self.op_frame = ctk.CTkFrame(self.sidebar_container, fg_color=COLOR_BOX_BG, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.op_frame.pack(fill="x", pady=(0, 10), ipady=5)
        ctk.CTkLabel(self.op_frame, text="Operations", font=("Arial", 12), text_color="grey").pack(pady=5, padx=15, anchor="w")
        
        self.btn_upload = ctk.CTkButton(self.op_frame, text="Dataset upload", command=self.upload_file)
        self.btn_upload.pack(pady=5, padx=20, fill="x")
        self.btn_run = ctk.CTkButton(self.op_frame, text="Run analysis", state="disabled", command=self.start_analysis_thread)
        self.btn_run.pack(pady=5, padx=20, fill="x")
        self.btn_show = ctk.CTkButton(self.op_frame, text="Show Result", state="disabled", command=self.start_result_thread)
        self.btn_show.pack(pady=5, padx=20, fill="x")

        # B. Graph Menu (Restored Logic)
        self.graph_frame = ctk.CTkFrame(self.sidebar_container, fg_color=COLOR_BOX_BG, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.graph_frame.pack(fill="x", pady=10, ipady=5)
        ctk.CTkLabel(self.graph_frame, text="Graphs and charts", font=("Arial", 12), text_color="grey").pack(pady=5, padx=15, anchor="w")
        
        for g_name in ["Heat map", "Bar graph", "Pie chart"]:
            ctk.CTkButton(self.graph_frame, text=g_name, fg_color="transparent", border_width=1, border_color="red", 
                          command=lambda n=g_name: self.load_single_view(n)).pack(pady=3, padx=20, fill="x")

        # C. Feedback
        self.fb_frame = ctk.CTkFrame(self.sidebar_container, fg_color=COLOR_BOX_BG, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.fb_frame.pack(fill="both", expand=True, pady=(10, 0))
        ctk.CTkLabel(self.fb_frame, text="Feedbacks", font=("Arial", 12, "underline"), text_color="grey").pack(pady=5, padx=15, anchor="w")
        self.feedback_box = ctk.CTkTextbox(self.fb_frame, fg_color="transparent", font=("Consolas", 11))
        self.feedback_box.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.feedback_box.tag_config("SYSTEM", foreground=TAG_SYSTEM_COLOR)
        self.feedback_box.tag_config("CONFIRM", foreground=TAG_CONFIRM_COLOR)
        self.feedback_box.tag_config("SUGGEST", foreground=TAG_SUGGEST_COLOR)
        self.feedback_box.tag_config("ERROR", foreground=TAG_ERROR_COLOR)

        # --- 3. Visualization Area (The Center Workspace) ---
        self.viz_container = ctk.CTkFrame(self, fg_color=COLOR_BOX_BG, corner_radius=15, border_width=2, border_color="#1a1a1a")
        self.viz_container.grid(row=1, column=1, sticky="nsew", padx=10, pady=20)
        
        self.viz_watermark = ctk.CTkLabel(self.viz_container, text="Visualization Area", 
                                          font=("Arial", 40, "italic"), text_color="#1a1a1a")
        self.viz_watermark.place(relx=0.5, rely=0.5, anchor="center")

        self.viz_scrollable = ctk.CTkScrollableFrame(self.viz_container, fg_color="transparent")
        self.viz_scrollable.pack(expand=True, fill="both", padx=10, pady=10)

        # --- 4. Right Panel (Text Results) ---
        self.result_container = ctk.CTkFrame(self, fg_color=COLOR_BOX_BG, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.result_container.grid(row=1, column=2, sticky="nsew", padx=(10, 20), pady=20)
        
        ctk.CTkLabel(self.result_container, text="Result in text format :", font=("Arial", 13, "italic"), text_color="grey").pack(pady=15, padx=15, anchor="nw")
        self.result_text = ctk.CTkTextbox(self.result_container, fg_color="transparent", text_color=COLOR_MATRIX_GREEN, font=("Consolas", 12))
        self.result_text.pack(pady=(0, 15), padx=15, fill="both", expand=True)
        self.result_text.configure(state="disabled")

    def update_feedback(self, category, msg):
        self.feedback_box.insert("end", f"> {category}: ", category)
        self.feedback_box.insert("end", f"{msg}\n")
        self.feedback_box.see("end")

    def upload_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.selected_file_path = file
            self.update_feedback("CONFIRM", "Dataset uploaded.")
            self.btn_run.configure(state="normal")

    def start_analysis_thread(self):
        self.is_processing = True
        threading.Thread(target=self._run_analysis, daemon=True).start()
        threading.Thread(target=self._timer_loop, daemon=True).start()

    def _timer_loop(self):
        start = time.time()
        while self.is_processing:
            elapsed = round(time.time() - start, 1)
            self.title_label.configure(text=f"Digit Skill Project ({elapsed}s)")
            time.sleep(0.1)
        self.title_label.configure(text="Digit Skill Project")

    # --- CORE ANALYSIS LOGIC WITH SYNC HANDSHAKE ---
    def _run_analysis(self):
        self.update_feedback("SYSTEM", "Starting pipeline...")
        try:
            from PyLog.function import parse_log_1, prepare_labels_2, features_3, train_semisup_4, predict_semisup_5, train_iforest_6, evaluate_model
            
            # Phase 1: Parsing
            if parse_log_1.parser():
                self.update_feedback("CONFIRM", "Phase 1: Done.")
                
                # HANDSHAKE: Wait for OS to release the file
                parsed_csv = os.path.join("PyLog", "Csv", "parsed", "parsed.csv")
                retry = 0
                while (not os.path.exists(parsed_csv) or os.path.getsize(parsed_csv) == 0) and retry < 20:
                    time.sleep(0.5)
                    retry += 1
                
                # Phase 2: Labeling
                if prepare_labels_2.prepare():
                    self.update_feedback("CONFIRM", "Phase 2: Done.")
                    
                    # Phase 3: Features
                    features_3.features()
                    self.update_feedback("CONFIRM", "Phase 3: Done.")
                    
                    # Phase 4: Training (Multiclass solver is handled in the PyLog file fix)
                    if train_semisup_4.train():
                        self.update_feedback("CONFIRM", "Phase 4: Done.")
                        
                        # Phase 5 & 6
                        predict_semisup_5.predict()
                        self.update_feedback("CONFIRM", "Phase 5: Done.")
                        train_iforest_6.iforest()
                        self.update_feedback("CONFIRM", "Phase 6: Done.")
            
            # Final Evaluation
            evaluate_model.main()
            self.is_processing = False
            self.update_feedback("CONFIRM", "Analysis Complete.")
            self.update_feedback("SUGGEST", "Visualization ready. Click 'Show Result'.")
            self.btn_show.configure(state="normal")
            
        except Exception as e:
            self.update_feedback("ERROR", f"Logic Error: {str(e)}")
            self.is_processing = False

    def start_result_thread(self):
        threading.Thread(target=self._show_results, daemon=True).start()

    def _show_results(self):
        if not self.result_cache["text"]:
            text_data, df_data = self.show_result_callback()
            self.result_cache["text"], self.result_cache["df"] = text_data, df_data
        
        self.result_text.configure(state="normal")
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", self.result_cache["text"])
        self.result_text.configure(state="disabled")

        if self.viz_watermark: self.viz_watermark.destroy(); self.viz_watermark = None
        for widget in self.viz_scrollable.winfo_children(): widget.destroy()

        for name, color in [("Heat map", "#1F77B4"), ("Bar graph", "#FF7F0E"), ("Pie chart", "#2CA02C")]:
            self._create_graph_box(name, color)

    def load_single_view(self, name):
        if not self.btn_show.cget("state") == "normal": return
        for widget in self.viz_scrollable.winfo_children(): widget.destroy()
        if self.viz_watermark: self.viz_watermark.destroy(); self.viz_watermark = None
        color_map = {"Heat map": "#1F77B4", "Bar graph": "#FF7F0E", "Pie chart": "#2CA02C"}
        self._create_graph_box(name, color_map[name])

    # --- HIGH-CONTRAST GRAPH BOX LOGIC ---
    def _create_graph_box(self, name, border_color):
        box = ctk.CTkFrame(self.viz_scrollable, height=480, corner_radius=15, border_width=2, border_color=border_color, fg_color="#000000")
        box.pack(pady=10, padx=10, fill="x")
        box.pack_propagate(False) 
        
        ctk.CTkLabel(box, text=f"📊 {name}", font=("Arial", 16, "bold"), text_color="white").pack(pady=10)
        
        # Plot styling for high-contrast dark mode
        plt.rcParams.update({
            'text.color': "white", 
            'axes.labelcolor': COLOR_CYAN, 
            'xtick.color': "white", 
            'ytick.color': "white",
            'axes.edgecolor': "#333333"
        })
        
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#000000')
        ax.set_facecolor('#000000')

        df = self.result_cache.get("df")
        if df is not None and not df.empty:
            try:
                if name == "Bar graph":
                    # Sum columns and filter attack names
                    cols = ['dos attack', 'malware attack', 'dns attack', 'fishing attack', 'bruteforce attack']
                    curr = [c for c in cols if c in df.columns]
                    sns.barplot(x=df[curr].sum().index, y=df[curr].sum().values, palette='viridis', ax=ax)
                    plt.xticks(rotation=20)
                elif name == "Pie chart":
                    df['predicted_label'].value_counts().plot.pie(autopct='%1.1f%%', colors=['#33FF33', '#FF3333'], ax=ax)
                    ax.set_ylabel('')
                elif name == "Heat map":
                    sns.heatmap(df.select_dtypes(include=['number']).corr(), annot=True, cmap='magma', fmt=".2f", ax=ax)
            except Exception as e:
                ax.text(0.5, 0.5, f"Data Render Error: {str(e)}", ha='center', color="red")
        else:
            ax.text(0.5, 0.5, "Waiting for Analysis Results...", ha='center', color="grey")

        canvas = FigureCanvasTkAgg(fig, master=box)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=15, pady=(0, 15))
        plt.close(fig)