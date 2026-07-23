import os
import re
import json
import shlex
import shutil
import time
import tempfile
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

class VideoLoopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TC Smart Video Loop Generator")
        self.root.geometry("850x700")
        self.root.minsize(800, 650)
        
        # Color Palette - Premium Modern Dark Mode
        self.bg_color = "#1e1e2e"       # Deep Slate Blue/Gray
        self.card_color = "#252538"     # Lighter Slate Card
        self.accent_color = "#39fdc0"   # Cyan/Teal Accent
        self.text_color = "#cdd6f4"     # Soft light gray text
        self.text_dim = "#a6adc8"      # Muted gray text
        self.error_color = "#f38ba8"    # Pastel Red
        
        # Application State
        self.source_path = ""
        self.output_path = ""
        self.working_dir = ""
        self.video_info = None
        self.processing_thread = None
        self.current_process = None
        self.temp_dir_obj = None
        self.cancel_requested = False
        
        # Apply Styles
        self.setup_styles()
        self.build_ui()
        self.check_system_dependencies()

    def setup_styles(self):
        self.root.configure(bg=self.bg_color)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frames and elements
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color, relief="flat")
        
        # Label Styles
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Helvetica", 10))
        style.configure("Card.TLabel", background=self.card_color, foreground=self.text_color, font=("Helvetica", 10))
        style.configure("Header.TLabel", background=self.bg_color, foreground=self.accent_color, font=("Helvetica", 16, "bold"))
        style.configure("Section.TLabel", background=self.card_color, foreground=self.accent_color, font=("Helvetica", 11, "bold"))
        
        # Checkbutton / Radiobutton
        style.configure("TCheckbutton", background=self.card_color, foreground=self.text_color, font=("Helvetica", 10))
        style.map("TCheckbutton", background=[('active', self.card_color)], foreground=[('active', self.accent_color)])
        
        style.configure("TRadiobutton", background=self.card_color, foreground=self.text_color, font=("Helvetica", 10))
        style.map("TRadiobutton", background=[('active', self.card_color)], foreground=[('active', self.accent_color)])
        
        # Button Styles
        style.configure("TButton", font=("Helvetica", 10, "bold"), borderwidth=0, focuscolor="none")
        style.configure("Accent.TButton", background=self.accent_color, foreground=self.bg_color)
        style.map("Accent.TButton", background=[('active', '#2ae2ab'), ('disabled', '#555566')], foreground=[('disabled', '#888888')])
        
        style.configure("Secondary.TButton", background="#313244", foreground=self.text_color)
        style.map("Secondary.TButton", background=[('active', '#45475a')])

        style.configure("Cancel.TButton", background=self.error_color, foreground=self.bg_color)
        style.map("Cancel.TButton", background=[('active', '#e06c75')])

        # Entry Style
        style.configure("TEntry", fieldbackground="#313244", foreground=self.text_color, insertcolor=self.text_color)

    def build_ui(self):
        # Outer Padding Frame
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Header Area
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        header_lbl = ttk.Label(header_frame, text="⚡ TC Smart Video Loop Generator", style="Header.TLabel")
        header_lbl.pack(anchor="w")
        
        desc_lbl = ttk.Label(header_frame, text="Creates long-duration seamless loops with crossfades instantly. Renders small tiles to achieve 100x speeds.", style="TLabel")
        desc_lbl.pack(anchor="w", pady=(2, 0))
        desc_lbl.configure(foreground=self.text_dim)

        # Left/Right Column Layout
        cols_frame = ttk.Frame(main_frame)
        cols_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel (Controls & Inputs)
        left_panel = ttk.Frame(cols_frame, width=420)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Right Panel (Console & Progress Logging)
        right_panel = ttk.Frame(cols_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- LEFT PANEL CONTENTS ---
        
        # CARD A: Files Selection
        file_card = ttk.Frame(left_panel, style="Card.TFrame", padding=12)
        file_card.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_card, text="1. Select Video Assets", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        
        # Source File
        src_btn_frame = ttk.Frame(file_card, style="Card.TFrame")
        src_btn_frame.pack(fill=tk.X, pady=2)
        self.src_btn = ttk.Button(src_btn_frame, text="Choose Source", style="Secondary.TButton", command=self.browse_source)
        self.src_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.src_lbl = ttk.Label(src_btn_frame, text="No source video selected", style="Card.TLabel")
        self.src_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.src_lbl.configure(foreground=self.text_dim)
        
        # Target File
        tgt_btn_frame = ttk.Frame(file_card, style="Card.TFrame")
        tgt_btn_frame.pack(fill=tk.X, pady=(8, 2))
        self.tgt_btn = ttk.Button(tgt_btn_frame, text="Choose Output", style="Secondary.TButton", command=self.browse_output)
        self.tgt_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.tgt_lbl = ttk.Label(tgt_btn_frame, text="No destination selected", style="Card.TLabel")
        self.tgt_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.tgt_lbl.configure(foreground=self.text_dim)

        # Working Directory (for temp/intermediate render files)
        work_btn_frame = ttk.Frame(file_card, style="Card.TFrame")
        work_btn_frame.pack(fill=tk.X, pady=(8, 2))
        self.work_btn = ttk.Button(work_btn_frame, text="Choose Working Dir", style="Secondary.TButton", command=self.browse_working_dir)
        self.work_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.work_lbl = ttk.Label(work_btn_frame, text="No working directory selected", style="Card.TLabel")
        self.work_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.work_lbl.configure(foreground=self.text_dim)

        # Free space indicator for the chosen working directory
        self.work_space_lbl = ttk.Label(file_card, text="", style="Card.TLabel")
        self.work_space_lbl.pack(anchor="w", pady=(2, 0))
        self.work_space_lbl.configure(foreground=self.text_dim, font=("Helvetica", 9, "italic"))

        # File Stats Display
        self.stats_lbl = ttk.Label(file_card, text="", style="Card.TLabel")
        self.stats_lbl.pack(anchor="w", pady=(8, 0))
        self.stats_lbl.configure(foreground=self.accent_color, font=("Helvetica", 9, "italic"))

        # CARD B: Targets & Strategy Settings
        settings_card = ttk.Frame(left_panel, style="Card.TFrame", padding=12)
        settings_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(settings_card, text="2. Configure Loop Settings", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        
        # Grid layout for specific inputs
        grid_frame = ttk.Frame(settings_card, style="Card.TFrame")
        grid_frame.pack(fill=tk.X, pady=4)
        
        # Expected Output Duration
        ttk.Label(grid_frame, text="Target Duration:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        duration_input_frame = ttk.Frame(grid_frame, style="Card.TFrame")
        duration_input_frame.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        self.hours_var = tk.StringVar(value="1")
        self.mins_var = tk.StringVar(value="0")
        self.secs_var = tk.StringVar(value="0")
        
        self.entry_hr = ttk.Entry(duration_input_frame, textvariable=self.hours_var, width=4, justify="center")
        self.entry_hr.pack(side=tk.LEFT)
        ttk.Label(duration_input_frame, text="h", style="Card.TLabel").pack(side=tk.LEFT, padx=(2, 8))
        
        self.entry_min = ttk.Entry(duration_input_frame, textvariable=self.mins_var, width=4, justify="center")
        self.entry_min.pack(side=tk.LEFT)
        ttk.Label(duration_input_frame, text="m", style="Card.TLabel").pack(side=tk.LEFT, padx=(2, 8))
        
        self.entry_sec = ttk.Entry(duration_input_frame, textvariable=self.secs_var, width=4, justify="center")
        self.entry_sec.pack(side=tk.LEFT)
        ttk.Label(duration_input_frame, text="s", style="Card.TLabel").pack(side=tk.LEFT, padx=(2, 0))

        # Video Crossfade Toggles
        self.video_fade_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid_frame, text="Video Crossfade", variable=self.video_fade_enabled, command=self.toggle_transitions).grid(row=1, column=0, sticky="w", pady=5)
        
        video_fade_frame = ttk.Frame(grid_frame, style="Card.TFrame")
        video_fade_frame.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.video_fade_secs = tk.StringVar(value="2.0")
        self.entry_vfade = ttk.Entry(video_fade_frame, textvariable=self.video_fade_secs, width=6, justify="center")
        self.entry_vfade.pack(side=tk.LEFT)
        ttk.Label(video_fade_frame, text="seconds", style="Card.TLabel").pack(side=tk.LEFT, padx=(5, 10))
        
        # Audio Crossfade Toggles
        self.audio_fade_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid_frame, text="Audio Crossfade", variable=self.audio_fade_enabled, command=self.toggle_transitions).grid(row=2, column=0, sticky="w", pady=5)
        
        audio_fade_frame = ttk.Frame(grid_frame, style="Card.TFrame")
        audio_fade_frame.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.audio_fade_secs = tk.StringVar(value="2.0")
        self.entry_afade = ttk.Entry(audio_fade_frame, textvariable=self.audio_fade_secs, width=6, justify="center")
        self.entry_afade.pack(side=tk.LEFT)
        ttk.Label(audio_fade_frame, text="seconds", style="Card.TLabel").pack(side=tk.LEFT, padx=(5, 0))

        # Transition Effects selector
        ttk.Label(grid_frame, text="Transition Effect:", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        self.effect_var = tk.StringVar(value="fade")
        self.effect_combo = ttk.Combobox(grid_frame, textvariable=self.effect_var, width=12, state="readonly")
        # List of fast/native crossfade transitions supported inside xfade
        self.effect_combo['values'] = ("fade", "dissolve", "wipeleft", "wiperight", "slideup", "slidedown", "circleopen")
        self.effect_combo.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # Loop Strategies Selector
        ttk.Label(settings_card, text="Looping Mode Strategy:", style="Card.TLabel").pack(anchor="w", pady=(10, 5))
        
        self.strategy_var = tk.StringVar(value="truncate")
        
        r_trunc = ttk.Radiobutton(settings_card, text="Precise Duration (Truncate with Ending Fade-out)", 
                                  variable=self.strategy_var, value="truncate", command=self.toggle_fadeout_setting)
        r_trunc.pack(anchor="w", pady=2)
        
        r_closest = ttk.Radiobutton(settings_card, text="Perfect Match Loop Limit (Close as possible, no truncation)", 
                                    variable=self.strategy_var, value="closest", command=self.toggle_fadeout_setting)
        r_closest.pack(anchor="w", pady=2)

        # Dynamic End Fade-out setting
        self.fadeout_frame = ttk.Frame(settings_card, style="Card.TFrame")
        self.fadeout_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(self.fadeout_frame, text="Final Video Fadeout Ending:", style="Card.TLabel").pack(side=tk.LEFT, padx=(20, 10))
        self.fadeout_secs_var = tk.StringVar(value="3.0")
        self.entry_fadeout = ttk.Entry(self.fadeout_frame, textvariable=self.fadeout_secs_var, width=6, justify="center")
        self.entry_fadeout.pack(side=tk.LEFT)
        ttk.Label(self.fadeout_frame, text="seconds", style="Card.TLabel").pack(side=tk.LEFT, padx=(5, 0))

        # --- RIGHT PANEL CONTENTS (CONSOLE LOG & PROCESS CONTROLS) ---
        
        console_card = ttk.Frame(right_panel, style="Card.TFrame", padding=12)
        console_card.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(console_card, text="🎬 Processing Pipeline & Terminal Logs", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        
        # Scrolled Text Box simulating standard terminal output
        self.log_box = ScrolledText(console_card, bg="#11111b", fg=self.text_color, insertbackground=self.text_color,
                                    font=("Consolas", 9), wrap=tk.WORD, borderwidth=0, highlightthickness=0)
        self.log_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Default instruction logs
        self.write_log("Ready to generate. Select a source video file to analyze properties...\n")
        
        # Process Progress Section
        self.progress_lbl = ttk.Label(console_card, text="Waiting for setup...", style="Card.TLabel")
        self.progress_lbl.pack(anchor="w", pady=(0, 2))
        
        self.progress_bar = ttk.Progressbar(console_card, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Build execution buttons (Start / Abort)
        exec_frame = ttk.Frame(console_card, style="Card.TFrame")
        exec_frame.pack(fill=tk.X)
        
        self.run_btn = ttk.Button(exec_frame, text="⚡ START RENDERING PROCESS", style="Accent.TButton", command=self.start_processing)
        self.run_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.cancel_btn = ttk.Button(exec_frame, text="🛑 ABORT RENDER", style="Cancel.TButton", state="disabled", command=self.cancel_processing)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 2))

    def write_log(self, text):
        self.root.after(0, self._write_log_ui, text)

    def _write_log_ui(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, text)
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def toggle_transitions(self):
        v_state = "normal" if self.video_fade_enabled.get() else "disabled"
        self.entry_vfade.configure(state=v_state)
        
        a_state = "normal" if self.audio_fade_enabled.get() else "disabled"
        self.entry_afade.configure(state=a_state)

    def toggle_fadeout_setting(self):
        state = "normal" if self.strategy_var.get() == "truncate" else "disabled"
        self.entry_fadeout.configure(state=state)

    def check_system_dependencies(self):
        ffmpeg_exists = shutil.which("ffmpeg") is not None
        ffprobe_exists = shutil.which("ffprobe") is not None
        
        if not ffmpeg_exists or not ffprobe_exists:
            self.write_log("🚨 DEPENDENCY ERROR: FFmpeg or FFprobe binaries were not found on your system path.\n")
            self.write_log("Please download and configure FFmpeg, ensuring it is in your Environment Variable PATH.\n")
            messagebox.showerror(
                "System Error", 
                "FFmpeg/FFprobe binaries not found on your system path!\n\n"
                "Please download FFmpeg and add it to your PATH variables so this script can interact with it."
            )
            self.run_btn.configure(state="disabled")

    def browse_source(self):
        file_path = filedialog.askopenfilename(
            title="Select Source Video Clip",
            filetypes=[("Video Files", "*.mp4 *.mkv *.mov *.avi *.webm *.flv *.m4v")]
        )
        if file_path:
            self.source_path = file_path
            short_name = os.path.basename(file_path)
            self.src_lbl.configure(text=short_name, foreground=self.text_color)
            self.write_log(f"Selected source clip: {file_path}\nAnalyzing properties via FFprobe...\n")
            
            threading.Thread(target=self.analyze_source_async, daemon=True).start()

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Choose Output Destination",
            defaultextension=".mp4",
            filetypes=[("MPEG-4 Video", "*.mp4")]
        )
        if file_path:
            self.output_path = file_path
            self.tgt_lbl.configure(text=os.path.basename(file_path), foreground=self.text_color)
            self.write_log(f"Target destination: {file_path}\n")

    def browse_working_dir(self):
        dir_path = filedialog.askdirectory(
            title="Select Working Directory (for temporary render files)"
        )
        if dir_path:
            self.working_dir = dir_path
            self.work_lbl.configure(text=dir_path, foreground=self.text_color)
            self.write_log(f"Working directory set to: {dir_path}\n")
            self.update_working_dir_space()

    def update_working_dir_space(self):
        if not self.working_dir:
            self.work_space_lbl.configure(text="")
            return
        try:
            usage = shutil.disk_usage(self.working_dir)
            free_gb = usage.free / (1024 ** 3)
            self.work_space_lbl.configure(text=f"💾 {free_gb:.1f} GB free on this drive")
            if free_gb < 5:
                self.work_space_lbl.configure(foreground=self.error_color)
            else:
                self.work_space_lbl.configure(foreground=self.text_dim)
        except Exception:
            self.work_space_lbl.configure(text="")

    def analyze_source_async(self):
        try:
            self.video_info = self.get_video_info(self.source_path)
            self.root.after(0, self.update_source_details)
        except Exception as e:
            err_msg = str(e)
            self.root.after(0, lambda msg=err_msg: self.write_log(f"❌ Error reading file metadata: {msg}\n"))
            self.root.after(0, lambda msg=err_msg: messagebox.showerror("Read Error", f"Failed to analyze source clip properties:\n{msg}"))

    def get_video_info(self, file_path):
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_format',
            '-show_streams',
            '-of', 'json'
        ]
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        result = subprocess.run(cmd + [file_path], capture_output=True, text=True, startupinfo=startupinfo, encoding='utf-8')
        if result.returncode != 0:
            raise Exception("FFprobe failed to analyze file properties.")
        
        data = json.loads(result.stdout)
        
        duration = float(data.get('format', {}).get('duration', 0))
        
        video_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
        
        if not video_stream:
            raise Exception("No active video stream found in the source asset.")
            
        fps_str = video_stream.get('r_frame_rate', '')
        if not fps_str or fps_str == '0/0':
            fps_str = video_stream.get('avg_frame_rate', '30/1')
        if '/' in fps_str:
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den != 0 else 30.0
        else:
            try:
                fps = float(fps_str)
            except ValueError:
                fps = 30.0
                fps_str = "30"
            fps_str = f"{fps_str}/1"
            
        width = int(video_stream.get('width', 1920))
        height = int(video_stream.get('height', 1080))
        
        sample_rate = 44100
        channels = 2
        if audio_stream:
            sample_rate = int(audio_stream.get('sample_rate', 44100))
            channels = int(audio_stream.get('channels', 2))
            
        return {
            'duration': duration,
            'fps': fps,
            'fps_str': fps_str,
            'width': width,
            'height': height,
            'sample_rate': sample_rate,
            'channels': channels,
            'has_audio': audio_stream is not None
        }

    def update_source_details(self):
        if not self.video_info:
            return
            
        mins, secs = divmod(self.video_info['duration'], 60)
        hrs, mins = divmod(mins, 60)
        dur_str = f"{int(hrs):02d}:{int(mins):02d}:{secs:05.2f}"
        
        stats = f"📏 Resolution: {self.video_info['width']}x{self.video_info['height']} | ⏱️ Clip Duration: {dur_str} | 🎥 Frame Rate: {self.video_info['fps']:.2f} fps | 🔊 Audio: {'Yes' if self.video_info['has_audio'] else 'No'}"
        self.stats_lbl.configure(text=stats)
        self.write_log(f"✅ Analysis Complete! Source is active. {self.video_info['width']}x{self.video_info['height']} at {self.video_info['fps']:.2f}fps.\n")

    def format_concat_path(self, path):
        safe_path = path.replace('\\', '/')
        safe_path = safe_path.replace("'", "'\\''")
        return f"file '{safe_path}'"

    def run_command(self, cmd, desc, progress_weight, current_base_progress, duration_hint=0.0):
        if self.cancel_requested:
            raise Exception("Cancelled by user.")
        self.root.after(0, lambda: self.progress_lbl.configure(text=desc))
        self.write_log(f"Executing: {shlex.join(cmd)}\n")
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        self.current_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            startupinfo=startupinfo,
            encoding='utf-8'
        )
        
        time_regex = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
        sub_render_duration = duration_hint
            
        while True:
            line = self.current_process.stdout.readline()
            if not line:
                break
                
            self.write_log(line)
            
            if sub_render_duration > 0:
                match = time_regex.search(line)
                if match:
                    hours, minutes, seconds = match.groups()
                    elapsed_secs = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    step_progress = min(100.0, max(0.0, (elapsed_secs / sub_render_duration) * 100))
                    
                    overall_progress = current_base_progress + (step_progress * (progress_weight / 100.0))
                    self.root.after(0, lambda p=overall_progress: self.progress_bar.configure(value=p))
                    
        self.current_process.wait()
        ret_code = self.current_process.returncode
        self.current_process = None
        return ret_code == 0

    def start_processing(self):
        if not self.source_path or not self.video_info:
            messagebox.showerror("Error", "Please select a valid source video file first.")
            return
        if not self.output_path:
            messagebox.showerror("Error", "Please select your final export path.")
            return
        if not self.working_dir:
            messagebox.showerror("Error", "Please select a working directory for temporary render files.")
            return
            
        try:
            hr = float(self.hours_var.get() or 0)
            mn = float(self.mins_var.get() or 0)
            sc = float(self.secs_var.get() or 0)
            self.total_requested_secs = (hr * 3600) + (mn * 60) + sc
        except ValueError:
            messagebox.showerror("Error", "Target Duration inputs must be numeric.")
            return
            
        if self.total_requested_secs <= 0:
            messagebox.showerror("Error", "Target Duration must be greater than zero.")
            return

        try:
            self.v_fade_secs = float(self.video_fade_secs.get() or 0) if self.video_fade_enabled.get() else 0.0
            self.a_fade_secs = float(self.audio_fade_secs.get() or 0) if self.audio_fade_enabled.get() else 0.0
        except ValueError:
            messagebox.showerror("Error", "Video/Audio crossfade duration inputs must be numeric.")
            return
        
        self.crossfade_secs = max(self.v_fade_secs, self.a_fade_secs)
        
        source_dur = self.video_info['duration']
        
        if self.crossfade_secs >= source_dur / 2:
            messagebox.showerror(
                "Overlap Bound Reached", 
                f"Requested crossfade transition ({self.crossfade_secs}s) cannot exceed half the source clip duration ({source_dur/2:.2f}s).\n\n"
                "Please shorten your transition times or select a longer source file."
            )
            return

        self.cancel_requested = False
        self.run_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.src_btn.configure(state="disabled")
        self.tgt_btn.configure(state="disabled")
        self.progress_bar.configure(value=0)
        
        self.processing_thread = threading.Thread(target=self.run_pipeline, daemon=True)
        self.processing_thread.start()

    def cancel_processing(self):
        self.cancel_requested = True
        if self.current_process:
            self.current_process.terminate()
            self.write_log("\n🛑 Process termination signal sent. Cleaning up tracks...\n")
        else:
            self.write_log("\n🛑 Cancel requested. Stopping after the current step...\n")
        self.cancel_btn.configure(state="disabled")

    def reset_ui_after_processing(self):
        self.run_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.src_btn.configure(state="normal")
        self.tgt_btn.configure(state="normal")
        self.progress_lbl.configure(text="Pipeline Idle")
        
        if self.temp_dir_obj:
            try:
                self.temp_dir_obj.cleanup()
            except Exception:
                pass
            self.temp_dir_obj = None

    def format_duration_human(self, seconds):
        seconds = max(0, float(seconds))
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds - hours * 3600 - minutes * 60

        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if hours == 0 and minutes == 0:
            parts.append(f"{secs:.1f} second{'s' if round(secs, 1) != 1.0 else ''}")
        elif secs >= 1:
            secs_int = round(secs)
            parts.append(f"{secs_int} second{'s' if secs_int != 1 else ''}")
        return " ".join(parts)

    def run_pipeline(self):
        pipeline_start_time = time.time()
        try:
            self.temp_dir_obj = tempfile.TemporaryDirectory(prefix="video_loop_", dir=self.working_dir)
            temp_dir = self.temp_dir_obj.name
            self.write_log(f"📁 Using working directory for temp/render files: {temp_dir}\n")
            
            source_dur = self.video_info['duration']
            C = self.crossfade_secs
            T = self.total_requested_secs
            mode = self.strategy_var.get()
            
            self.write_log(f"--- Starting Render Pipeline ---\n")
            self.write_log(f"Source: {source_dur:.2f}s | Crossfade: {C:.2f}s | Target: {T:.2f}s | Mode: {mode}\n")

            if self.video_fade_enabled.get() and self.audio_fade_enabled.get() and abs(self.v_fade_secs - self.a_fade_secs) > 1e-6:
                self.write_log(
                    f"⚠️ Video fade ({self.v_fade_secs:.2f}s) and audio fade ({self.a_fade_secs:.2f}s) differ. "
                    f"Both share one {C:.2f}s transition window, so the shorter of the two will actually run "
                    f"for the full {C:.2f}s.\n"
                )

            effective_loop_duration = (source_dur - C) if C > 0 else source_dur

            if mode == "truncate":
                full_loops = int(T // effective_loop_duration)
                R = T - (full_loops * effective_loop_duration)
                if R < 1e-6:
                    R = 0.0
            else:  # closest set limit
                full_loops = max(1, round(T / effective_loop_duration))
                R = 0.0
                if full_loops == 1 and T < effective_loop_duration:
                    self.write_log(
                        "⚠️ Requested duration is shorter than one full loop cycle — output will be a single "
                        "truncated playthrough with no seamless loop closure.\n"
                    )

            self.write_log(f"Calculated full loop cycles: {full_loops} | Truncated remainder: {R:.2f}s\n")
            if mode == "truncate" and R > 0:
                self.write_log(f"Truncated remainder: {R:.2f}s with ending fade-out.\n")

            normalized_path = os.path.join(temp_dir, "normalized.mp4")
            intro_path = os.path.join(temp_dir, "intro.mp4")
            tail_path = os.path.join(temp_dir, "tail.mp4")
            head_path = os.path.join(temp_dir, "head.mp4")
            trans_path = os.path.join(temp_dir, "transition_tile.mp4")
            middle_path = os.path.join(temp_dir, "middle.mp4")
            block_b_path = os.path.join(temp_dir, "block_b.mp4")
            block_b_raw_path = os.path.join(temp_dir, "block_b_raw.mp4")
            last_block_path = os.path.join(temp_dir, "last_block.mp4")
            
            codec_v = ['-c:v', 'libx264', '-bf', '0', '-pix_fmt', 'yuv420p', '-r', self.video_info['fps_str'], '-s', f"{self.video_info['width']}x{self.video_info['height']}"]
            codec_a = ['-c:a', 'aac', '-ar', str(self.video_info['sample_rate']), '-ac', str(self.video_info['channels'])] if self.video_info['has_audio'] else []

            # STEP 0
            self.write_log("🧠 Normalizing source & pinning keyframes at loop boundaries (one-time encode pass)...\n")
            cmd_normalize = ['ffmpeg', '-y', '-i', self.source_path]
            if C > 0:
                cmd_normalize += ['-force_key_frames', f"{C},{effective_loop_duration}"]
            cmd_normalize += codec_v + codec_a + [normalized_path]
            if not self.run_command(cmd_normalize, "Normalizing source (single encode pass)...",
                                     progress_weight=45, current_base_progress=0, duration_hint=source_dur):
                raise Exception("Failed to normalize source video.")

            need_loop_pieces = C > 0 and full_loops >= 1

            # CASE A: Seamless Transitions (Crossfade > 0)
            if need_loop_pieces:
                # STEP 1
                self.write_log("🎥 Slicing Intro Segment (stream copy)...\n")
                cmd_intro = ['ffmpeg', '-y', '-ss', '0', '-to', f"{effective_loop_duration}", '-i', normalized_path, '-c', 'copy', intro_path]
                if not self.run_command(cmd_intro, "Building Intro Slice...", progress_weight=1, current_base_progress=45):
                    raise Exception("Failed to build Intro Segment.")

                # STEP 2
                self.write_log("🎞️ Slicing Loop Tail boundary (stream copy)...\n")
                cmd_tail = ['ffmpeg', '-y', '-ss', f"{effective_loop_duration}", '-to', f"{source_dur}", '-i', normalized_path, '-c', 'copy', tail_path]
                if not self.run_command(cmd_tail, "Slicing Loop Tail...", progress_weight=1, current_base_progress=46):
                    raise Exception("Failed to slice Loop Tail.")

                # STEP 3
                self.write_log("🎞️ Slicing Loop Head boundary (stream copy)...\n")
                cmd_head = ['ffmpeg', '-y', '-ss', '0', '-to', f"{C}", '-i', normalized_path, '-c', 'copy', head_path]
                if not self.run_command(cmd_head, "Slicing Loop Head...", progress_weight=1, current_base_progress=47):
                    raise Exception("Failed to slice Loop Head.")

                # STEP 4
                self.write_log("🔄 Generating transition boundary (re-encoding blend)...\n")
                v_trans = self.video_fade_enabled.get()
                a_trans = self.audio_fade_enabled.get()
                effect = self.effect_var.get()

                filter_complex = []
                map_args = []
                
                if v_trans:
                    filter_complex.append(f"[0:v][1:v]xfade=transition={effect}:duration={C}:offset=0[out_v]")
                    map_args.extend(["-map", "[out_v]"])
                else:
                    filter_complex.append(f"[0:v][1:v]concat=n=2:v=1:a=0[out_v]")
                    map_args.extend(["-map", "[out_v]"])
                    
                if self.video_info['has_audio']:
                    filter_complex.append(f"[2:a]atrim=start={effective_loop_duration}:end={source_dur},asetpts=PTS-STARTPTS[a_tail]")
                    filter_complex.append(f"[3:a]atrim=start=0:end={C},asetpts=PTS-STARTPTS[a_head]")
                    if a_trans:
                        filter_complex.append(f"[a_tail][a_head]acrossfade=d={C}[out_a]")
                        map_args.extend(["-map", "[out_a]"])
                    else:
                        filter_complex.append(f"[a_tail][a_head]concat=n=2:v=0:a=1[out_a]")
                        map_args.extend(["-map", "[out_a]"])

                cmd_trans = ['ffmpeg', '-y', '-i', tail_path, '-i', head_path, '-i', normalized_path, '-i', normalized_path, '-filter_complex', "; ".join(filter_complex)] + map_args + codec_v + codec_a + [trans_path]
                if not self.run_command(cmd_trans, "Generating transition_tile.mp4...", progress_weight=15, current_base_progress=48, duration_hint=C):
                    raise Exception("Failed to build seamless transition tile.")

                # STEP 4b
                block_b_audio_path = os.path.join(temp_dir, "block_b_audio.m4a")
                if self.video_info['has_audio']:
                    self.write_log("🎧 Building continuous block_b audio track (no internal splice)...\n")
                    audio_filter = [
                        f"[0:a]atrim=start={effective_loop_duration}:end={source_dur},asetpts=PTS-STARTPTS[a_tail]",
                        f"[1:a]atrim=start=0:end={C},asetpts=PTS-STARTPTS[a_head]",
                    ]
                    if a_trans:
                        audio_filter.append(f"[a_tail][a_head]acrossfade=d={C}[a_trans]")
                    else:
                        audio_filter.append(f"[a_tail][a_head]concat=n=2:v=0:a=1[a_trans]")
                    audio_filter.append(f"[2:a]atrim=start={C}:end={effective_loop_duration},asetpts=PTS-STARTPTS[a_middle]")
                    audio_filter.append(f"[a_trans][a_middle]concat=n=2:v=0:a=1[out_a]")

                    cmd_block_b_audio = ['ffmpeg', '-y', '-i', normalized_path, '-i', normalized_path, '-i', normalized_path,
                                          '-filter_complex', "; ".join(audio_filter), '-map', '[out_a]'] + codec_a + [block_b_audio_path]
                    if not self.run_command(cmd_block_b_audio, "Building block_b audio track...", progress_weight=2, current_base_progress=61, duration_hint=effective_loop_duration):
                        raise Exception("Failed to build continuous block_b audio track.")

                # STEP 5
                self.write_log("🎞️ Slicing Middle Slice (stream copy)...\n")
                cmd_middle = ['ffmpeg', '-y', '-ss', f"{C}", '-to', f"{effective_loop_duration}", '-i', normalized_path, '-c', 'copy', middle_path]
                if not self.run_command(cmd_middle, "Slicing Loop Middle...", progress_weight=1, current_base_progress=63):
                    raise Exception("Failed to slice Loop Middle.")

                # STEP 6
                self.write_log("🧱 Merging transition tile with middle block near-instantaneously...\n")
                concat_block_b_list = os.path.join(temp_dir, "concat_block_b.txt")
                with open(concat_block_b_list, "w", encoding="utf-8") as f:
                    f.write(f"{self.format_concat_path(trans_path)}\n")
                    f.write(f"{self.format_concat_path(middle_path)}\n")
                
                cmd_block_b = ['ffmpeg', '-y', '-safe', '0', '-f', 'concat', '-i', concat_block_b_list, '-c', 'copy', block_b_raw_path]
                if not self.run_command(cmd_block_b, "Assembling block_b.mp4...", progress_weight=1, current_base_progress=64):
                    raise Exception("Failed to merge seamless tile sections.")

                # STEP 6b
                self.write_log("✂️ Assembling final block_b (clean audio + clamped duration)...\n")
                if self.video_info['has_audio']:
                    cmd_block_b_final = ['ffmpeg', '-y', '-i', block_b_raw_path, '-i', block_b_audio_path,
                                          '-map', '0:v', '-map', '1:a', '-c', 'copy', '-t', f"{effective_loop_duration}", block_b_path]
                else:
                    cmd_block_b_final = ['ffmpeg', '-y', '-i', block_b_raw_path, '-c', 'copy', '-t', f"{effective_loop_duration}", block_b_path]
                if not self.run_command(cmd_block_b_final, "Assembling block_b.mp4...", progress_weight=1, current_base_progress=65, duration_hint=effective_loop_duration):
                    raise Exception("Failed to assemble final block_b.")

            # STEP 7
            if mode == "truncate" and R > 0:
                self.write_log("🔚 Generating Truncated Ending Tile with Fade-out...\n")
                f_out_dur = min(float(self.fadeout_secs_var.get() or 3), R)
                fade_start = R - f_out_dur

                vf_fade = f"trim=start=0:end={R},setpts=PTS-STARTPTS,fade=t=out:st={fade_start}:d={f_out_dur}"
                af_fade = f"atrim=start=0:end={R},asetpts=PTS-STARTPTS,afade=t=out:st={fade_start}:d={f_out_dur}"

                source_for_ending = block_b_path if need_loop_pieces else normalized_path

                cmd_last_block = ['ffmpeg', '-y', '-i', source_for_ending, '-vf', vf_fade]
                if self.video_info['has_audio']:
                    cmd_last_block += ['-af', af_fade]
                cmd_last_block += codec_v + codec_a + [last_block_path]

                if not self.run_command(cmd_last_block, "Generating Truncated Fadeout End...", progress_weight=14, current_base_progress=66, duration_hint=R):
                    raise Exception("Failed to build Ending Segment.")

            # STEP 8
            self.write_log("📝 Formatting manifest for lossless fast concat stitch...\n")
            concat_list_path = os.path.join(temp_dir, "concat_list.txt")
            manifest_piece_count = 0
            
            with open(concat_list_path, "w", encoding="utf-8") as f:
                if C > 0:
                    if need_loop_pieces:
                        f.write(f"{self.format_concat_path(intro_path)}\n")
                        manifest_piece_count += 1
                        for _ in range(full_loops - 1):
                            f.write(f"{self.format_concat_path(block_b_path)}\n")
                            manifest_piece_count += 1
                        if mode == "truncate" and R > 0:
                            f.write(f"{self.format_concat_path(last_block_path)}\n")
                            manifest_piece_count += 1
                    else:
                        f.write(f"{self.format_concat_path(last_block_path)}\n")
                        manifest_piece_count += 1
                else:
                    for _ in range(full_loops):
                        f.write(f"{self.format_concat_path(normalized_path)}\n")
                        manifest_piece_count += 1
                    if mode == "truncate" and R > 0:
                        f.write(f"{self.format_concat_path(last_block_path)}\n")
                        manifest_piece_count += 1

            self.write_log("⚡ Stitching manifest pieces together losslessly (No Re-encoding)...\n")
            interim_output_path = os.path.join(temp_dir, "interim_video.mp4") if manifest_piece_count > 1 else self.output_path
            cmd_concat = ['ffmpeg', '-y', '-safe', '0', '-f', 'concat', '-i', concat_list_path, '-c', 'copy', interim_output_path]

            if not self.run_command(cmd_concat, "Fast Concat Stitching...", progress_weight=100 - 80, current_base_progress=80, duration_hint=T):
                raise Exception("Lossless Concat stitching failed.")

            # STEP 9 & 10
            if self.video_info['has_audio'] and manifest_piece_count > 1:
                self.write_log("🎧 Rebuilding full-length audio as one continuous track (no repeat-boundary clicks)...\n")
                sr = self.video_info['sample_rate']
                full_audio_path = os.path.join(temp_dir, "full_audio.m4a")
                f_out_dur = min(float(self.fadeout_secs_var.get() or 3), R) if (mode == "truncate" and R > 0) else 0

                if C > 0 and need_loop_pieces:
                    block_b_samples = round(effective_loop_duration * sr)
                    block_b_repeats = full_loops - 1
                    audio_inputs = ['-i', normalized_path]
                    input_idx = 1
                    af = [f"[0:a]atrim=start=0:end={effective_loop_duration},asetpts=PTS-STARTPTS[a_intro]"]
                    if block_b_repeats == 0:
                        af.append("[a_intro]anull[a_base]")
                    else:
                        audio_inputs += ['-i', block_b_audio_path]
                        block_input_idx = input_idx
                        input_idx += 1
                        if block_b_repeats == 1:
                            af.append(f"[{block_input_idx}:a]anull[a_blocks]")
                        else:
                            af.append(f"[{block_input_idx}:a]aloop=loop={block_b_repeats - 1}:size={block_b_samples}:start=0[a_blocks]")
                        af.append("[a_intro][a_blocks]concat=n=2:v=0:a=1[a_base]")
                    if f_out_dur > 0:
                        rem_source = block_b_audio_path if block_b_repeats > 0 else normalized_path
                        audio_inputs += ['-i', rem_source]
                        rem_input_idx = input_idx
                        input_idx += 1
                        remainder_src_end = R if block_b_repeats > 0 else min(R, effective_loop_duration)
                        af.append(f"[{rem_input_idx}:a]atrim=start=0:end={remainder_src_end},asetpts=PTS-STARTPTS,afade=t=out:st={remainder_src_end - f_out_dur}:d={f_out_dur}[a_rem]")
                        af.append("[a_base][a_rem]concat=n=2:v=0:a=1[out_a]")
                    else:
                        af.append("[a_base]anull[out_a]")
                elif C == 0:
                    source_samples = round(source_dur * sr)
                    audio_inputs = ['-i', normalized_path]
                    af = []
                    if full_loops >= 2:
                        af.append(f"[0:a]aloop=loop={full_loops - 1}:size={source_samples}:start=0[a_base]")
                    else:
                        af.append(f"[0:a]anull[a_base]")
                    if f_out_dur > 0:
                        audio_inputs += ['-i', normalized_path]
                        af.append(f"[1:a]atrim=start=0:end={R},asetpts=PTS-STARTPTS,afade=t=out:st={R - f_out_dur}:d={f_out_dur}[a_rem]")
                        af.append("[a_base][a_rem]concat=n=2:v=0:a=1[out_a]")
                    else:
                        af.append("[a_base]anull[out_a]")
                else:
                    af = None

                if af is not None:
                    cmd_full_audio = ['ffmpeg', '-y'] + audio_inputs + ['-filter_complex', "; ".join(af), '-map', '[out_a]'] + codec_a + [full_audio_path]
                    if not self.run_command(cmd_full_audio, "Building full continuous audio track...", progress_weight=0, current_base_progress=99, duration_hint=T):
                        raise Exception("Failed to build the full continuous audio track.")

                    self.write_log("🔗 Muxing continuous audio against the finished video...\n")
                    cmd_final_mux = ['ffmpeg', '-y', '-i', interim_output_path, '-i', full_audio_path,
                                      '-map', '0:v', '-map', '1:a', '-c', 'copy', self.output_path]
                    if not self.run_command(cmd_final_mux, "Finalizing output...", progress_weight=0, current_base_progress=99, duration_hint=T):
                        raise Exception("Failed to mux final audio and video together.")
            elif manifest_piece_count > 1:
                shutil.copy(interim_output_path, self.output_path)

            elapsed_secs = time.time() - pipeline_start_time
            try:
                final_info = self.get_video_info(self.output_path)
                final_duration = final_info['duration']
            except Exception:
                final_duration = T

            duration_str = self.format_duration_human(final_duration)
            elapsed_str = self.format_duration_human(elapsed_secs)

            self.write_log(f"✨ Seamless Loop Generation successfully complete! Output is {duration_str}, rendered in {elapsed_str}.\n")
            self.root.after(0, lambda: self.progress_bar.configure(value=100))
            self.root.after(0, lambda: self.progress_lbl.configure(text="Finished Successfully!"))
            self.root.after(0, lambda: messagebox.showinfo(
                "Process Finished",
                f"Your video of {duration_str} was produced in {elapsed_str}."
            ))

        except Exception as e:
            err_msg = str(e)
            if self.cancel_requested:
                self.write_log("🛑 Pipeline stopped (cancelled by user).\n")
            else:
                self.write_log(f"❌ Error encountered in pipeline: {err_msg}\n")
                self.root.after(0, lambda msg=err_msg: messagebox.showerror("Pipeline Failed", f"A processing error occurred during render:\n{msg}"))
        
        finally:
            self.root.after(0, self.reset_ui_after_processing)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoLoopApp(root)
    root.mainloop()
