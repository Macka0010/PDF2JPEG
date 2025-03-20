import os
import re
import sys
import argparse
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import fitz
from PIL import Image, ImageTk, ImageOps
Image.MAX_IMAGE_PIXELS = None  
import cv2
import numpy as np
import subprocess

# Global variables
file_paths = []          # Store selected file paths
sliced_pdf_var = None    # (Unused placeholder from your original code)
# edge_detection_var removed as edge detection is applied by default
root = None              # Main Tkinter window (used in GUI mode)
canvas = None            # Canvas widget to display images (GUI only)
canvas_image = None      # Currently displayed image on the canvas (GUI only)
progress = None          # Progress bar widget (GUI only)
image_counter = None     # Label to display number of images extracted (GUI only)
pdf_counter = None       # Label to display number of PDFs left to process (GUI only)
extracted_images_dir = ""  # Folder path of the last extracted images

# Progress counters (GUI only)
extracted_image_count = 0
total_pdf_count = 0
processed_pdf_count = 0

def clean_filename(filename):
    # Remove any characters that are not alphanumeric, space, underscore, or hyphen.
    return re.sub(r"[^\w\s\-]", "", filename)

def is_valid_aspect_ratio(width, height):
    aspect_ratio = width / height
    VALID_ASPECT_RATIOS = [
        1/1, 3/2, 4/3, 5/4, 16/9, 21/9, 2.39/1, 2.35/1, 2.76/1, 9/16, 18/9, 19.5/9,
        20/9, 32/9, 3/1, 4/5, 7/6, 8/5, 11/8, 14/9, 17/9, 18.5/9, 19.3/9, 2/1, 2.4/1,
        2.55/1, 2.59/1, 5/3, 5/2, 6/5, 8.5/11, 2.20/1, 2.66/1, 3.56/1, 2.13/1, 2.28/1,
        2.1/1, 2.31/1, 2.32/1, 2.37/1, 2.42/1, 2.5/1, 2.63/1, 2.7/1, 2.82/1, 2.93/1,
        3.44/1, 3.6/1, 3.7/1, 4.9/1, 5.6/1, 7/1, 10/1
    ]
    return any(abs(aspect_ratio - valid_ratio) < 0.10 for valid_ratio in VALID_ASPECT_RATIOS)

def extract_images_from_page(image_path, output_dir, page_num, pdf_basename):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to detect contours (edge detection applied by default)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_height, img_width = gray.shape
    min_area = (img_width * img_height) * 0.03  # 3% of the image area
    max_area = (img_width * img_height) * 1.05

    extracted_images = []
    image_count = 1  # Counter for images on the same page

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if min_area < w * h < max_area and is_valid_aspect_ratio(w, h):
            save_path = os.path.join(output_dir, f"{pdf_basename}_page_{page_num + 1}_image_{image_count}.jpg")
            cropped_img = image[y:y+h, x:x+w]
            resized_img = cv2.resize(cropped_img, None, fx=1/3, fy=1/3, interpolation=cv2.INTER_AREA)
            cv2.imwrite(save_path, resized_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
            extracted_images.append(save_path)
            image_count += 1
    return extracted_images

def extract_images_with_processing(file_path, output_dir):
    global extracted_images_dir, extracted_image_count, root, image_counter
    extracted_images_dir = output_dir
    pdf_file = fitz.open(file_path)
    image_paths = []
    pdf_basename = os.path.splitext(os.path.basename(file_path))[0]
    # Clean the pdf basename to remove special characters
    pdf_basename = clean_filename(pdf_basename)
    
    for page_num in range(len(pdf_file)):
        page = pdf_file[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        temp_image_path = os.path.join(output_dir, f"{pdf_basename}_pdf_page_{page_num + 1}.png")
        pix.save(temp_image_path)
        images_extracted = extract_images_from_page(temp_image_path, output_dir, page_num, pdf_basename)
        for img_path in images_extracted:
            image_paths.append(img_path)
            # Only update the GUI if running in GUI mode
            if root is not None:
                update_canvas(img_path)
                extracted_image_count += 1
                image_counter.config(text=f"Images Extracted: {extracted_image_count}")
                root.update()
        os.remove(temp_image_path)
    return image_paths

def update_canvas(image_path):
    global canvas_image, canvas
    if canvas is None:
        return
    try:
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        img = ImageTk.PhotoImage(img)
        canvas.delete("all")
        canvas.create_image(150, 150, image=img)
        canvas.image = img
    except Exception as e:
        print(f"Error updating canvas with {image_path}: {e}")

# GUI functions remain the same
def extract_and_process_images_files():
    global file_paths, total_pdf_count, processed_pdf_count, progress, pdf_counter
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if file_paths:
        total_pdf_count = len(file_paths)
        processed_pdf_count = 0
        progress['maximum'] = total_pdf_count
        pdf_counter.config(text=f"PDFs left: {total_pdf_count - processed_pdf_count}")
        for file_path in file_paths:
            file_dir = os.path.dirname(file_path)
            output_dir = os.path.join(file_dir, "Extracted Images")
            os.makedirs(output_dir, exist_ok=True)
            extract_images_with_processing(file_path, output_dir)
            processed_pdf_count += 1
            pdf_counter.config(text=f"PDFs left: {total_pdf_count - processed_pdf_count}")
            progress['value'] = processed_pdf_count
            root.update()  # Update GUI after processing each PDF

def extract_and_process_images_directory():
    global file_paths, total_pdf_count, processed_pdf_count, progress, pdf_counter
    directory = filedialog.askdirectory()
    if directory:
        file_paths = []
        for dirpath, dirnames, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".pdf"):
                    file_paths.append(os.path.join(dirpath, file))
        if file_paths:
            total_pdf_count = len(file_paths)
            processed_pdf_count = 0
            progress['maximum'] = total_pdf_count
            pdf_counter.config(text=f"PDFs left: {total_pdf_count - processed_pdf_count}")
            for file_path in file_paths:
                file_dir = os.path.dirname(file_path)
                output_dir = os.path.join(file_dir, "Extracted Images")
                os.makedirs(output_dir, exist_ok=True)
                extract_images_with_processing(file_path, output_dir)
                processed_pdf_count += 1
                pdf_counter.config(text=f"PDFs left: {total_pdf_count - processed_pdf_count}")
                progress['value'] = processed_pdf_count
                root.update()  # Refresh GUI after each PDF
        else:
            messagebox.showinfo("No PDFs Found", "No PDF files were found in the selected directory.")

def open_extracted_folder():
    if extracted_images_dir and os.path.exists(extracted_images_dir):
        subprocess.Popen(f'explorer "{extracted_images_dir}"')

def create_gui():
    global root, canvas, progress, image_counter, pdf_counter, extracted_image_count
    extracted_image_count = 0
    root = tk.Tk()
    root.title("Image Extractor")
    frame = ttk.Frame(root, padding="20")
    frame.grid()
    
    ttk.Label(frame, text="Select PDFs to Extract Images:").grid(row=0, column=0, pady=5)
    
    files_button = ttk.Button(frame, text="Select PDF Files", command=extract_and_process_images_files)
    files_button.grid(row=1, column=0, pady=5)
    
    dir_button = ttk.Button(frame, text="Select Directory", command=extract_and_process_images_directory)
    dir_button.grid(row=2, column=0, pady=5)
    
    canvas = tk.Canvas(frame, width=300, height=300, bg="gray")
    canvas.grid(row=3, column=0, pady=10)
    
    progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
    progress.grid(row=4, column=0, pady=10)
    
    pdf_counter = ttk.Label(frame, text="PDFs left: 0")
    pdf_counter.grid(row=5, column=0, pady=5)
    
    image_counter = ttk.Label(frame, text="Images Extracted: 0")
    image_counter.grid(row=6, column=0, pady=5)
    
    open_folder_button = ttk.Button(frame, text="Open Last Extracted Images Folder", command=open_extracted_folder)
    open_folder_button.grid(row=7, column=0, pady=10)
    
    root.mainloop()

# ----- Command-Line Interface (CLI) functionality -----
def process_pdf_file(file_path):
    """Process a single PDF file and return the output directory and list of extracted images."""
    file_dir = os.path.dirname(file_path)
    output_dir = os.path.join(file_dir, "Extracted Images")
    os.makedirs(output_dir, exist_ok=True)
    extracted_paths = extract_images_with_processing(file_path, output_dir)
    return output_dir, extracted_paths

def main_cli():
    parser = argparse.ArgumentParser(description="Image Extractor from PDF")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', nargs='+', help="Path(s) to PDF file(s) to process.")
    group.add_argument('--dir', help="Directory to search for PDF files to process.")
    
    args = parser.parse_args()

    results = {}

    if args.file:
        for file_path in args.file:
            if os.path.isfile(file_path) and file_path.lower().endswith(".pdf"):
                out_dir, extracted_paths = process_pdf_file(file_path)
                results[file_path] = {"output_dir": out_dir, "extracted_paths": extracted_paths}
            else:
                print(f"File {file_path} is not a valid PDF file.")
    elif args.dir:
        if os.path.isdir(args.dir):
            pdf_files = []
            for root_dir, _, files in os.walk(args.dir):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_files.append(os.path.join(root_dir, file))
            if pdf_files:
                for file_path in pdf_files:
                    out_dir, extracted_paths = process_pdf_file(file_path)
                    results[file_path] = {"output_dir": out_dir, "extracted_paths": extracted_paths}
            else:
                print(f"No PDF files found in directory {args.dir}.")
        else:
            print(f"{args.dir} is not a valid directory.")

    # Output the results
    for pdf, info in results.items():
        print(f"Processed PDF: {pdf}")
        print(f"Extracted Images Directory: {info['output_dir']}")
        if info['extracted_paths']:
            print("Extracted images:")
            for img in info['extracted_paths']:
                print(f"  {img}")
        else:
            print("No images extracted.")
        print("-" * 40)

# ----- Main entry point -----
if __name__ == "__main__":
    # If command-line arguments are provided, run in CLI mode.
    if len(sys.argv) > 1:
        main_cli()
    else:
        create_gui()
