from utils import get_content_box, cm_to_pts, is_page_number, is_footer, is_header, is_empty_space

top_margin_cm = 3.0
bottom_margin_cm = 3.0
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
        text_bboxes, image_positions, vector_bboxes = get_content_box(page) # Get content blocks (text, images, vectors).

        text_bboxes = [b for b in text_bboxes if not is_empty_space(b, page.rect)]
        text_bboxes = [b for b in text_bboxes if not is_footer(b, page.rect)] # Header and footer as text.
        text_bboxes = [b for b in text_bboxes if not is_header(b, page.rect)]
        text_bboxes = [b for b in text_bboxes if not is_page_number(b, page.rect)] # All thext boxes without page number block.
        vector_bboxes = [v for v in vector_bboxes if not is_footer(v, page.rect)] # Excluding all the headers and footers as vector graphics (being close to top and bottom of the page are considered as header or footer).
        vector_bboxes = [v for v in vector_bboxes if not is_header(v, page.rect)]

        # print(f"Text blocks after header/footer removal: {[b[1] for b in text_bboxes]}") # Debug only to see what are the contents of the blocks included in the bboxes after excluding headers/footers, etc.

        all_content = [b[0] for b in text_bboxes] + image_positions + [v for v in vector_bboxes] # Now all the remaining blocks are unioned and then margins are calculated.

        if not all_content:
            continue # Skip the page with no content. Below the skip also for pages with too little content (specified length).

        total_text_length = sum(len(b[1].strip()) for b in text_bboxes)  # Sum lengths of text content.
        if total_text_length < 5:
            continue

        # Find page content edges to determine the whole text as one box whose borders are considered as actual margins.
        top_edge = min(block.y0 for block in all_content)
        bottom_edge = max(block.y1 for block in all_content)
        left_edge = min(block.x0 for block in all_content)
        right_edge = max(block.x1 for block in all_content)

        # These are actual margins based on empty space that will be computed according to text box and below we compare with margins user gave as input.
        # The drawn borders actually represent the border sides, from where we calculate the current margin.
        actual_left_margin = left_edge
        actual_top_margin = top_edge
        actual_right_margin = page_rect.width - right_edge
        actual_bottom_margin = page_rect.height - bottom_edge

        # for block in all_content: # Draw a red border around the text box violating the margin rules (For debug only where we draw the bounding box around all the text blocks(those included only i.e. not page numbers)).
        #    page.draw_rect(block, color=(1, 0, 0), width=1)

        left_ok = abs(actual_left_margin - left_margin_pts) <= tolerance_other
        top_ok = abs(actual_top_margin - top_margin_pts) <= tolerance_other
        right_ok = abs(actual_right_margin - right_margin_pts) <= tolerance_other
        bottom_ok = actual_bottom_margin >= bottom_margin_pts - tolerance_bottom

        incorrect_margins = [] # All the margins should be correct to not append the page and mark it as incorrect
        if not left_ok:
            incorrect_margins.append(f"Left ({actual_left_margin:.2f} pts)")
            page.draw_line((left_edge, page_rect.y0), (left_edge, page_rect.y1), color=(1, 0, 0), width=2) # Draw a red line on the side of the text violating the margin rules.
        if not top_ok:
            incorrect_margins.append(f"Top ({actual_top_margin:.2f} pts)")
            page.draw_line((page_rect.x0, top_edge), (page_rect.x1, top_edge), color=(1, 0, 0), width=2)
        if not right_ok:
            incorrect_margins.append(f"Right ({actual_right_margin:.2f} pts)")
            page.draw_line((right_edge, page_rect.y0), (right_edge, page_rect.y1), color=(1, 0, 0), width=2)
        if not bottom_ok:
            incorrect_margins.append(f"Bottom ({actual_bottom_margin:.2f} pts)")
            page.draw_line((page_rect.x0, bottom_edge), (page_rect.x1, bottom_edge), color=(1, 0, 0), width=2)

        if incorrect_margins:
            incorrect_pages.append((page_number + 1, incorrect_margins)) # 1 based index for page number.

    return incorrect_pages
