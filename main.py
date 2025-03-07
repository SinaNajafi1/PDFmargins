import fitz
import os
from checker_tools.image_alignments import check_image_alignments
from checker_tools.pdf_margins import check_pdf_margins


pdf_file = "examples/Japok.pdf"
output_folder = "output" # To ensure that output folder exists if not create.
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_file_path = os.path.join(output_folder, "annotated_output.pdf")

doc = fitz.open(pdf_file)
margins = check_pdf_margins(doc)
alignments = check_image_alignments(doc)

doc.save(output_file_path)
doc.close()

if margins or alignments:
    print("Margin or alignment incorrect on the following pages:")
    for page, issues in margins:
        print(f"Page {page}: {', '.join(issues)}")
    for page, issues in alignments:
        print(f"Page {page}: {', '.join(issues)}")
    print(f"Marked incorrect margins in the PDF and saved as: {output_file_path}")
else:
    print("All pages have correct margins and correct image alignments.")
