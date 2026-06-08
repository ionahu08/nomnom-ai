#!/usr/bin/env python3
"""
Helper script: Generate a sample nutrition label PDF for testing.

This creates a realistic nutrition label that we can use to test
the PDF parsing in 02_pdf_parsing.py.

Usage:
    python create_sample_pdf.py

Output:
    Creates: learning_lab/phase_3/sample_nutrition_label.pdf
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from pathlib import Path


def create_nutrition_label_pdf(output_path: str = "learning_lab/phase_3/sample_nutrition_label.pdf"):
    """
    Generate a sample nutrition label PDF.

    Args:
        output_path: Where to save the PDF
    """

    # Create PDF (use smaller margins to fit everything)
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Start from top with tighter spacing
    y = height - 0.5*inch

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(0.5*inch, y, "NUTRITION FACTS")
    y -= 0.25*inch

    # Product name
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.5*inch, y, "Organic Whole Grain Bread")
    y -= 0.2*inch

    # Serving size section
    c.setFont("Helvetica", 10)
    c.drawString(0.5*inch, y, "Serving Size: 2 slices (56g)")
    y -= 0.15*inch
    c.drawString(0.5*inch, y, "Servings Per Container: 10")
    y -= 0.2*inch

    # Calories
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.5*inch, y, "Calories: 160")
    y -= 0.25*inch

    # Macronutrients section header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5*inch, y, "NUTRITION INFORMATION")
    y -= 0.2*inch

    # Nutrition facts
    c.setFont("Helvetica", 9)
    nutrients = [
        ("Total Fat", "2g", "3%"),
        ("Saturated Fat", "0g", "0%"),
        ("Trans Fat", "0g", "0%"),
        ("Cholesterol", "0mg", "0%"),
        ("Sodium", "320mg", "14%"),
        ("Total Carbohydrate", "28g", "10%"),
        ("Dietary Fiber", "4g", "14%"),
        ("Total Sugars", "2g", ""),
        ("Protein", "6g", "12%"),
        ("Vitamin D", "0mcg", "0%"),
        ("Calcium", "80mg", "6%"),
        ("Iron", "2mg", "11%"),
        ("Potassium", "120mg", "3%"),
    ]

    for nutrient, amount, percent in nutrients:
        text = f"{nutrient} {amount}"
        c.drawString(0.7*inch, y, text)
        if percent:
            c.drawString(4*inch, y, percent)
        y -= 0.15*inch

    # Ingredients section
    y -= 0.1*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5*inch, y, "INGREDIENTS:")
    y -= 0.15*inch

    c.setFont("Helvetica", 9)
    c.drawString(0.7*inch, y, "Whole wheat flour, water, yeast, salt, wheat gluten, vinegar")
    y -= 0.2*inch

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(0.5*inch, y, "* Percent Daily Values based on a 2,000 calorie diet.")

    # Save
    c.save()
    print(f"✅ Created: {output_path}")


if __name__ == "__main__":
    try:
        create_nutrition_label_pdf()
        print("\nNow you can test the PDF parser with:")
        print("  python 02_pdf_parsing.py")
    except ImportError:
        print("❌ reportlab not installed")
        print("\nInstall it with:")
        print("  pip install reportlab")
        print("\nThen run this script again:")
        print("  python create_sample_pdf.py")
