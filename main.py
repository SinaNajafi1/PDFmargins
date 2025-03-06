import fitz
import os

def cm_to_pts(cm):
    """
    PDFs use points (pts) instead of cm or inches. 1 cm ≈ 28.346 points.
    """
    return cm * 28.346


pdf_file = "examples/Japok.pdf"
top_margin_cm = 3
bottom_margin_cm = 3
left_margin_cm = 2.5
right_margin_cm = 2.5
image_alignment = "left"

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
        """
        x0 the starting horizontal position of the text block (from the left).
        y0 the starting vertical position of the text block (from the top).
        x1 the ending horizontal position of the text block (from the left).
        y1 the ending vertical position of the text block (from the top).
        """

        text_bbox |= fitz.Rect(x0, y0, x1, y1)

    image_bbox = fitz.Rect()
    image_positions = []

    for img in page.get_images(full=True):
        for rect in page.get_image_rects(img[0]):
            image_bbox |= rect # Union of all image rectangles.
            image_positions.append(rect)

    vector_bbox = fitz.Rect()
    for draw in page.get_drawings():
        vector_bbox |= draw["rect"] # bounding the vector graphics.

    full_bbox = text_bbox | image_bbox | vector_bbox # Union of text and image bounding boxes and vector graphics so paragraphs and images won't be considered as separated boxes.

    if full_bbox.is_empty or full_bbox.get_area() < cm_to_pts(0.5) ** 2:
        return None # No content detection will return None

    return full_bbox, image_positions


def check_pdf_margins(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    incorrect_pages = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        page_rect = page.rect # Each page dimension (width and height).
        content_bbox, image_positions = get_content_box(page)

        if content_bbox is None:
            continue # Skip the page with no content.

        # These are actual margins based on empty space that will be computed according to text box and below we compare with margins user gave as input.
        # The drawn borders actually represent the border sides, from where we calculate the current margin.
        actual_left_margin = content_bbox.x0
        actual_top_margin = content_bbox.y0
        actual_right_margin = page_rect.width - content_bbox.x1
        actual_bottom_margin = page_rect.height - content_bbox.y1

        left_ok = abs(actual_left_margin - left_margin_pts) <= tolerance_other
        top_ok = abs(actual_top_margin - top_margin_pts) <= tolerance_other
        right_ok = abs(actual_right_margin - right_margin_pts) <= tolerance_other
        bottom_ok = abs(actual_bottom_margin - bottom_margin_pts) <= tolerance_bottom

        incorrect_margins = [] # All the margins should be correct to not append the page and mark it as incorrect
        if not left_ok:
            incorrect_margins.append(f"Left ({actual_left_margin:.2f} pts)")
            #page.draw_line((content_bbox.x0, page_rect.y0), (content_bbox.x0, page_rect.y1), color=(1, 0, 0), width=2) # Draw a red line on the side of the text violating the margin rules.
        if not top_ok:
            incorrect_margins.append(f"Top ({actual_top_margin:.2f} pts)")
            #page.draw_line((page_rect.x0, content_bbox.y0), (page_rect.x1, content_bbox.y0), color=(1, 0, 0), width=2)
        if not right_ok:
            incorrect_margins.append(f"Right ({actual_right_margin:.2f} pts)")
            #page.draw_line((content_bbox.x1, page_rect.y0), (content_bbox.x1, page_rect.y1), color=(1, 0, 0), width=2)
        if not bottom_ok:
            incorrect_margins.append(f"Bottom ({actual_bottom_margin:.2f} pts)")
            #page.draw_line((page_rect.x0, content_bbox.y1), (page_rect.x1, content_bbox.y1), color=(1, 0, 0), width=2)

        if incorrect_margins:
            incorrect_pages.append((page_number + 1, incorrect_margins)) # 1 based index for page number.

            page.draw_rect(content_bbox, color=(1, 0, 0), width=2)
            # Draw a red border around the text box violating the margin rules (For debug, where we draw the bounding box that margins are measured from on all four sides).

        incorrect_images = [] # Image alignments.
        for rect in image_positions:
            img_x_center = (rect.x0 + rect.x1) / 2  # Find the center of the image.

            if image_alignment == "left":
                if abs(rect.x0 - left_margin_pts) > tolerance_other:  # Check if left-aligned.
                    incorrect_images.append(rect)

            elif image_alignment == "right":
                if abs(page_rect.width - rect.x1 - right_margin_pts) > tolerance_other:  # Check if right-aligned.
                    incorrect_images.append(rect)

            elif image_alignment == "center":
                page_center = page_rect.width / 2
                if abs(img_x_center - page_center) > tolerance_other:  # Check if centered.
                    incorrect_images.append(rect)

        for img_rect in incorrect_images:
            page.draw_rect(img_rect, color=(0, 0, 1), width=2) # Draw blue border around incorrectly aligned images.

        if incorrect_images:
            incorrect_pages.append((page_number + 1, incorrect_margins + [f"Images not {image_alignment}-aligned."]))

    doc.save(output_path)
    doc.close()

    if incorrect_pages:
        print("Margin or alignment incorrect on the following pages:")
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
