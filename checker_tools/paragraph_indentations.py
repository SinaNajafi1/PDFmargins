import fitz  # PyMuPDF
from utils import get_content_box, cm_to_pts

# Configuration parameters
EXPECTED_INDENTATION = cm_to_pts(0.5)  # Expected indent (e.g., 0.5 cm)
TOLERANCE = cm_to_pts(0.1)  # Allowed variation (e.g., ±0.1 cm)
INDENTATION_LIMIT = EXPECTED_INDENTATION + TOLERANCE
PARAGRAPH_HEIGHT_THRESHOLD = cm_to_pts(0.5)  # Height threshold for marking
VERTICAL_TOLERANCE = 2  # Small vertical tolerance for misalignment

def check_paragraph_indentations(doc):
    incorrect_pages = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        words = page.get_text("words")  # Extract words from the page
        text_bboxes, image_positions, vector_bboxes = get_content_box(page)  # Get actual content areas

        if not text_bboxes:
            continue  # Skip if page has no content

        # ✅ **Find True Left Margin (Avoiding 0.00 Issue)**
        text_left_margins = [b[0].x0 for b in text_bboxes]  # Extract left X positions
        actual_left_margin = min(text_left_margins) if text_left_margins else 0  # Get minimum (true left)

        incorrect_paragraphs = []

        # ✅ **Find First Sentences of Paragraphs**
        paragraph_start_y_positions = sorted(set(b[0].y0 for b in text_bboxes))  # Unique Y positions sorted

        for y_pos in paragraph_start_y_positions:
            # Get all text boxes that start at this y-position (first line of a paragraph)
            paragraph_blocks = [b[0] for b in text_bboxes if abs(b[0].y0 - y_pos) < VERTICAL_TOLERANCE]

            if not paragraph_blocks:
                continue  # Skip if no valid paragraph blocks found

            # ✅ **Find first word of the first sentence (strict filtering)**
            sentence_words = sorted(
                [w for w in words if abs(w[1] - y_pos) < VERTICAL_TOLERANCE],
                key=lambda w: w[0]
            )

            if not sentence_words:
                continue  # Skip if no words found at this position

            first_word_x = sentence_words[0][0]  # X-coordinate of the first word of the sentence

            # ✅ **Compute Indentation Relative to Left Margin**
            indentation_size = first_word_x - actual_left_margin

            # Debugging output
            print(f"Page {page_number + 1} | First Word X: {first_word_x:.2f} pts | "
                  f"Actual Left Margin: {actual_left_margin:.2f} pts | "
                  f"Indentation: {indentation_size:.2f} pts | Limit: {INDENTATION_LIMIT:.2f} pts")

            # If indentation is incorrect, mark the paragraph
            if indentation_size > INDENTATION_LIMIT:
                incorrect_paragraphs.append((page_number + 1, y_pos, indentation_size))

                # Draw rectangle around incorrect indentation space
                indent_rect = fitz.Rect(actual_left_margin, y_pos, first_word_x, y_pos + PARAGRAPH_HEIGHT_THRESHOLD)
                page.draw_rect(indent_rect, color=(1, 0, 0), width=2)

        if incorrect_paragraphs:
            incorrect_pages.append((page_number + 1, ["Incorrect paragraph indentation detected."]))

    return incorrect_pages
