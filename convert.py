#!/usr/bin/env python3
"""
Convert PNG drawing to JSON with vectors, text, and OCR
Usage: python convert.py input.png output.json
"""

import cv2
import numpy as np
import json
import pytesseract
import sys
from PIL import Image

class DrawingToJSON:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        
        if self.image is None:
            raise FileNotFoundError(f"Cannot read image: {image_path}")
        
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.height, self.width = self.gray.shape
        
        self.results = {
            "metadata": {
                "width": self.width,
                "height": self.height,
                "source": image_path
            },
            "vectors": [],
            "lines": [],
            "circles": [],
            "text": []
        }
    
    def extract_vectors(self):
        """Extract shapes and contours"""
        edges = cv2.Canny(self.gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for idx, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 100:  # Skip very small contours
                continue
            
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) > 2:
                points = [{"x": int(p[0][0]), "y": int(p[0][1])} for p in approx]
                
                self.results["vectors"].append({
                    "id": f"vector_{idx}",
                    "type": self._classify_shape(approx),
                    "points": points,
                    "area": float(area),
                    "perimeter": float(cv2.arcLength(contour, True))
                })
    
    def _classify_shape(self, approx):
        """Classify shape by vertex count"""
        sides = len(approx)
        shapes = {3: "triangle", 4: "rectangle", 5: "pentagon", 6: "hexagon"}
        return shapes.get(sides, f"polygon_{sides}")
    
    def extract_lines(self):
        """Extract straight lines"""
        edges = cv2.Canny(self.gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=30, maxLineGap=10)
        
        if lines is not None:
            for idx, line in enumerate(lines):
                x1, y1, x2, y2 = line[0]
                length = float(np.sqrt((x2-x1)**2 + (y2-y1)**2))
                
                self.results["lines"].append({
                    "id": f"line_{idx}",
                    "start": {"x": int(x1), "y": int(y1)},
                    "end": {"x": int(x2), "y": int(y2)},
                    "length": length
                })
    
    def extract_circles(self):
        """Extract circles"""
        circles = cv2.HoughCircles(
            self.gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=5,
            maxRadius=100
        )
        
        if circles is not None:
            for idx, circle in enumerate(np.uint16(np.around(circles))[0, :]):
                x, y, r = circle
                self.results["circles"].append({
                    "id": f"circle_{idx}",
                    "center": {"x": int(x), "y": int(y)},
                    "radius": int(r),
                    "area": float(np.pi * r**2)
                })
    
    def extract_text(self):
        """Extract text using OCR"""
        try:
            data = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DICT)
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and int(data['conf'][i]) > 0:
                    self.results["text"].append({
                        "id": f"text_{i}",
                        "content": text,
                        "confidence": float(data['conf'][i]) / 100,
                        "bbox": {
                            "x": int(data['left'][i]),
                            "y": int(data['top'][i]),
                            "width": int(data['width'][i]),
                            "height": int(data['height'][i])
                        }
                    })
        except Exception as e:
            print(f"Warning: OCR failed - {e}")
    
    def process(self):
        """Process all elements"""
        print("🔍 Extracting vectors...")
        self.extract_vectors()
        
        print("📏 Extracting lines...")
        self.extract_lines()
        
        print("⭕ Extracting circles...")
        self.extract_circles()
        
        print("📝 Extracting text (OCR)...")
        self.extract_text()
        
        return self.results
    
    def save(self, output_path):
        """Save to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ Saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert.py input.png [output.json]")
        print("Example: python convert.py drawing.png output.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.json"
    
    try:
        converter = DrawingToJSON(input_file)
        converter.process()
        converter.save(output_file)
        print(f"\n📊 Results:")
        print(f"  - Vectors: {len(converter.results['vectors'])}")
        print(f"  - Lines: {len(converter.results['lines'])}")
        print(f"  - Circles: {len(converter.results['circles'])}")
        print(f"  - Text: {len(converter.results['text'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
