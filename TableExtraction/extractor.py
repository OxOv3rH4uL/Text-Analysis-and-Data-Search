import os
import json
import argparse
import fitz  # PyMuPDF
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
import pandas as pd

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_text_pages(pdf_plumber, out_dir):
    """Extract words with coordinates from each page using pdfplumber."""
    text_data = {}
    for i, page in enumerate(pdf_plumber.pages, 1):
        words = page.extract_words()  # list of dicts with 'text','x0','x1','top','bottom'
        page_dict = {"words": words}
        text_path = os.path.join(out_dir, f"page_{i:03}_text.json")
        with open(text_path, "w", encoding="utf-8") as f:
            json.dump(page_dict, f, indent=2)
        text_data[i] = page_dict
    return text_data

def extract_tables_pages(pdf_plumber, out_dir):
    """Extract tables using pdfplumber for each page."""
    for i, page in enumerate(pdf_plumber.pages, 1):
        tables = page.extract_tables()  # list of tables (rows of cells)
        for ti, table in enumerate(tables):
            if not table: 
                continue
            df = pd.DataFrame(table)
            csv_path = os.path.join(out_dir, f"page_{i:03}_table_{ti}.csv")
            # Write CSV without header (tables usually have no separate header row here)
            df.to_csv(csv_path, index=False, header=False)
        # If no tables found, one could mark or log that
    return

def extract_tables_ocr(pdf_path, pages, out_dir):
    """Attempt OCR-based table/text extraction on given pages (scanned)."""
    # Convert pages to images using pdf2image
    images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=max(pages))
    for i in pages:
        img = images[i-1]  # PIL image for page i
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        # Binarize (inverted) for finding lines
        _, thresh = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # Detect horizontal lines by morphology
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(img_cv.shape[1]/30), 1))
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        # Detect vertical lines by morphology
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(img_cv.shape[0]/30)))
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        # Combine lines to get table mask (this is a simplification)
        mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
        # (Optional) find contours on mask to isolate table regions...
        # Fallback: OCR entire page or use pytesseract data
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)
        ocr_data = ocr_data[ocr_data.conf != -1]  # remove empty
        ocr_csv = os.path.join(out_dir, f"page_{i:03}_ocr.csv")
        ocr_data.to_csv(ocr_csv, index=False)
    return

def extract_images(pdf_fitz, out_dir):
    """Extract embedded images from each page using PyMuPDF."""
    for i in range(len(pdf_fitz)):
        page = pdf_fitz[i]
        img_list = page.get_images(full=True)
        for img_index, img_info in enumerate(img_list, 1):
            xref = img_info[0]
            base_image = pdf_fitz.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]
            img_filename = os.path.join(out_dir, f"page_{i+1:03}_img_{img_index}.{img_ext}")
            with open(img_filename, "wb") as f_img:
                f_img.write(img_bytes)
    return

def detect_captions(pdf_fitz, text_data, out_dir):
    """Associate nearby text as captions for each image on each page."""
    for i in range(len(pdf_fitz)):
        page = pdf_fitz[i]
        page_dict = page.get_text("dict")
        # Extract image blocks from PyMuPDF dict
        img_blocks = [b for b in page_dict["blocks"] if b["type"] == 1]
        text_blocks = [b for b in page_dict["blocks"] if b["type"] == 0]
        for img_idx, img in enumerate(img_blocks, 1):
            ibox = img["bbox"]  # (x0, y0, x1, y1) of image
            caption_text = ""
            # Find text blocks whose top is below the image bottom and horizontally overlapping
            for tb in text_blocks:
                (tx0, ty0, tx1, ty1) = tb["bbox"]
                if ty0 >= ibox[3] and tx0 < ibox[2] and tx1 > ibox[0]:
                    # combine all spans in this block as one line
                    for line in tb["lines"]:
                        for span in line["spans"]:
                            caption_text += span["text"]
                        caption_text += " "
            if caption_text.strip():
                cap_filename = os.path.join(out_dir, f"page_{i+1:03}_img_{img_idx}_caption.txt")
                with open(cap_filename, "w", encoding="utf-8") as fcap:
                    fcap.write(caption_text.strip())
    return

def main(pdf_path, output_dir):
    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    root_out = os.path.join(output_dir, basename)
    ensure_dir(root_out)

    # Open PDF with both libraries
    pdf_plumber = pdfplumber.open(pdf_path)
    pdf_fitz = fitz.open(pdf_path)

    # 1. Extract text (words with coords) per page
    text_out = os.path.join(root_out, "text")
    ensure_dir(text_out)
    text_data = extract_text_pages(pdf_plumber, text_out)

    # 2. Extract tables (digital) per page
    tables_out = os.path.join(root_out, "tables")
    ensure_dir(tables_out)
    extract_tables_pages(pdf_plumber, tables_out)

    # 3. Check for pages with no tables (or for scanned pages)
    #    Here as an example, we assume any page with no table triggers OCR.
    pages_to_ocr = [i for i in range(1, len(pdf_plumber.pages)+1)
                    if not pdf_plumber.pages[i-1].extract_tables()]
    if pages_to_ocr:
        ocr_out = os.path.join(root_out, "tables_ocr")
        ensure_dir(ocr_out)
        extract_tables_ocr(pdf_path, pages_to_ocr, ocr_out)

    # 4. Extract images from PDF
    images_out = os.path.join(root_out, "images")
    ensure_dir(images_out)
    extract_images(pdf_fitz, images_out)

    # 5. Detect captions (text near images)
    detect_captions(pdf_fitz, text_data, images_out)

    pdf_plumber.close()
    pdf_fitz.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text, tables, and images from a PDF.")
    parser.add_argument("--input", required=True, help="Input PDF file path")
    parser.add_argument("--output_dir", default="output", help="Directory to store outputs")
    args = parser.parse_args()
    main(args.input, args.output_dir)