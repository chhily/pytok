import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from license_validator import LicenseValidator

# --- Configuration ---https://qngsvqkvvhvfiyhqnklu.supabase.co/functions/v1/validate_license
SUPABASE_URL = "https://qngsvqkvvhvfiyhqnklu.supabase.co"
# It's better practice to load this from an environment variable or a config file
SUPABASE_ANON_KEY = "sb_publishable_m5aCChrLbhGXe-SviUkjXA_wlnRNNUH"

# --- Style Configuration ---
STYLE = {
    "font_normal": ("Segoe UI", 10),
    "font_bold": ("Segoe UI", 11, "bold"),
    "colors": {
        "primary": "#22A7F0",         # VS Code blue
        "success": "#43EA7B",         # Vibrant green
        "warning": "#FFB300",         # Amber
        "error": "#FF4C4C",           # Red
        "disabled": "#757575",        # Muted gray
        "text_light": "#D4D4D4",      # VS Code light text
        "text_dark": "#1E1E1E",       # VS Code dark text
        "bg": "#1E1E1E",              # VS Code dark background
        "frame_bg": "#252526",        # VS Code panel background
        "status_default": "#8A8A8A"   # Neutral gray
    },
    "padding": {"padx": 12, "pady": 7}
}

class TikTokDownloader:
    def __init__(self, root):
        self.root = root
        self.license_validator = LicenseValidator(SUPABASE_URL, SUPABASE_ANON_KEY)
        self.yt_dlp_process = None
        self.is_license_valid = False
        
        self.setup_gui()

    def setup_gui(self):
        """Initialize and lay out the GUI components."""
        self.root.title("TikTok Video Downloader")
        self.root.geometry("520x420")
        self.root.resizable(False, False)
        self.root.configure(bg=STYLE["colors"]["bg"])

        # --- License Section ---
        license_frame = self._create_labelframe("License Validation", STYLE["colors"]["frame_bg"])
        
        tk.Label(license_frame, text="Enter License Key:", font=STYLE["font_normal"], bg=STYLE["colors"]["frame_bg"], fg=STYLE["colors"]["text_light"]).pack(pady=(10, 5))
        self.license_key_entry = tk.Entry(license_frame, font=("Segoe UI", 11), width=45, show="*", bg=STYLE["colors"]["bg"], fg=STYLE["colors"]["text_light"], insertbackground=STYLE["colors"]["text_light"])
        self.license_key_entry.pack(pady=STYLE["padding"]["pady"])
        self.license_key_entry.bind('<Return>', lambda e: self.check_license_key())

        self.license_check_btn = self._create_button(license_frame, "🔍 Validate License", self.check_license_key, "success")
        self.license_check_btn.pack(pady=10)
        
        self.license_status_var = tk.StringVar(value="❓ License not validated")
        self.license_status_label = tk.Label(license_frame, textvariable=self.license_status_var, font=STYLE["font_normal"], fg=STYLE["colors"]["warning"], bg=STYLE["colors"]["frame_bg"])
        self.license_status_label.pack(pady=(0, 10))

        # --- Download Section ---
        download_frame = self._create_labelframe("Download Settings", STYLE["colors"]["frame_bg"])
        
        tk.Label(download_frame, text="Enter TikTok Username:", font=STYLE["font_normal"], bg=STYLE["colors"]["frame_bg"], fg=STYLE["colors"]["text_light"]).pack(pady=(10, 5))
        self.username_entry = tk.Entry(download_frame, font=("Segoe UI", 11), width=45, state="disabled", bg=STYLE["colors"]["bg"], fg=STYLE["colors"]["text_light"], insertbackground=STYLE["colors"]["text_light"])
        self.username_entry.pack(pady=STYLE["padding"]["pady"])
        self.username_entry.bind('<Return>', lambda e: self.start_download())

        btn_frame = tk.Frame(download_frame, bg=STYLE["colors"]["frame_bg"])
        btn_frame.pack(pady=15)
        
        self.download_btn = self._create_button(btn_frame, "📥 Download All Videos", self.start_download, "primary", state="disabled")
        self.download_btn.grid(row=0, column=0, padx=10)
        
        self.cancel_btn = self._create_button(btn_frame, "⛔ Cancel", self.cancel_download, "error", state="disabled")
        self.cancel_btn.grid(row=0, column=1, padx=10)

        # --- Progress Section ---
        progress_frame = self._create_labelframe("Download Progress", STYLE["colors"]["frame_bg"])
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", foreground=STYLE["colors"]["primary"], background=STYLE["colors"]["primary"], troughcolor=STYLE["colors"]["bg"], bordercolor=STYLE["colors"]["frame_bg"])
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=480, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(pady=10, padx=STYLE["padding"]["padx"])
        
        self.status_var = tk.StringVar(value="Ready to validate license")
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var, wraplength=480, justify="left", font=STYLE["font_normal"], fg=STYLE["colors"]["status_default"], bg=STYLE["colors"]["frame_bg"])
        self.status_label.pack(pady=(0, 10))

    def _create_labelframe(self, text, bg_color):
        """Helper to create a styled LabelFrame."""
        frame = tk.LabelFrame(self.root, text=text, font=STYLE["font_bold"], bg=bg_color, fg=STYLE["colors"]["text_light"], relief="groove")
        frame.pack(fill="x", padx=STYLE["padding"]["padx"], pady=STYLE["padding"]["pady"])
        return frame

    def _create_button(self, parent, text, command, color_key, state="normal"):
        """Helper to create a styled Button."""
        button = tk.Button(
            parent, 
            text=text, 
            font=STYLE["font_normal"], 
            command=command, 
            bg=STYLE["colors"][color_key],
            fg=STYLE["colors"]["text_light"],
            activebackground=STYLE["colors"]["primary"],
            activeforeground=STYLE["colors"]["bg"],
            relief="flat",
            padx=15,
            pady=5,
            state=state,
            borderwidth=0,
            highlightthickness=0
        )
        return button

    def _update_status(self, message, color_key):
        """Helper to update the main status label."""
        self.status_var.set(message)
        self.status_label.config(fg=STYLE["colors"][color_key])

    def _set_ui_state(self, is_active):
        """Enable or disable UI elements based on license validity."""
        download_state = "normal" if is_active else "disabled"
        license_state = "disabled" if is_active else "normal"

        self.username_entry.config(state=download_state)
        self.download_btn.config(state=download_state)
        self.license_key_entry.config(state=license_state)
        self.license_check_btn.config(state=license_state)

    def check_license_key(self):
        """Validate the entered license key in a separate thread."""
        license_key = self.license_key_entry.get().strip()
        if not license_key:
            messagebox.showerror("Error", "Please enter a license key.")
            return
            
        self.license_status_var.set("🔄 Validating...")
        self.license_status_label.config(fg=STYLE["colors"]["primary"])
        self.license_check_btn.config(state="disabled")
        self._update_status("🔐 Validating license key...", "primary")
        
        threading.Thread(target=self._validate_in_thread, args=(license_key,), daemon=True).start()

    def _validate_in_thread(self, license_key):
        """Worker function for license validation."""
        try:
            is_valid, reason = self.license_validator.validate_license_key(license_key)
            self.root.after(0, self.on_validation_complete, is_valid, reason)
        except Exception as e:
            self.root.after(0, self.on_validation_complete, False, str(e))
    
    def on_validation_complete(self, is_valid, reason):
        """Handle GUI updates after validation completes."""
        self.is_license_valid = is_valid
        self.license_check_btn.config(state="normal")

        if is_valid:
            self.license_status_var.set("✅ License Valid")
            self.license_status_label.config(fg=STYLE["colors"]["success"])
            self._update_status("Ready to download.", "success")
            self._set_ui_state(True)
        else:
            self.license_status_var.set("❌ License Invalid")
            self.license_status_label.config(fg=STYLE["colors"]["error"])
            self._update_status(f"Validation failed: {reason or 'Unknown error'}", "error")
            self._set_ui_state(False)
            messagebox.showerror("License Validation Failed", f"Validation failed: {reason or 'Unknown error'}")

    def start_download(self):
        """Start the video download process in a separate thread."""
        if not self.is_license_valid:
            messagebox.showerror("Access Denied", "A valid license is required to start downloads.")
            return
            
        username = self.username_entry.get().strip().lstrip("@")
        if not username:
            messagebox.showerror("Error", "Please enter a TikTok username.")
            return
        
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_bar["value"] = 0
        self._update_status(f"📥 Starting download for @{username}...", "primary")
        
        threading.Thread(target=self._run_download_in_thread, args=(username,), daemon=True).start()

    def _run_download_in_thread(self, username):
        """Worker function for running the yt-dlp process."""
        profile_url = f"https://www.tiktok.com/@{username}"
        output_folder = os.path.join("downloads", username)
        os.makedirs(output_folder, exist_ok=True)

        try:
            command = [
                "yt-dlp", profile_url,
                "-o", os.path.join(output_folder, "%(title)s.%(ext)s"),
                "--yes-playlist", "--continue", "--no-overwrites",
                # "--write-description", "--write-info-json"  # Commented: Only download video files
            ]
            self.yt_dlp_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            video_count = 0
            for line in self.yt_dlp_process.stdout:
                if "Downloading video" in line:
                    video_count += 1
                    # Try to extract video title from the line if present
                    title = ""
                    if ":" in line:
                        title = line.split("Downloading video")[-1].strip(": \n")
                    status_msg = f"📥 Downloading video #{video_count}"
                    if title:
                        status_msg += f": {title}"
                    self.root.after(0, self._update_status, status_msg, "primary")
                elif "%" in line and "ETA" in line:
                    try:
                        percent = float(line.split("%")[0].split()[-1].strip())
                        self.root.after(0, lambda p=percent: self.progress_bar.config(value=p))
                    except (ValueError, IndexError):
                        pass
            
            return_code = self.yt_dlp_process.wait()
            self.root.after(0, self.on_download_complete, return_code, username, video_count)

        except FileNotFoundError:
             self.root.after(0, lambda: messagebox.showerror("yt-dlp Not Found", "yt-dlp is not installed or not in your system's PATH."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Download Error", f"An unexpected error occurred: {e}"))
        finally:
            self.yt_dlp_process = None
            self.root.after(0, lambda: (self.download_btn.config(state="normal"), self.cancel_btn.config(state="disabled")))

    def on_download_complete(self, return_code, username, video_count):
        """Handle GUI updates after download process finishes."""
        if return_code == 0:
            self._update_status(f"✅ Download completed for @{username}!", "success")
            self.progress_bar["value"] = 100
            messagebox.showinfo("Download Complete", f"Successfully downloaded {video_count} videos from @{username}")
        elif self.yt_dlp_process and self.yt_dlp_process.poll() is not None and return_code != 0:
             self._update_status(f"❌ Download failed (Exit code: {return_code})", "error")
             messagebox.showerror("Download Failed", f"Download failed. Check the username and your network connection.")
        else: # Cancelled
            self._update_status("⛔ Download canceled by user.", "warning")
            self.progress_bar["value"] = 0

    def cancel_download(self):
        """Terminate the ongoing yt-dlp process."""
        if self.yt_dlp_process and self.yt_dlp_process.poll() is None:
            self.yt_dlp_process.terminate()
            self._update_status("⏹ Canceling download...", "warning")

def main():
    """Main application entry point."""
    root = tk.Tk()
    app = TikTokDownloader(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")

    # Remove window border for a modern look (optional)
    root.configure(bg=STYLE["colors"]["bg"])
    root.tk_setPalette(background=STYLE["colors"]["bg"], foreground=STYLE["colors"]["text_light"])

    root.mainloop()

if __name__ == "__main__":
    main()
