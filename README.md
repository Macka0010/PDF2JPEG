# PDF2IMAGE CLI Tool – End-User Documentation

## Overview
The PDF2IMAGE CLI Tool allows users to extract images from PDF files. This tool can process either individual PDFs or all PDFs in a specified directory. The extracted images are saved in JPEG format within a subfolder named `Extracted Images`.
You can run this program in either a GUI or CLI.

## Command-Line Options

The tool accepts one of two mutually exclusive options:

### `--file`
Process one or more individual PDF files.
- **Syntax:**
  PDF2IMAGE.exe --file <path_to_pdf1> <path_to_pdf2> ...

### `--dir`
Process all PDF files in the specified directory (recursively, including subdirectories).
- **Syntax:**
  PDF2IMAGE.exe --dir <path_to_directory>

**Note:** Only one option (`--file` or `--dir`) may be used per execution.

## Examples

### Example 1: Processing Specific PDF Files
Scenario: A user wants to extract images from two PDFs located at `C:\Docs\file1.pdf` and `C:\Docs\file2.pdf`.

- **In Command Prompt (CMD):**
  "C:\Path\To\PDF2IMAGE.exe" --file "C:\Docs\file1.pdf" "C:\Docs\file2.pdf"

- **In PowerShell:**
  & "C:\Path\To\PDF2IMAGE.exe" --file "C:\Docs\file1.pdf" "C:\Docs\file2.pdf"

### Example 2: Processing an Entire Directory
Scenario: A user wants to extract images from all PDFs stored in `C:\Users\danny\Downloads\PDFs`, including any subdirectories.

- **In Command Prompt (CMD):**
  "C:\Path\To\PDF2IMAGE.exe" --dir "C:\Users\danny\Downloads\PDFs"

- **In PowerShell:**
  & "C:\Path\To\PDF2IMAGE.exe" --dir "C:\Users\danny\Downloads\PDFs"

## Output Details
For each processed PDF file:

- **Output Folder:** A subfolder named `Extracted Images` will be created in the same directory as the PDF file.
- **Image Files:** Extracted images are saved as JPEG files with a naming format similar to:
  `<PDF_Basename>_page_<page_number>_image_<image_counter>.jpg`
  For example, if processing `report.pdf`, images might be named:
  - report_page_1_image_1.jpg
  - report_page_1_image_2.jpg, etc.
