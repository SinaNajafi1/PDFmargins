import fitz
import re


def cm_to_pts(cm):
    """
    PDFs use points (pts) instead of cm or inches. 1 cm ≈ 28.346 points.
    """
    return cm * 28.346


def get_content_box(page):
    """
    To get the bounding box of all visible content on the page, excluding page numbers.
    """
    text_blocks = page.get_text("blocks") # Getting blocks of contents separately (texts, headers, footers, paragraphs).
    text_bboxes = []  # List to hold individual text blocks.

    for block in text_blocks:
        x0, y0, x1, y1, text = block[:5]
        """
        x0 the starting horizontal position of the text block (from the left).
        y0 the starting vertical position of the text block (from the top).
        x1 the ending horizontal position of the text block (from the left).
        y1 the ending vertical position of the text block (from the top).
        """
        bbox = fitz.Rect(x0, y0, x1, y1)
        text_bboxes.append((bbox, text.strip()))  # Store individual text block

    image_positions = []

    for img in page.get_images(full=True):
        for rect in page.get_image_rects(img[0]):
            image_positions.append(rect)

    vector_bboxes = []
    for draw in page.get_drawings():
        vector_bboxes.append(draw["rect"]) # bounding the vector graphics.

    return text_bboxes, image_positions, vector_bboxes


def is_page_number(block, page_rect):
    """
    Detect if a text block is a page number.
    Criteria:
    - It contains only a number (e.g., '1', '10'). With re below for finding digits.
    - It is near the bottom margin of the page.
    """
    bbox, text = block

    expression = re.compile(r"^\d+$")
    if not expression.match(text.strip()):
        return False

    # Define bottom and top threshold. Anything that matches the criteria going x (here 4.0 cm which must be adjusted according to bottom and top margin) pts from bottom.
    bottom_threshold = page_rect.height - cm_to_pts(3.0)
    top_threshold = cm_to_pts(3.0)

    return bbox.y0 > bottom_threshold or bbox.y1 < top_threshold # Block is near the bottom or top.


def is_empty_space(block, page_rect):
    """
    Detect if a text block is empty space. To remove the empty space that appears in the bottom under page number.
    Criteria:
    - It contains no visible text.
    - It is near the bottom margin of the page (like footers).
    """
    bbox, text = block

    if text.strip() != "":
        return False  # Not empty space

    bottom_threshold = page_rect.height - cm_to_pts(3.0)
    return bbox.y0 > bottom_threshold


def is_header(block, page_rect):
    """
    Detect if a block (text or vector) is a header.
    Criteria:
    - It contains a known header pattern (if text-based).
    - It is near the top margin of the page.
    """
    if isinstance(block, tuple): # If the block contains 'text', that is having the matching pattern of bbox, text.
        bbox, text = block
        header_patterns = [
            r"^(Chapter|Section)\s+\d+(\.\d+)?\s*",  # Chapter or section numbers
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",  # Dates
            r"^\w+(\s+\w+)*\s*\d{4}$",  # Simple title pattern
        ]
        for pattern in header_patterns:
            if re.search(pattern, text.strip()):
                top_threshold = cm_to_pts(3.0)
                return bbox.y1 < top_threshold
    else:
        bbox = block  # Vector elements only have a bbox
        top_threshold = cm_to_pts(3.0)
        return bbox.y1 < top_threshold  # If near top, assume it's a header and the graphic is excluded (same for bottom) (Headers and footers are vector graphics rather that text).

    return False


def is_footer(block, page_rect):
    """
    Detect if a block (text or vector) is a footer.
    Criteria:
    - It contains a known footer pattern (if text-based).
    - It is near the bottom margin of the page.
    """
    if isinstance(block, tuple):
        bbox, text = block
        footer_patterns = [
            r"©\s?\d{4}",
            r"Copyright\s+\d{4}",
            r"(https?://\S+|www\.\S+)",
        ]
        bottom_threshold = page_rect.height - cm_to_pts(3.0)
        for pattern in footer_patterns:
            if re.search(pattern, text.strip()):
                return bbox.y1 > bottom_threshold
    else:
        bbox = block
        bottom_threshold = page_rect.height - cm_to_pts(3.0)
        return bbox.y1 > bottom_threshold

    return False
