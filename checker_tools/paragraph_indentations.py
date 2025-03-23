import fitz
from utils import get_content_box, cm_to_pts, is_page_number, is_footer, is_header, is_empty_space

expected_indentation = cm_to_pts(0.5)
tolerance = cm_to_pts(0.1)
indentation_limit = expected_indentation + tolerance
vertical_tolerance = 2  # Small vertical tolerance for misalignment

box_height = cm_to_pts(0.5)  # Height of the box used to mark the indentation.


def check_paragraph_indentations(doc):
    incorrect_pages = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        words = page.get_text("words")
        text_bboxes, image_positions, vector_bboxes = get_content_box(page)

        # Exclude irrelevant content (same logic as in pdf_margins).
        text_bboxes = [b for b in text_bboxes if not is_empty_space(b, page.rect)]
        text_bboxes = [b for b in text_bboxes if not is_footer(b, page.rect)]
        text_bboxes = [b for b in text_bboxes if not is_header(b, page.rect)]
        text_bboxes = [b for b in text_bboxes if not is_page_number(b, page.rect)]

        if not text_bboxes:
            continue

        text_left_margins = [b[0].x0 for b in text_bboxes]
        actual_left_margin = min(text_left_margins) if text_left_margins else 0

        incorrect_paragraphs = []

        paragraph_start_y_positions = sorted(set(b[0].y0 for b in text_bboxes))  # Unique Y positions of paragraphs sorted.

        # Only consider the first line of each paragraph.
        for y_pos in paragraph_start_y_positions:
            # Get all text boxes that start at this y-position (first line of a paragraph).
            paragraph_blocks = [b[0] for b in text_bboxes if abs(b[0].y0 - y_pos) < vertical_tolerance]

            if not paragraph_blocks:
                continue

            # To Find first word of the first sentence (strict filtering).
            sentence_words = sorted(
                [w for w in words if abs(w[1] - y_pos) < vertical_tolerance],
                key=lambda w: w[0]
            )

            if not sentence_words:
                continue

            first_word_x = sentence_words[0][0]  # X-coordinate of the first word of the first line.

            indentation_size = first_word_x - actual_left_margin # Compute Indentation Relative to Left Margin** and compare it with the indentation limit (given above) below.

            # Debugging output
            # print(f"Page {page_number + 1} | First Word X: {first_word_x:.2f} pts | "
            #      f"Actual Left Margin: {actual_left_margin:.2f} pts | "
            #      f"Indentation: {indentation_size:.2f} pts | Limit: {indentation_limit:.2f} pts")

            if indentation_size > indentation_limit:  # If indentation is incorrect, mark the paragraph draw rectangle around incorrect indentation space.
                incorrect_paragraphs.append((page_number + 1, y_pos, indentation_size))

                indent_rect = fitz.Rect(actual_left_margin, y_pos, first_word_x, y_pos + box_height)
                page.draw_rect(indent_rect, color=(1, 0, 0), width=2)

        if incorrect_paragraphs:
            incorrect_pages.append((page_number + 1, ["Incorrect paragraph indentation detected."]))

    return incorrect_pages
