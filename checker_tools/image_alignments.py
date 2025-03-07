from utils import get_content_box, cm_to_pts

image_alignment = "left"
tolerance_other = cm_to_pts(0.2)

left_margin_cm = 2.5
right_margin_cm = 2.5

left_margin_pts = cm_to_pts(left_margin_cm)
right_margin_pts = cm_to_pts(right_margin_cm)


def check_image_alignments(doc):

    incorrect_pages = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        page_rect = page.rect
        content_bbox = get_content_box(page)

        if content_bbox is None:
            continue

        content_bbox, image_positions = content_bbox
        incorrect_images = [] # Image alignments.
        for rect in image_positions:
            img_x_center = (rect.x0 + rect.x1) / 2  # Find the center of the image.

            if image_alignment == "left":
                if abs(rect.x0 - left_margin_pts) > tolerance_other:  # Check if left-aligned.
                    incorrect_images.append((rect, "<-- Image Should be LEFT Aligned!"))

            elif image_alignment == "right":
                if abs(page_rect.width - rect.x1 - right_margin_pts) > tolerance_other:  # Check if right-aligned.
                    incorrect_images.append((rect, "Image Should be RIGHT Aligned! -->"))

            elif image_alignment == "center":
                page_center = page_rect.width / 2
                if abs(img_x_center - page_center) > tolerance_other:  # Check if centered.
                    incorrect_images.append((rect, "Align Image to CENTER!"))

        for img_rect, message in incorrect_images:
            page.draw_rect(img_rect, color=(1, 0, 0), width=2) # Draw blue border around incorrectly aligned images.
            text_x = img_rect.x0
            text_y = img_rect.y0 - 10  # Place text just above the image.
            page.insert_text((text_x, text_y), message, fontsize=10, color=(1, 0, 0))

        if incorrect_images:
            incorrect_pages.append((page_number + 1, [f"Images not {image_alignment}-aligned."]))

    return incorrect_pages
