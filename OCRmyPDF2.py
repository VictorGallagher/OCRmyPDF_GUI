#OCRmyPDFgui

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
import sys
from threading import Thread
from ocrmypdf import ocr
import codecs
import os
import queue




class OCRThread(Thread):
    def __init__(self, input_path, output_path, output_log, text_queue, options):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.output_log = output_log
        self.text_queue = text_queue
        self.options = options

    def run(self):
        #' '.join(command)command = [self.input_path, self.output_path]
        command = []
        if self.options.get("skip_text"):
            command.append("--skip-text=True")

        if self.options.get("output_type"):
            command.extend(["--output-type", self.options.get("output_type")])
        if self.options.get("remove_background"):
            command.append("--remove-background=True")
        if self.options.get("deskew"):
            command.append("--deskew=True")
        if self.options.get("force_ocr"):
            command.append("--force-ocr=True")
        if self.options.get("clean_final"):
            command.append("--clean-final")
        if self.options.get("side_car"):
            command.append("--sidecar")
        if self.options.get("jbig2_lossy"):
            command.append("--jbig2-lossy")
        if self.options.get("threshold_level"):
            command.extend(["--threshold", self.options.get("threshold_level")])
        if self.options.get("core_count"):
            command.extend(["--jobs", self.options.get("core_count")])
        command.append('language="eng"')

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            with open(self.output_log, "w") as log_file:
                sys.stdout = log_file
                sys.stderr = log_file
                #ocr(self.input_path, self.output_path, skip_text=True, language="eng", output_type="pdf")
                #ocr(self.input_path, self.output_path + ' '.join(command))
                print(' '.join(command))
            messagebox.showinfo("OCR Completed", "OCR process completed successfully!")
        except Exception as e:
            messagebox.showerror("OCR Error", f"An error occurred during OCR:\n{str(e)}")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        self.text_queue.put(None)  # Signal the end of output

    def read_log_file(self):
        try:
            with codecs.open(self.output_log, "r", encoding="utf-8", errors="ignore") as file:
                log_content = file.read()
                self.text_queue.put(log_content)
        except IOError:
            self.text_queue.put("Error: Failed to open output log file.")

    def stop(self):
        if self.process:
            self.process.terminate()


class MainWindow:
    def __init__(self, root):

        self.root = root

        #self.root = ctk.CTk()
        self.root.title("OCRmyPDF GUI")
        self.root.geometry("1000x900")

        self.file_label = ctk.CTkLabel(self.root, text="Select a PDF file to OCR")
        self.file_label.pack(pady=10)

        self.file_name_label = ctk.CTkLabel(self.root, text="File Name")
        self.file_name_label.pack(pady=10)

        self.output_label = ctk.CTkLabel(self.root, text="Output File:")
        self.output_label.pack()

        self.output_path_label = ctk.CTkLabel(self.root, text="File Name")
        self.output_path_label.pack()

        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.StringVar()
        self.log_text.set("")  # Initialize log text variable

        self.log_scrollbar = tk.Scrollbar(self.log_frame)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_label = tk.Text(
            self.log_frame, yscrollcommand=self.log_scrollbar.set, wrap=tk.WORD, state=tk.DISABLED, bg="black",fg="green2")
        #self.log_label.configure(font=("Courier", 12))
        #self.log_label.pack(fill=tk.BOTH, expand=True)
        self.log_label.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.log_scrollbar.configure(command=self.log_label.yview)

        self.text_queue = queue.Queue()
        self.output_log = ""  # Initialize output log attribute

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, pady=15)

        self.file_button = ctk.CTkButton(self.button_frame, text="Browse", command=self.browse_file)
        self.file_button.pack(side=tk.LEFT)

        self.start_button = ctk.CTkButton(self.button_frame, text="Start OCR", command=self.start_ocr, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = ctk.CTkButton(self.button_frame, text="Stop OCR", command=self.stop_ocr, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        self.close_button = ctk.CTkButton(self.button_frame, text="Close", command=self.root.quit)
        self.close_button.pack(side=tk.LEFT)


        self.options_frame1 = tk.Frame(self.root)
        self.options_frame1.pack(pady=15)

        self.skip_text_var = tk.BooleanVar()
        self.skip_text_checkbutton = ctk.CTkCheckBox(self.options_frame1, text="Skip Text", variable=self.skip_text_var)
        self.skip_text_checkbutton.select()
        self.skip_text_checkbutton.pack(side=tk.LEFT)

        self.output_type_var = tk.StringVar()
        self.output_type_var.set("pdf")
        self.output_type_label = ctk.CTkLabel(self.options_frame1, text="Output Type:")
        self.output_type_label.pack(side=tk.LEFT)
        #self.output_type_optionmenu = ctk.CTkOptionMenu(self.options_frame1, self.output_type_var, "pdf", "pdfa")
        self.output_type_optionmenu = ctk.CTkOptionMenu(self.options_frame1, variable=self.output_type_var, values=["pdf", "pdfa"])
        self.output_type_optionmenu.pack(side=tk.LEFT)
        self.output_type_optionmenu.pack(padx=10)

        self.remove_background_var = tk.BooleanVar()
        self.remove_background_checkbutton = ctk.CTkCheckBox(
            self.options_frame1, text="Remove Background", variable=self.remove_background_var)
        self.remove_background_checkbutton.pack(side=tk.LEFT)
        self.remove_background_checkbutton.pack(padx=10)

        self.deskew_var = tk.BooleanVar()
        self.deskew_checkbutton = ctk.CTkCheckBox(self.options_frame1, text="Deskew", variable=self.deskew_var)
        self.deskew_checkbutton.pack(side=tk.LEFT)

        self.force_ocr_var = tk.BooleanVar()
        self.force_ocr_checkbutton = ctk.CTkCheckBox(self.options_frame1, text="Force OCR", variable=self.force_ocr_var)
        self.force_ocr_checkbutton.pack(side=tk.LEFT)


        self.options_frame2 = tk.Frame(self.root)
        self.options_frame2.pack(pady=15)

        self.clean_final_var = tk.BooleanVar()
        self.clean_final_checkbutton = ctk.CTkCheckBox(self.options_frame2, text="Clean Final", variable=self.clean_final_var)
        self.clean_final_checkbutton.pack(side=tk.LEFT)

        self.side_car_var = tk.BooleanVar()
        self.side_car_checkbutton = ctk.CTkCheckBox(self.options_frame2, text="+ Text File", variable=self.side_car_var)
        self.side_car_checkbutton.pack(side=tk.LEFT)

        self.jbig2_lossy_var = tk.BooleanVar()
        self.jbig2_lossy_checkbutton = ctk.CTkCheckBox(self.options_frame2, text="JBig2 lossy", variable=self.jbig2_lossy_var)
        self.jbig2_lossy_checkbutton.pack(side=tk.LEFT)

        self.threshold_level_label = ctk.CTkLabel(self.options_frame2, text="Threshold Level:")
        self.threshold_level_label.pack(side=tk.LEFT)
        self.threshold_level_var  = tk.StringVar()
        self.threshold_values = [str(x) for x in range(0,255,10) ]
        self.threshold_values.append("255")
        self.threshold_values.reverse()
        self.threshold_level_optionmenu = ctk.CTkOptionMenu(self.options_frame2, variable=self.threshold_level_var, values=self.threshold_values)
        self.threshold_level_optionmenu.pack(side=tk.LEFT)
        self.threshold_level_optionmenu.pack(padx=10)
        self.threshold_level_optionmenu.set("255")

        self.cores_count_label = ctk.CTkLabel(self.options_frame2, text="Number of Cores:  ")
        self.cores_count_label.pack(side=tk.LEFT)
        self.cores_count_var = tk.StringVar()
        self.cores_count_values = [str(x) for x in range(1,64)]
        self.cores_count_optionmenu = ctk.CTkOptionMenu(self.options_frame2, variable=self.cores_count_var, values=self.cores_count_values)
        self.cores_count_optionmenu.set("2")
        self.cores_count_optionmenu.pack(side=tk.LEFT)
        self.cores_count_optionmenu.pack(padx=10)

        self.update_text_widget()

    input_path = ''
    output_path = ''


    def browse_file(self):
        input_directory = '/home/victor/Documents/Literature'
        file_path = filedialog.askopenfilename(initialdir=input_directory, filetypes=[("PDF Files", "*.pdf")] )
        if file_path:
            head, tail = os.path.split(file_path)
            self.input_path = file_path
            self.file_name_label.configure(text=tail)
            self.start_button.configure(state=tk.NORMAL)

    def start_ocr(self):
        #input_path = self.file_label.cget("text")
        input_path = self.input_path

        output_directory = os.path.dirname(input_path)
        output_file_name = os.path.splitext(os.path.basename(input_path))[0] + "_ocr.pdf"
        output_path = os.path.join(output_directory, output_file_name)

        self.output_path_label.configure(text=output_file_name)
        self.clear_log_frame()
        self.output_log = os.path.join(output_directory, "ocr_log.txt")

        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)

        options = {
            "skip_text": self.skip_text_var.get(),
            "output_type": self.output_type_var.get(),
            "remove_background": self.remove_background_var.get(),
            "deskew": self.deskew_var.get(),
            "force_ocr": self.force_ocr_var.get(),
            "clean_final":self.clean_final_var.get(),
            "side_car": self.side_car_var.get(),
            "jbig2_lossy": self.jbig2_lossy_var.get(),
            "threshold_level": self.threshold_level_var.get(),
            "core_count": self.cores_count_var.get(),
        }
        cr_thread = OCRThread(input_path, output_path, self.output_log, self.text_queue, options)
        cr_thread.start()


    def stop_ocr(self):
        if self.ocr_thread:
            self.ocr_thread.stop()
            self.ocr_thread.join()
            self.ocr_thread = None
            messagebox.showinfo("Info", "OCR process stopped.")

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


    def update_text_widget(self):
        self.read_log_file()  # Read the updated content of the log file
        self.clear_log_frame()
        while True:
            try:
                content = self.text_queue.get_nowait()
                if content is None:
                    break
                self.log_text.set(content)
                self.log_label.config(state=tk.NORMAL)
                self.log_label.delete("1.0", tk.END)
                self.log_label.insert(tk.END, content)
                self.log_label.config(state=tk.DISABLED)
                self.root.update_idletasks()
            except queue.Empty:
                break

        self.root.after(500, self.update_text_widget)

    def clear_log_frame(self):
        self.log_label.config(state=tk.NORMAL)
        self.log_label.delete("1.0", tk.END)
        self.log_label.config(state=tk.DISABLED)


    def read_log_file(self):
        try:
            with codecs.open(self.output_log, "r", encoding="utf-8", errors="ignore") as file:
                log_content = file.read()
                log_lines = log_content.splitlines()
                reversed_content = "\n".join(log_lines[::-1])
                self.text_queue.put(reversed_content)
        except IOError:
            self.text_queue.put("Error: Failed to open output log file.")



if __name__ == "__main__":
    #root = tk.Tk()
    root = ctk.CTk()
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme('dark-blue')
    app = MainWindow(root)
    root.mainloop()
