import fitz


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
    - It contains only a number (e.g., '1', '10').
    - It is near the bottom margin of the page.
    """
    bbox, text = block

    if not text.strip().isdigit():
        return False

    # Define bottom threshold (anything that matches the criteria going x (here 4.0 cm) pts from bottom).
    bottom_threshold = page_rect.height - cm_to_pts(4.0)

    return bbox.y0 > bottom_threshold # Block is near the bottom.
