import fitz  # PyMuPDF
from PIL import Image, ImageDraw

def visualize_vector_graphics(pdf_path, output_prefix):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()  
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        draw = ImageDraw.Draw(img)

        drawings = page.get_drawings()
        coords = []
        for d in drawings:
            rect = d["rect"]
            # print(rect)
            dims = []
            width  = abs(rect.x1 - rect.x0)
            height = abs(rect.y1 - rect.y0)
            area   = width * height
            dims.append(width)
            dims.append(height)

            size = ""

            if area < 10000:
                size = "small"
            elif 10000 <= area < 50000:
                size = "medium"
                draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], outline="red", width=2)
            else:
                # if(width/2 >= pix.width/2 and height/2 >= pix.height/2):
                hw = width/2
                hh = height/2
                mw = pix.width/2
                mh = pix.height/2
                if(abs(mw-hw) >= 100 or abs(mh-hh) >= 100):
                # coords.append(dims)
                    draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], outline="black", width=2)
                # else:    
                    # draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], outline="green", width=2)

        img.save(f"{output_prefix}_page{page_num+1}_graphics.png")
        print(f"Saved visualization for page {page_num+1}")
        # print(coords)


# # # Usage
visualize_vector_graphics("check.pdf", "output/visualized")
# # import cv2

# # # Load the image
# # img = cv2.imread("object.jpg")
# # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # # Preprocess
# # blur = cv2.GaussianBlur(gray, (5,5), 0)
# # edges = cv2.Canny(blur, 50, 150)

# # # Find contours
# # contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# # for cnt in contours:
# #     # Approximate contour to reduce number of points
# #     approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

# #     # If the contour has 4 points, it's a potential rectangle
# #     if len(approx) == 4 and cv2.isContourConvex(approx):
# #         x, y, w, h = cv2.boundingRect(approx)
# #         aspect_ratio = w / float(h)

# #         # Filter out unlikely rectangles (too narrow, too small, etc.)
# #         if w > 50 and h > 50 and 0.5 < aspect_ratio < 2:
# #             cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# # cv2.imshow("Detected Rectangles", img)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()


