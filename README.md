# PNG to JSON Converter

Convert 2D drawing PNG images to JSON format with vector data, text extraction, and OCR.

## Features

✨ **Extracts:**
- **Vectors**: Shapes and contours (triangles, rectangles, polygons, etc.)
- **Lines**: Straight lines with start/end coordinates and length
- **Circles**: Circular shapes with center, radius, and area
- **Text**: OCR text recognition with bounding boxes and confidence scores

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Usage

```bash
python convert.py input.png output.json
```

### Example

```bash
python convert.py marmon_drawing.png marmon_output.json
```

## Output JSON Structure

```json
{
  "metadata": {
    "width": 800,
    "height": 600,
    "source": "drawing.png"
  },
  "vectors": [
    {
      "id": "vector_0",
      "type": "triangle",
      "points": [
        {"x": 100, "y": 50},
        {"x": 200, "y": 150},
        {"x": 50, "y": 150}
      ],
      "area": 5000,
      "perimeter": 380.2
    }
  ],
  "lines": [
    {
      "id": "line_0",
      "start": {"x": 10, "y": 20},
      "end": {"x": 200, "y": 150},
      "length": 234.5
    }
  ],
  "circles": [
    {
      "id": "circle_0",
      "center": {"x": 400, "y": 300},
      "radius": 50,
      "area": 7854.0
    }
  ],
  "text": [
    {
      "id": "text_0",
      "content": "Label Text",
      "confidence": 0.95,
      "bbox": {
        "x": 150,
        "y": 200,
        "width": 100,
        "height": 30
      }
    }
  ]
}
```

## How It Works

1. **Edge Detection**: Uses Canny edge detection to identify shape boundaries
2. **Contour Extraction**: Finds all contours and classifies them by shape type
3. **Line Detection**: Uses Hough Line Transform to detect straight lines
4. **Circle Detection**: Uses Hough Circle Transform for circular shapes
5. **Text Recognition**: Tesseract OCR extracts and localizes text with confidence scores

## Customization

Edit thresholds in `convert.py`:

- `cv2.Canny(50, 150)` - Edge detection sensitivity
- `minLineLength=30` - Minimum line length to detect
- `minRadius=5, maxRadius=100` - Circle size range

## For Technical Drawings (like MARMON)

When processing technical/engineering drawings:
- Text extraction will capture all labels, dimensions, and annotations
- Lines will include grid lines, construction lines, and view separators
- Contours will identify component shapes and detail sections
- Confidence scores help identify clear vs. poor quality text regions

## License

MIT
