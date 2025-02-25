import fitz
import os


def cm_to_pts(cm):
    """
    PDFs use points (pts) instead of cm or inches. 1 cm ≈ 28.35 points
    """
    return cm * 28.35


pdf_file = input("Enter the path to the PDF file: ")
top_margin_cm = float(input("Enter the top margin (cm): "))
bottom_margin_cm = float(input("Enter the bottom margin (cm): "))
left_margin_cm = float(input("Enter the left margin (cm): "))
right_margin_cm = float(input("Enter the right margin (cm): "))

top_margin_pts = cm_to_pts(top_margin_cm)
bottom_margin_pts = cm_to_pts(bottom_margin_cm)
left_margin_pts = cm_to_pts(left_margin_cm)
right_margin_pts = cm_to_pts(right_margin_cm)


def check_pdf_margins(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    incorrect_pages = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        page_rect = page.rect  # Each page dimension (width and height).
        text_blocks = page.get_text("blocks")  # Get text bounding boxes.
        incorrect_found = False  # Will be used to mark the incorrect pages.

        for block in text_blocks:
            x0, y0, x1, y1, _, _ = block
            """
            x0 the starting horizontal position of the text block (from the left).
            y0 the starting vertical position of the text block (from the top).
            x1 the ending horizontal position of the text block (from the left).
            y1 the ending vertical position of the text block (from the top).
            """
            if (x0 < left_margin_pts or
                y0 < top_margin_pts or
                (page_rect.width - x1) < right_margin_pts or
                (page_rect.height - y1) < bottom_margin_pts):

                incorrect_found = True

                rect = fitz.Rect(x0, y0, x1, y1)
                page.insert_rect(rect, color=(1, 0, 0), width=2) # Draw a red border around the text box violating the margin rules.

        if incorrect_found:
            incorrect_pages.append(page_number + 1) # 1-based index.

    doc.save(output_path)
    doc.close()

    if incorrect_pages:
        print(f"Margins incorrect on pages: {incorrect_pages}")
        print(f"Marked incorrect margins in the PDF and saved as: {output_path}")
    else:
        print("All pages have correct margins.")


output_folder = "output" # To ensure that output folder exists if not create.
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_file_path = os.path.join(output_folder, "annotated_output.pdf")
check_pdf_margins(pdf_file, output_file_path)
