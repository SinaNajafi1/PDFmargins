import fitz
import os


def cm_to_pts(cm):
    """
    PDFs use points (pts) instead of cm or inches. 1 cm ≈ 28.346 points.
    """
    return cm * 28.346


pdf_file = input("Enter the path to the PDF file: ")
top_margin_cm = float(input("Enter the top margin (cm): "))
bottom_margin_cm = float(input("Enter the bottom margin (cm): "))
left_margin_cm = float(input("Enter the left margin (cm): "))
right_margin_cm = float(input("Enter the right margin (cm): "))

top_margin_pts = cm_to_pts(top_margin_cm)
bottom_margin_pts = cm_to_pts(bottom_margin_cm)
left_margin_pts = cm_to_pts(left_margin_cm)
right_margin_pts = cm_to_pts(right_margin_cm)

tolerance_other = cm_to_pts(0.2) # 0.2 cm error allowance.
tolerance_bottom = cm_to_pts(0.2)


def get_content_box(page):
    """
    To get the bounding box of all visible content on the page, excluding page numbers.
    """
    text_blocks = page.get_text("words")
    text_bbox = fitz.Rect()

    for block in text_blocks:
        x0, y0, x1, y1, text = block[:5]

        text_bbox |= fitz.Rect(x0, y0, x1, y1)

    image_bbox = fitz.Rect()
    for img in page.get_images(full=True):
        for rect in page.get_image_rects(img[0]):
            image_bbox |= rect # Union of all image rectangles.

    vector_bbox = fitz.Rect()
    for draw in page.get_drawings():
        vector_bbox |= draw["rect"] # bounding the vector graphics.

    full_bbox = text_bbox | image_bbox | vector_bbox # Union of text and image bounding boxes and vector graphics so paragraphs and images won't be considered as separated boxes.

    if full_bbox.is_empty or full_bbox.get_area() < cm_to_pts(0.5) ** 2:
        return None # No content detection will return None

    return full_bbox


def check_pdf_margins(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    incorrect_pages = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        page_rect = page.rect # Each page dimension (width and height).
        content_bbox = get_content_box(page)

        if content_bbox is None:
            continue # Skip the page with no content.

        # These are actual margins based on empty space that will be computed according to text box and below we compare with margins user gave as input.
        # The drawn borders actually represent the border sides, from where we calculate the current margin.
        actual_left_margin = content_bbox.x0
        actual_top_margin = content_bbox.y0
        actual_right_margin = page_rect.width - content_bbox.x1
        actual_bottom_margin = page_rect.height - content_bbox.y1

        left_ok = (left_margin_pts - tolerance_other) <= actual_left_margin <= (left_margin_pts + tolerance_other)
        top_ok = (top_margin_pts - tolerance_other) <= actual_top_margin <= (top_margin_pts + tolerance_other)
        right_ok = (right_margin_pts - tolerance_other) <= actual_right_margin <= (right_margin_pts + tolerance_other)
        bottom_ok = (bottom_margin_pts - tolerance_bottom) <= actual_bottom_margin <= (bottom_margin_pts + tolerance_bottom)

        incorrect_margins = [] # All the margins should be correct to not append the page and mark it as incorrect
        if not left_ok:
            incorrect_margins.append(f"Left ({actual_left_margin:.2f} pts)")
        if not top_ok:
            incorrect_margins.append(f"Top ({actual_top_margin:.2f} pts)")
        if not right_ok:
            incorrect_margins.append(f"Right ({actual_right_margin:.2f} pts)")
        if not bottom_ok:
            incorrect_margins.append(f"Bottom ({actual_bottom_margin:.2f} pts)")

        if incorrect_margins:
            incorrect_pages.append((page_number + 1, incorrect_margins)) # 1 based index for page number.

            page.draw_rect(content_bbox, color=(1, 0, 0), width=2) # Draw a red border around the text box violating the margin rules.

    doc.save(output_path)
    doc.close()

    if incorrect_pages:
        print("Margins incorrect on the following pages:")
        for page, issues in incorrect_pages:
            print(f"Page {page}: {', '.join(issues)}")
        print(f"Marked incorrect margins in the PDF and saved as: {output_path}")
    else:
        print("All pages have correct margins.")


output_folder = "output" # To ensure that output folder exists if not create.
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_file_path = os.path.join(output_folder, "annotated_output.pdf")
check_pdf_margins(pdf_file, output_file_path)
