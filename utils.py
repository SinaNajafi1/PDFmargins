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
    text_blocks = page.get_text("words") # Getting blocks of contents separately (texts, headers, footers, paragraphs).
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
