"""
GUI Image Compressor
User-friendly interface for batch image compression with real-time preview.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import os
from pathlib import Path
from PIL import Image, ImageTk
import queue
from image_compressor import ImageCompressor, format_size

class ImageCompressorGUI:
    """Advanced GUI for image compression with real-time preview and batch processing."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Compressor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize compressor
        self.compressor = ImageCompressor(auto_repair=True)
        
        # Initialize variables
        self.selected_files = []
        self.output_directory = tk.StringVar()
        self.quality_preset = tk.StringVar(value="balanced")
        self.target_format = tk.StringVar(value="same")
        self.preserve_exif = tk.BooleanVar(value=True)
        self.auto_repair = tk.BooleanVar(value=True)
        self.current_preview_path = None
        
        # Queue for thread communication
        self.progress_queue = queue.Queue()
        
        # Setup GUI
        self.setup_gui()
        self.setup_styles()
        
        # Start monitoring progress queue
        self.root.after(100, self.check_progress_queue)
    
    def setup_styles(self):
        """Configure custom styles for the GUI."""
        style = ttk.Style()
        
        # Configure button styles
        style.configure("Accent.TButton", padding=(10, 5))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
    
    def setup_gui(self):
        """Create and layout GUI components."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced Image Compressor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - File selection and settings
        left_panel = ttk.LabelFrame(main_frame, text="Files & Settings", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.setup_file_selection(left_panel)
        self.setup_compression_settings(left_panel)
        self.setup_output_settings(left_panel)
        
        # Middle panel - Preview
        preview_panel = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 5))
        
        self.setup_preview_panel(preview_panel)
        
        # Right panel - File list
        files_panel = ttk.LabelFrame(main_frame, text="Selected Files", padding="10")
        files_panel.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        self.setup_files_panel(files_panel)
        
        # Bottom panel - Progress and results
        bottom_panel = ttk.Frame(main_frame)
        bottom_panel.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.setup_progress_panel(bottom_panel)
    
    def setup_file_selection(self, parent):
        """Setup file selection controls."""
        # File selection buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Add Images", 
                  command=self.select_images, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Add Folder", 
                  command=self.select_folder).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Clear All", 
                  command=self.clear_files).pack(side=tk.LEFT)
    
    def setup_compression_settings(self, parent):
        """Setup compression settings controls."""
        settings_frame = ttk.LabelFrame(parent, text="Compression Settings", padding="5")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quality preset
        ttk.Label(settings_frame, text="Quality Preset:").grid(row=0, column=0, sticky=tk.W, pady=2)
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_preset,
                                   values=["maximum", "high", "balanced", "small"],
                                   state="readonly", width=15)
        quality_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Target format
        ttk.Label(settings_frame, text="Target Format:").grid(row=1, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(settings_frame, textvariable=self.target_format,
                                  values=["same", "jpeg", "png", "webp"],
                                  state="readonly", width=15)
        format_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Preserve EXIF
        ttk.Checkbutton(settings_frame, text="Preserve EXIF data",
                       variable=self.preserve_exif).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Auto-repair option
        ttk.Checkbutton(settings_frame, text="Auto-repair corrupted images",
                       variable=self.auto_repair).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        settings_frame.columnconfigure(1, weight=1)
    
    def setup_output_settings(self, parent):
        """Setup output directory settings."""
        output_frame = ttk.LabelFrame(parent, text="Output Settings", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Output Directory:").pack(anchor=tk.W)
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_entry = ttk.Entry(dir_frame, textvariable=self.output_directory)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="Browse", 
                  command=self.select_output_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Set default output directory
        self.output_directory.set("compressed_images")
    
    def setup_preview_panel(self, parent):
        """Setup image preview panel."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Preview info
        self.preview_info = ttk.Label(parent, text="Select an image to preview")
        self.preview_info.grid(row=0, column=0, pady=(0, 10))
        
        # Preview canvas with scrollbars
        preview_frame = ttk.Frame(parent)
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_canvas = tk.Canvas(preview_frame, bg="white", width=300, height=300)
        v_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        h_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def setup_files_panel(self, parent):
        """Setup selected files list panel."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Files count
        self.files_count_label = ttk.Label(parent, text="No files selected")
        self.files_count_label.grid(row=0, column=0, pady=(0, 10))
        
        # Files listbox with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.files_listbox = tk.Listbox(list_frame, height=15)
        files_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        self.files_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Remove button
        ttk.Button(parent, text="Remove Selected", 
                  command=self.remove_selected_file).grid(row=2, column=0, pady=(10, 0))
    
    def setup_progress_panel(self, parent):
        """Setup progress and results panel."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.compress_button = ttk.Button(control_frame, text="Start Compression", 
                                        command=self.start_compression, style="Accent.TButton")
        self.compress_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", 
                                    command=self.stop_compression, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        
        # Results text area
        results_frame = ttk.LabelFrame(parent, text="Results", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = ScrolledText(results_frame, height=8, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def select_images(self):
        """Open file dialog to select image files."""
        filetypes = [
            ("All Images", "*.jpg *.jpeg *.png *.webp *.tiff *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("WebP files", "*.webp"),
            ("TIFF files", "*.tiff"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
        
        self.update_files_list()
    
    def select_folder(self):
        """Open dialog to select a folder containing images."""
        folder = filedialog.askdirectory(title="Select Folder Containing Images")
        
        if folder:
            # Find all image files in the folder
            for ext in ['.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp']:
                for file_path in Path(folder).rglob(f"*{ext}"):
                    str_path = str(file_path)
                    if str_path not in self.selected_files:
                        self.selected_files.append(str_path)
                        
                for file_path in Path(folder).rglob(f"*{ext.upper()}"):
                    str_path = str(file_path)
                    if str_path not in self.selected_files:
                        self.selected_files.append(str_path)
        
        self.update_files_list()
    
    def select_output_directory(self):
        """Open dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
    
    def clear_files(self):
        """Clear all selected files."""
        self.selected_files.clear()
        self.update_files_list()
        self.clear_preview()
    
    def remove_selected_file(self):
        """Remove selected file from the list."""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            del self.selected_files[index]
            self.update_files_list()
            if not self.selected_files:
                self.clear_preview()
    
    def update_files_list(self):
        """Update the files listbox."""
        self.files_listbox.delete(0, tk.END)
        
        for file_path in self.selected_files:
            filename = Path(file_path).name
            self.files_listbox.insert(tk.END, filename)
        
        count = len(self.selected_files)
        self.files_count_label.config(text=f"{count} file{'s' if count != 1 else ''} selected")
    
    def on_file_select(self, event):
        """Handle file selection in the listbox."""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            file_path = self.selected_files[index]
            self.show_preview(file_path)
    
    def show_preview(self, image_path):
        """Display image preview with information."""
        try:
            self.current_preview_path = image_path
            
            # Get image info
            info = self.compressor.get_image_info(image_path)
            
            # Update info label
            if info:
                info_text = (f"{info['format']} • {info['width']}×{info['height']} • "
                           f"{format_size(info['file_size'])}")
                self.preview_info.config(text=info_text)
            
            # Load and display image
            with Image.open(image_path) as img:
                # Calculate display size (max 300x300)
                display_size = self.calculate_display_size(img.size, (300, 300))
                
                # Resize image for display
                display_img = img.copy()
                display_img.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.preview_photo = ImageTk.PhotoImage(display_img)
                
                # Clear canvas and display image
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(150, 150, image=self.preview_photo, anchor=tk.CENTER)
                
                # Update scroll region
                self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
                
        except Exception as e:
            self.preview_info.config(text=f"Error loading preview: {str(e)}")
            self.clear_preview()
    
    def calculate_display_size(self, original_size, max_size):
        """Calculate display size maintaining aspect ratio."""
        w, h = original_size
        max_w, max_h = max_size
        
        ratio = min(max_w / w, max_h / h)
        return (int(w * ratio), int(h * ratio))
    
    def clear_preview(self):
        """Clear the image preview."""
        self.preview_canvas.delete("all")
        self.preview_info.config(text="Select an image to preview")
        self.current_preview_path = None
    
    def start_compression(self):
        """Start the compression process in a separate thread."""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select images to compress.")
            return
        
        if not self.output_directory.get():
            messagebox.showwarning("No Output Directory", "Please specify an output directory.")
            return
        
        # Disable controls
        self.compress_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        # Start compression thread
        self.compression_thread = threading.Thread(target=self.compression_worker, daemon=True)
        self.compression_thread.start()
    
    def compression_worker(self):
        """Worker thread for image compression."""
        try:
            # Update compressor auto-repair setting
            self.compressor.auto_repair = self.auto_repair.get()
            
            target_fmt = None if self.target_format.get() == "same" else self.target_format.get()
            
            # Process each file
            total_files = len(self.selected_files)
            successful = 0
            repaired_count = 0
            
            for i, file_path in enumerate(self.selected_files):
                # Update progress
                progress = (i / total_files) * 100
                self.progress_queue.put(("progress", progress))
                self.progress_queue.put(("status", f"Processing: {Path(file_path).name}"))
                
                # Determine output path
                filename = Path(file_path).stem
                ext = target_fmt if target_fmt else Path(file_path).suffix.lstrip('.')
                output_path = os.path.join(self.output_directory.get(), f"{filename}_compressed.{ext}")
                
                # Compress image
                result = self.compressor.compress_image(
                    file_path,
                    output_path,
                    quality_preset=self.quality_preset.get(),
                    target_format=target_fmt,
                    preserve_exif=self.preserve_exif.get()
                )
                
                # Report result
                if result['success']:
                    successful += 1
                    message = (f"✅ {Path(file_path).name}: "
                             f"{result['compression_ratio']:.1f}% reduction "
                             f"({format_size(result['original_size'])} → "
                             f"{format_size(result['compressed_size'])})")
                    
                    # Add auto-repair note if applicable
                    if result.get('was_auto_repaired', False):
                        repaired_count += 1
                        repair_method = result.get('repair_method', 'unknown method')
                        message += f"\n   🔧 Auto-repaired using: {repair_method}"
                else:
                    message = f"❌ {Path(file_path).name}: {result['error']}"
                
                self.progress_queue.put(("result", message))
            
            # Final progress
            self.progress_queue.put(("progress", 100))
            
            completion_msg = f"Compression complete: {successful}/{total_files} files processed"
            if repaired_count > 0:
                completion_msg += f" ({repaired_count} auto-repaired)"
            
            self.progress_queue.put(("complete", completion_msg))
            
        except Exception as e:
            self.progress_queue.put(("error", f"Compression failed: {str(e)}"))
        finally:
            # Clean up any temporary files
            if hasattr(self.compressor, 'cleanup_temp_files'):
                self.compressor.cleanup_temp_files()
    
    def stop_compression(self):
        """Stop the compression process."""
        # Note: This is a simplified stop - in a real implementation,
        # you'd need more sophisticated thread management
        self.compress_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def check_progress_queue(self):
        """Check for progress updates from the compression thread."""
        try:
            while True:
                msg_type, msg_data = self.progress_queue.get_nowait()
                
                if msg_type == "progress":
                    self.progress_var.set(msg_data)
                elif msg_type == "status":
                    # Could add status label if needed
                    pass
                elif msg_type == "result":
                    self.results_text.insert(tk.END, msg_data + "\n")
                    self.results_text.see(tk.END)
                elif msg_type == "complete":
                    self.results_text.insert(tk.END, f"\n{msg_data}\n")
                    self.results_text.see(tk.END)
                    self.compress_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    messagebox.showinfo("Complete", msg_data)
                elif msg_type == "error":
                    self.results_text.insert(tk.END, f"\n❌ {msg_data}\n")
                    self.results_text.see(tk.END)
                    self.compress_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    messagebox.showerror("Error", msg_data)
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_progress_queue)

def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    
    # Set window icon (if you have one)
    # root.iconbitmap("icon.ico")
    
    app = ImageCompressorGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()