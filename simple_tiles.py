# draw_text.py

from PIL import Image, ImageDraw, ImageFont
import argparse

def text(output_path):
    image = Image.new("RGB", (48, 48), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("Tests/fonts/NotoSans-Regular.ttf", 6)
    draw.text((24, 24), "1", fill="black", anchor="mm", font=font)

    draw.line((0, 0, 0, 47), "black")
    draw.line((0, 0, 47, 0), "black")
    draw.line((47, 47, 0, 47), "black")
    draw.line((47, 47, 47, 0 , "black")
    image.save(output_path)

if __name__ == "__main__":
    text("text.jpg")
