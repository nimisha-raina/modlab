"""Create printable PNG and SVG QR codes for the published student lesson.

Requires Pillow and reportlab. Pass the final, successfully deployed HTTPS URL:
    python3 scripts/create_lesson_qr.py https://your-lesson.example
"""

import argparse
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel


def create_qr(url, output):
    """Use square modules, a four-module quiet border, and high contrast."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Use the final public HTTPS lesson address.")
    code = QRCode(None, QRErrorCorrectLevel.Q)
    code.addData(url)
    code.make()
    border = 4
    side = code.getModuleCount() + 2 * border
    scale = 16
    picture = Image.new("RGB", (side * scale, side * scale), "white")
    draw = ImageDraw.Draw(picture)
    cells = []
    for row in range(code.getModuleCount()):
        for col in range(code.getModuleCount()):
            if code.isDark(row, col):
                x, y = col + border, row + border
                draw.rectangle((x * scale, y * scale, (x + 1) * scale - 1,
                                (y + 1) * scale - 1), fill="black")
                cells.append(f"M{x},{y}h1v1h-1z")
    output.mkdir(parents=True, exist_ok=True)
    picture.save(output / "lesson-qr.png", dpi=(300, 300))
    picture.resize((side * 6, side * 6), Image.Resampling.NEAREST).save(output / "lesson-qr-preview.png")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side} {side}" '
           'shape-rendering="crispEdges" role="img" aria-label="Scan to open the Class 8 electromagnetism lesson">'
           f'<rect width="{side}" height="{side}" fill="white"/>'
           f'<path d="{"".join(cells)}" fill="black"/></svg>\n')
    (output / "lesson-qr.svg").write_text(svg, encoding="utf-8")
    (output / "lesson-link.txt").write_text(url + "\n", encoding="utf-8")
    print(f"QR files saved in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[1] / "output" / "share")
    args = parser.parse_args()
    create_qr(args.url, args.output)
