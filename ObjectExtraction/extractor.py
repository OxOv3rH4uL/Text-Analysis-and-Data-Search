# import fitz  # PyMuPDF
# from PIL import Image, ImageDraw

# def visualize_vector_graphics(pdf_path, output_prefix):
#     doc = fitz.open(pdf_path)

#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         pix = page.get_pixmap()  # Render page to image
#         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

#         draw = ImageDraw.Draw(img)

#         # Get vector graphic elements (lines, curves, polygons, etc)
#         drawings = page.get_drawings()

#         for d in drawings:
#             rect = d["rect"]
#             # rect is fitz.Rect with (x0, y0, x1, y1)
#             # Draw rectangle around vector graphic in red
#             draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], outline="red", width=2)

#         # Save the annotated image
#         img.save(f"{output_prefix}_page{page_num+1}_graphics.png")
#         print(f"Saved visualization for page {page_num+1}")

# # Usage
# visualize_vector_graphics("object.pdf", "output/visualized")

# import layoutparser as lp
# import cv2
# import matplotlib.pyplot as plt


# image = cv2.imread("object.jpg")
# image = image[..., ::-1]

# model = lp.EfficientDetLayoutModel('lp://HJDatasetEfficientDet/config')

# layout = model.detect(image)
# lp.draw_box(image, layout, box_width=3)

# text_blocks = lp.Layout([b for b in layout if b.type=='Text'])
# figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
# # text_blocks = lp.Layout([b for b in text_blocks \
# #                    if not any(b.is_in(b_fig) for b_fig in figure_blocks)])

# h, w = image.shape[:2]

# left_interval = lp.Interval(0, w/2*1.05, axis='x').put_on_canvas(image)

# left_blocks = text_blocks.filter_by(left_interval, center=True)
# left_blocks.sort(key = lambda b:b.coordinates[1], inplace=True)

# right_blocks = [b for b in text_blocks if b not in left_blocks]
# right_blocks.sort(key = lambda b:b.coordinates[1], inplace=True)

# # And finally combine the two list and add the index
# # according to the order
# text_blocks = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

# lp.draw_box(image, text_blocks,
#             box_width=3,
#             show_element_id=True)


# plt.figure(figsize=(12, 16))
# plt.imshow(image_with_text_ids)
# plt.axis("off")
# plt.title("Detected Layout with Text Blocks")
# plt.show()


import layoutparser as lp
import cv2
import matplotlib.pyplot as plt

# Load image
image = cv2.imread("object.jpg")
image = image[..., ::-1]  # Convert BGR to RGB

# Use the Tesseract-based OCR Layout Model
ocr_agent = lp.TesseractAgent(languages='eng')

layout = ocr_agent.detect(image)

# Draw detected text boxes
image_with_boxes = lp.draw_box(image, layout, box_width=3, show_element_id=True)

plt.figure(figsize=(12, 16))
plt.imshow(image_with_boxes)
plt.axis("off")
plt.title("Detected Text Layout (Tesseract OCR)")
plt.show()
