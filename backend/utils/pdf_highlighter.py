import pymupdf  # import package PyMuPDF
import textwrap
import logging
import json

logger = logging.getLogger(__name__)


def get_highlight_color(color_name: str) -> tuple:
    """Get RGB color tuple for a given color name"""
    colors = {
        "green": (0, 0.8, 0),  # Green for main ideas
        "yellow": (1, 1, 0),  # Yellow for vocabulary
        "pink": (1, 0.7, 0.7),  # Pink for questions
        "blue": (0.5, 0.5, 1),  # Lighter blue for sub-ideas
    }
    return colors.get(color_name, (1, 1, 0))  # Default to yellow if color not found


def add_highlights(highlight_data, filename) -> str:
    """
    Add color-coded highlights and suggestions to a PDF file.

    Args:
        highlight_data (list): List of dictionaries containing content and highlight information
        filename (str): Path to the PDF file

    Returns:
        str: Path to the highlighted PDF file
    """
    logger.info("Adding highlights to %s", filename)

    # Log highlight data and save to file
    logger.info("Highlight data: %s", highlight_data)
    with open("highlight_data.json", "w") as f:
        json.dump(highlight_data, f)
    # return "highlighted_" + filename
    # Open document
    doc = pymupdf.open(filename)
    filename = filename.split("/")[-1]

    # Process each highlight
    for highlight in highlight_data:
        content = highlight["content"]
        color = get_highlight_color(highlight["highlight_type"]["color"])

        highlight["page"] = 0
        for i, page in enumerate(doc):
            rects = page.search_for(content)
            if rects:
                highlight["page"] = i
                # Add highlight annotation
                annot = page.add_highlight_annot(rects)
                annot.set_colors(stroke=color)
                annot.set_info(content=highlight["explanation"])
                annot.update()

    # Save the document
    try:
        logger.info("Saving highlighted file to %s", filename)
        doc.save("files/" + "highlighted_" + filename)

        return "files/" + "highlighted_" + filename
    except Exception as e:
        logger.error("Error saving highlighted file: %s", e)
        return None


if __name__ == "__main__":
    with open("highlight_data.json", "r") as f:
        highlight_data = json.load(f)
    add_highlights(highlight_data, "test.pdf")
