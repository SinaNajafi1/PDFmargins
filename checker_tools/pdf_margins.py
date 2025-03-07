from utils import get_content_box, cm_to_pts

top_margin_cm = 3
bottom_margin_cm = 3
left_margin_cm = 2.5
right_margin_cm = 2.5

top_margin_pts = cm_to_pts(top_margin_cm)
bottom_margin_pts = cm_to_pts(bottom_margin_cm)
left_margin_pts = cm_to_pts(left_margin_cm)
right_margin_pts = cm_to_pts(right_margin_cm)

tolerance_other = cm_to_pts(0.2) # 0.2 cm error allowance.
tolerance_bottom = cm_to_pts(0.2)


def check_pdf_margins(doc):

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
        bottom_ok = actual_bottom_margin >= bottom_margin_pts - tolerance_bottom

        incorrect_margins = [] # All the margins should be correct to not append the page and mark it as incorrect
        if not left_ok:
            incorrect_margins.append(f"Left ({actual_left_margin:.2f} pts)")
            # page.draw_line((content_bbox.x0, page_rect.y0), (content_bbox.x0, page_rect.y1), color=(1, 0, 0), width=2) # Draw a red line on the side of the text violating the margin rules.
        if not top_ok:
            incorrect_margins.append(f"Top ({actual_top_margin:.2f} pts)")
            # page.draw_line((page_rect.x0, content_bbox.y0), (page_rect.x1, content_bbox.y0), color=(1, 0, 0), width=2)
        if not right_ok:
            incorrect_margins.append(f"Right ({actual_right_margin:.2f} pts)")
            # page.draw_line((content_bbox.x1, page_rect.y0), (content_bbox.x1, page_rect.y1), color=(1, 0, 0), width=2)
        if not bottom_ok:
            incorrect_margins.append(f"Bottom ({actual_bottom_margin:.2f} pts)")
            # page.draw_line((page_rect.x0, content_bbox.y1), (page_rect.x1, content_bbox.y1), color=(1, 0, 0), width=2)

        if incorrect_margins:
            incorrect_pages.append((page_number + 1, incorrect_margins)) # 1 based index for page number.

            page.draw_rect(content_bbox, color=(1, 0, 0), width=2)
            # Draw a red border around the text box violating the margin rules (For debug, where we draw the bounding box that margins are measured from on all four sides).

    return incorrect_pages
