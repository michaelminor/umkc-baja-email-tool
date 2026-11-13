"""
GUI Application for Email Automation Tool.
Provides a user-friendly interface for UMKC Baja Racing email outreach.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import json
from pathlib import Path

from .config import Config, ConfigurationError
from .logger import setup_logger
from .gui_processor import GUIEmailProcessor
from .csv_handler import CSVHandler
from .outlook_handler import OutlookNotAvailableError


# Colors
COLORS = {
    'primary': '#003366',      # Navy blue
    'secondary': '#FFD700',    # Gold
    'success': '#28a745',      # Green
    'error': '#dc3545',        # Red
    'warning': '#ffc107',      # Yellow
    'bg': '#f8f9fa',          # Light gray background
    'fg': '#212529'           # Dark text
}

# Fonts
FONTS = {
    'heading': ('Segoe UI', 12, 'bold'),
    'normal': ('Segoe UI', 10),
    'small': ('Segoe UI', 8)
}


class EmailAutomationGUI:
    """Main GUI application for email automation."""

    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.config = None
        self.logger = None
        self.progress_queue = queue.Queue()
        self.is_running = False

        # StringVars for configuration
        self.email_subject = tk.StringVar()
        self.template_path = tk.StringVar()
        self.attachment_path = tk.StringVar()
        self.csv_folder = tk.StringVar()

        # Setup window
        self._setup_window()

        # Load configuration
        self._load_config()

        # Create GUI
        self._create_gui()

    def _setup_window(self):
        """Configure main window properties."""
        self.root.title("UMKC Baja Racing - Email Automation Tool")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Set background color
        self.root.configure(bg=COLORS['bg'])

    def _load_config(self):
        """Load configuration from settings.json."""
        try:
            self.config = Config()
            self.logger = setup_logger()
            self.logger.info("GUI launched")

            # Load config values into StringVars
            self.email_subject.set(self.config.email_subject)
            self.template_path.set(self.config.email_template_path)
            self.attachment_path.set(self.config.attachment_path)
            self.csv_folder.set(self.config.csv_folder)

        except ConfigurationError as e:
            messagebox.showerror(
                "Configuration Error",
                f"Failed to load configuration:\n\n{e}\n\nUsing default values."
            )
            # Set defaults
            self.email_subject.set("University of Missouri - Kansas City Baja Racing team sponsorship outreach")
            self.template_path.set("templates/email_template.txt")
            self.attachment_path.set("templates/sponsorship_packet.docx")
            self.csv_folder.set("C:\\Users\\mfmin\\EmailOutreach")

    def _create_gui(self):
        """Create the main GUI components."""
        # Header
        header = tk.Frame(self.root, bg=COLORS['primary'], height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="🏁 UMKC Baja Racing Email Tool",
            font=('Segoe UI', 16, 'bold'),
            bg=COLORS['primary'],
            fg='white'
        )
        title.pack(pady=15)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self._create_setup_tab()
        self._create_send_tab()
        self._create_history_tab()
        self._create_logs_tab()

    def _create_setup_tab(self):
        """Create configuration setup tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Setup")

        # Main frame with padding
        main_frame = ttk.Frame(tab, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="Configuration",
            font=FONTS['heading']
        ).grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky='w')

        # Email Subject
        ttk.Label(main_frame, text="Email Subject:", font=FONTS['normal']).grid(
            row=1, column=0, sticky='w', pady=5
        )
        ttk.Entry(main_frame, textvariable=self.email_subject, width=60).grid(
            row=1, column=1, columnspan=2, sticky='ew', pady=5
        )

        # Email Template
        ttk.Label(main_frame, text="Email Template:", font=FONTS['normal']).grid(
            row=2, column=0, sticky='w', pady=5
        )
        ttk.Entry(main_frame, textvariable=self.template_path, width=50).grid(
            row=2, column=1, sticky='ew', pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._browse_template).grid(
            row=2, column=2, padx=(5, 0), pady=5
        )

        # Attachment
        ttk.Label(main_frame, text="Sponsorship Packet:", font=FONTS['normal']).grid(
            row=3, column=0, sticky='w', pady=5
        )
        ttk.Entry(main_frame, textvariable=self.attachment_path, width=50).grid(
            row=3, column=1, sticky='ew', pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._browse_attachment).grid(
            row=3, column=2, padx=(5, 0), pady=5
        )

        # CSV Folder
        ttk.Label(main_frame, text="CSV Folder:", font=FONTS['normal']).grid(
            row=4, column=0, sticky='w', pady=5
        )
        ttk.Entry(main_frame, textvariable=self.csv_folder, width=50).grid(
            row=4, column=1, sticky='ew', pady=5
        )
        ttk.Button(main_frame, text="Browse...", command=self._browse_csv_folder).grid(
            row=4, column=2, padx=(5, 0), pady=5
        )

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(
            button_frame,
            text="Preview Template",
            command=self._preview_template
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Save Configuration",
            command=self._save_config
        ).pack(side='left', padx=5)

    def _create_send_tab(self):
        """Create email sending tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📧 Send Emails")

        # Main frame with padding
        main_frame = ttk.Frame(tab, padding="20")
        main_frame.pack(fill='both', expand=True)

        # CSV Files section
        csv_frame = ttk.LabelFrame(main_frame, text="CSV Files", padding="10")
        csv_frame.pack(fill='both', expand=True, pady=(0, 10))

        self.csv_text = scrolledtext.ScrolledText(csv_frame, height=8, font=FONTS['normal'])
        self.csv_text.pack(fill='both', expand=True)

        ttk.Button(csv_frame, text="Refresh File List", command=self._refresh_csv_list).pack(pady=(5, 0))

        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill='x', pady=(0, 10))

        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', pady=(0, 5))

        self.status_label = ttk.Label(progress_frame, text="Ready", font=FONTS['normal'])
        self.status_label.pack()

        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.pack(fill='x', pady=(0, 10))

        self.stats_text = tk.Text(stats_frame, height=5, font=FONTS['normal'], state='disabled')
        self.stats_text.pack(fill='x')

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')

        self.dry_run_btn = ttk.Button(
            button_frame,
            text="🧪 Test Run (Dry Run)",
            command=self._run_dry_run
        )
        self.dry_run_btn.pack(side='left', padx=5)

        self.send_btn = ttk.Button(
            button_frame,
            text="✉️ Send Emails",
            command=self._run_send
        )
        self.send_btn.pack(side='left', padx=5)

        # Auto-refresh CSV list
        self._refresh_csv_list()

    def _create_history_tab(self):
        """Create email history viewer tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📜 History")

        # Main frame with padding
        main_frame = ttk.Frame(tab, padding="20")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text="Email Send History",
            font=FONTS['heading']
        ).pack(pady=(0, 10))

        # Text widget for history
        self.history_text = scrolledtext.ScrolledText(main_frame, font=FONTS['normal'])
        self.history_text.pack(fill='both', expand=True)

        # Refresh button
        ttk.Button(main_frame, text="Refresh History", command=self._load_history).pack(pady=(10, 0))

        # Load history
        self._load_history()

    def _create_logs_tab(self):
        """Create log viewer tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Logs")

        # Main frame with padding
        main_frame = ttk.Frame(tab, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Log selector
        selector_frame = ttk.Frame(main_frame)
        selector_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(selector_frame, text="Select Log File:", font=FONTS['normal']).pack(side='left', padx=(0, 10))

        self.log_file_var = tk.StringVar()
        self.log_dropdown = ttk.Combobox(selector_frame, textvariable=self.log_file_var, state='readonly')
        self.log_dropdown.pack(side='left', fill='x', expand=True)
        self.log_dropdown.bind('<<ComboboxSelected>>', lambda e: self._load_log())

        ttk.Button(selector_frame, text="Refresh", command=self._refresh_logs).pack(side='left', padx=(10, 0))

        # Log viewer
        self.log_text = scrolledtext.ScrolledText(main_frame, font=('Courier New', 9))
        self.log_text.pack(fill='both', expand=True)

        # Refresh logs
        self._refresh_logs()

    # Browse methods
    def _browse_template(self):
        """Browse for email template file."""
        filename = filedialog.askopenfilename(
            title="Select Email Template",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            self.template_path.set(filename)

    def _browse_attachment(self):
        """Browse for attachment file."""
        filename = filedialog.askopenfilename(
            title="Select Sponsorship Packet",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            self.attachment_path.set(filename)

    def _browse_csv_folder(self):
        """Browse for CSV folder."""
        folder = filedialog.askdirectory(title="Select CSV Folder")
        if folder:
            self.csv_folder.set(folder)

    def _preview_template(self):
        """Preview email template."""
        template_path = self.template_path.get()
        if not os.path.exists(template_path):
            messagebox.showerror("Error", f"Template file not found:\n{template_path}")
            return

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create preview window
            preview = tk.Toplevel(self.root)
            preview.title("Email Template Preview")
            preview.geometry("600x400")

            text_widget = scrolledtext.ScrolledText(preview, wrap='word', font=FONTS['normal'])
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', content)
            text_widget.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read template:\n{e}")

    def _save_config(self):
        """Save configuration to settings.json."""
        # Validate paths
        errors = []

        if not os.path.exists(self.template_path.get()):
            errors.append(f"Email template not found: {self.template_path.get()}")

        if not os.path.exists(self.attachment_path.get()):
            errors.append(f"Attachment not found: {self.attachment_path.get()}")

        if not os.path.exists(self.csv_folder.get()):
            errors.append(f"CSV folder not found: {self.csv_folder.get()}")

        if errors:
            messagebox.showerror("Validation Error", "\n\n".join(errors))
            return

        # Convert paths to relative (for portability)
        from pathlib import Path

        install_dir = self.config.install_dir

        def make_relative(path_str):
            """Convert absolute path to relative from install_dir."""
            try:
                path_obj = Path(path_str)
                if path_obj.is_absolute():
                    rel_path = path_obj.relative_to(install_dir)
                    return str(rel_path).replace('\\', '/')  # Use forward slashes
                return path_str.replace('\\', '/')
            except ValueError:
                # Path is not relative to install_dir, keep absolute
                return path_str

        # Save configuration with relative paths
        config_data = {
            "email_template_path": make_relative(self.template_path.get()),
            "email_subject": self.email_subject.get(),
            "attachment_path": make_relative(self.attachment_path.get()),
            "csv_folder": make_relative(self.csv_folder.get()),
            "log_directory": "logs",
            "history_file": "data/sent_emails_history.txt"
        }

        try:
            config_file = install_dir / "config" / "settings.json"
            with open(config_file, "w", encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)

            messagebox.showinfo("Success", "Configuration saved successfully!")

            # Reload config
            self.config = Config()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

    def _refresh_csv_list(self):
        """Refresh the list of CSV files."""
        csv_folder = self.csv_folder.get()
        self.csv_text.delete('1.0', 'end')

        if not os.path.exists(csv_folder):
            self.csv_text.insert('1.0', f"Folder not found: {csv_folder}")
            return

        csv_files = [
            f for f in os.listdir(csv_folder)
            if f.lower().endswith('.csv') and not f.startswith('~$')
        ]

        if not csv_files:
            self.csv_text.insert('1.0', f"No CSV files found in:\n{csv_folder}")
            return

        self.csv_text.insert('1.0', f"Found {len(csv_files)} CSV file(s):\n\n")

        for csv_file in csv_files:
            file_path = os.path.join(csv_folder, csv_file)
            try:
                handler = CSVHandler(file_path)
                handler.load()
                count = handler.get_row_count()
                self.csv_text.insert('end', f"✓ {csv_file} ({count} recipients)\n")
            except Exception as e:
                self.csv_text.insert('end', f"✗ {csv_file} (error: {e})\n")

    def _load_history(self):
        """Load and display email history."""
        history_file = "data/sent_emails_history.txt"
        self.history_text.delete('1.0', 'end')

        if not os.path.exists(history_file):
            self.history_text.insert('1.0', "No history file found yet.\nEmails sent will appear here.")
            return

        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count non-comment lines
            emails = [line for line in content.split('\n') if line.strip() and not line.startswith('#')]

            self.history_text.insert('1.0', f"Total emails sent: {len(emails)}\n\n")
            self.history_text.insert('end', content)

        except Exception as e:
            self.history_text.insert('1.0', f"Error reading history: {e}")

    def _refresh_logs(self):
        """Refresh the list of log files."""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return

        log_files = sorted(
            [f for f in os.listdir(log_dir) if f.endswith('.log')],
            reverse=True
        )

        self.log_dropdown['values'] = log_files

        if log_files:
            self.log_dropdown.current(0)
            self._load_log()

    def _load_log(self):
        """Load and display selected log file."""
        log_file = self.log_file_var.get()
        if not log_file:
            return

        log_path = os.path.join("logs", log_file)
        self.log_text.delete('1.0', 'end')

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.log_text.insert('1.0', content)
        except Exception as e:
            self.log_text.insert('1.0', f"Error reading log: {e}")

    def _run_dry_run(self):
        """Run dry run (test mode)."""
        self._run_processor(dry_run=True)

    def _run_send(self):
        """Run actual email send."""
        # Confirmation dialog
        result = messagebox.askyesno(
            "Confirm Send",
            "This will send emails to all recipients in the CSV files.\n\n"
            "Are you sure you want to proceed?",
            icon='warning'
        )

        if result:
            self._run_processor(dry_run=False)

    def _run_processor(self, dry_run=False):
        """Run email processor in background thread."""
        if self.is_running:
            messagebox.showwarning("Already Running", "Email processing is already in progress.")
            return

        # Disable buttons
        self.is_running = True
        self.send_btn.config(state='disabled')
        self.dry_run_btn.config(state='disabled')

        # Reset progress
        self.progress_var.set(0)
        self.status_label.config(text="Initializing...")

        # Start worker thread
        thread = threading.Thread(
            target=self._worker_thread,
            args=(dry_run,),
            daemon=True
        )
        thread.start()

        # Start checking queue
        self.root.after(100, self._check_queue)

    def _worker_thread(self, dry_run):
        """Worker thread for email processing."""
        # Initialize COM for this thread (required for Outlook)
        import pythoncom
        pythoncom.CoInitialize()

        try:
            # Reload config
            config = Config()

            # Create processor with progress callbacks
            processor = GUIEmailProcessor(
                config=config,
                logger=self.logger,
                dry_run=dry_run,
                progress_callback=lambda current, total, percentage: self.progress_queue.put({
                    'type': 'progress',
                    'current': current,
                    'total': total,
                    'percentage': percentage
                }),
                status_callback=lambda message, stats: self.progress_queue.put({
                    'type': 'status',
                    'message': message,
                    'stats': stats
                })
            )

            # Initialize and process
            processor.initialize()
            stats = processor.process_all_files()

            # Send completion message
            self.progress_queue.put({
                'type': 'done',
                'stats': stats
            })

        except OutlookNotAvailableError as e:
            self.progress_queue.put({
                'type': 'error',
                'message': f"Outlook Error:\n\n{e}\n\nPlease ensure Outlook is installed and configured."
            })

        except Exception as e:
            self.progress_queue.put({
                'type': 'error',
                'message': f"Error:\n\n{e}"
            })

        finally:
            # Cleanup COM
            pythoncom.CoUninitialize()

    def _check_queue(self):
        """Check queue for updates from worker thread."""
        try:
            while True:
                update = self.progress_queue.get_nowait()

                if update['type'] == 'progress':
                    self.progress_var.set(update['percentage'])

                elif update['type'] == 'status':
                    self.status_label.config(text=update['message'])
                    self._update_stats(update['stats'])

                elif update['type'] == 'done':
                    self._on_completion(update['stats'])
                    return

                elif update['type'] == 'error':
                    self._on_error(update['message'])
                    return

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self._check_queue)

    def _update_stats(self, stats):
        """Update statistics display."""
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')
        self.stats_text.insert('1.0',
            f"Sent: {stats['sent']}\n"
            f"Failed: {stats['failed']}\n"
            f"Skipped: {stats['skipped']}\n"
            f"Duplicates: {stats['duplicates']}"
        )
        self.stats_text.config(state='disabled')

    def _on_completion(self, stats):
        """Handle completion of email processing."""
        self.is_running = False
        self.send_btn.config(state='normal')
        self.dry_run_btn.config(state='normal')
        self.status_label.config(text="Complete!")

        messagebox.showinfo(
            "Processing Complete",
            f"Email processing completed!\n\n"
            f"Sent: {stats['sent']}\n"
            f"Failed: {stats['failed']}\n"
            f"Skipped: {stats['skipped']}\n"
            f"Duplicates: {stats['duplicates']}"
        )

        # Refresh displays
        self._refresh_csv_list()
        self._load_history()

    def _on_error(self, message):
        """Handle errors from worker thread."""
        self.is_running = False
        self.send_btn.config(state='normal')
        self.dry_run_btn.config(state='normal')
        self.status_label.config(text="Error occurred")

        messagebox.showerror("Error", message)

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Entry point for GUI application."""
    app = EmailAutomationGUI()
    app.run()


if __name__ == "__main__":
    main()
