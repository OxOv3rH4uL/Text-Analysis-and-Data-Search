import fitz  # PyMuPDF
from PIL import Image, ImageDraw



def detection(big, small):
    return (
        small.x0 >= big.x0 and
        small.y0 >= big.y0 and
        small.x1 <= big.x1 and
        small.y1 <= big.y1
    )


def visualize_vector_graphics(pdf_path, output_prefix):
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        draw = ImageDraw.Draw(img)

        small_size = []
        med_size = []
        large_size = []

        drawings = page.get_drawings()

        for d in drawings:
            rect = d["rect"]

            width = abs(rect.x1 - rect.x0)
            height = abs(rect.y1 - rect.y0)
            area = width * height

            
            if area < 10000:
                # draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1],
                #                outline="blue", width=2)
                small_size.append(rect)

            elif 10000 <= area < 50000:
                # draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1],
                #                outline="red", width=2)
                med_size.append(rect)

            else:
                # Identify useful large boxes (filter)
                hw = width / 2
                hh = height / 2
                mw = pix.width / 2
                mh = pix.height / 2

                if abs(mw - hw) >= 100 or abs(mh - hh) >= 100:
                    # draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1],
                    #                outline="black", width=2)
                    large_size.append(rect)

        
        large_matches = []
        for s in small_size:
            for l in large_size:
                if detection(l, s):
                    large_matches.append(l)
                    break

        crop_count = 0
        uniq = set()
        for i in large_matches:
            uniq.add(i)

        for l in uniq:
            draw.rectangle([l.x0, l.y0, l.x1, l.y1], outline="green", width=4)
            x0, y0, x1, y1 = int(l.x0), int(l.y0), int(l.x1), int(l.y1)
            cropped = img.crop((x0, y0, x1, y1))
            crop_path = f"output/page{page_num+1}_diagram{crop_count+1}.png"
            cropped.save(crop_path)
            crop_count += 1

        
        # img.save(f"{output_prefix}_page{page_num + 1}_graphics.png")

        # img.save(f"{output_prefix}_page{page_num + 1}_graphics.png")
        print(f"Saved visualization for page {page_num + 1}")


# Run
visualize_vector_graphics("check.pdf", "output/vi")
