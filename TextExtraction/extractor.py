# import pdfplumber

# with pdfplumber.open("text.pdf") as pdf:
#     first_page = pdf.pages[0]
#     a = first_page.extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False, x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None)
#     print(a)


import pymupdf 
doc = pymupdf.open("text.pdf") # open a document
for page in doc: # iterate the document pages
  text = page.get_text() # get plain text encoded as UTF-8
  print(text)