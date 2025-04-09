from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw, ImageFilter
import io
import base64

app = Flask(__name__)

def hexColor(color):
    def hex2dec(hex_str):
        return int(hex_str, 16)
    r = hex2dec(color[1:3])
    g = hex2dec(color[3:5])
    b = hex2dec(color[5:7])
    return (r, g, b)

def platno(width, height, color):
    return Image.new('RGB', (width, height), color)

def filled_circle(im, S, r, color):
    if r <= 0:
        return
    draw = ImageDraw.Draw(im)
    left_up = (S[0] - r, S[1] - r)
    right_down = (S[0] + r, S[1] + r)
    draw.ellipse([left_up, right_down], fill=color)

def filled_rectangle(im, x1, x2, y1, y2, color):
    for x in range(x1, x2):
        for y in range(y1, y2):
            im.putpixel((x, y), color)
    return im

def line1(im, A, B, color, thickness):
    draw = ImageDraw.Draw(im)
    draw.line([A, B], fill=color, width=thickness)

def triangle(im, A, B, C, color):
    V = sorted([A, B, C], key=lambda p: p[1])
    left = linePixels(V[0], V[1]) + linePixels(V[1], V[2])
    right = linePixels(V[0], V[2])

    Xmax = max(A[0], B[0], C[0])
    Xmin = min(A[0], B[0], C[0])

    if V[1][0] == Xmax:
        left, right = right, left

    for y in range(getY(V[0]), getY(V[2]) + 1):
        x1 = Xmax
        for X in left:
            if X[1] == y and X[0] < x1:
                x1 = X[0]
        x2 = Xmin
        for X in right:
            if X[1] == y and X[0] > x2:
                x2 = X[0]
        if x2 < 0:
            continue
        if x2 > im.width:
            x2 = im.width - 1
        if x1 < 0:
            x1 = 0
        for x in range(x1, x2 + 1):
            im.putpixel((x, y), color)

def simulate_protanopia(im):
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = im.getpixel((x, y))
            new_r = int(0.567 * r + 0.433 * g)
            new_g = int(0.558 * r + 0.442 * g)
            new_b = b
            im.putpixel((x, y), (new_r, new_g, new_b))
    return im

def invert_colors(im):
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = im.getpixel((x, y))
            new_r = 255 - r
            new_g = 255 - g
            new_b = 255 - b
            im.putpixel((x, y), (new_r, new_g, new_b))
    return im

def blur_image(im):
    return im.filter(ImageFilter.GaussianBlur(radius=5))

def generate_image_from_ves(ves_code):
    obr = None
    sunset_colors = ["#FFEB99", "#FFD170", "#FFB84D", "#FFAA3E", "#F99B72", "#F28A8B", "#E37F9E", "#D86F94", "#D15F8C", "#B9446E"]

    for line in ves_code.splitlines():
        line = line.strip()
        parts = line.split()

        if parts[0] == "VES":
            continue

        if parts[0] == "FILL_CIRCLEX":
            S = (int(parts[1]), int(parts[2]))
            r = int(parts[3])
            times = int(parts[4])
            color_keyword = parts[5]
            if color_keyword == "SUNSET":
                colors = sunset_colors
            for i in range(times):
                prvy_r = r - i * 15
                if prvy_r > 0:
                    color = colors[i]
                    rgb_color = hexColor(color)
                    filled_circle(obr, S, prvy_r, rgb_color)

        if parts[0] == "FILL_RECTANGLE":
            x1 = int(parts[1])
            x2 = int(parts[2])
            y1 = int(parts[3])
            y2 = int(parts[4])
            color = parts[5]
            rgb_color = hexColor(color)
            obr = filled_rectangle(obr, x1, x2, y1, y2, rgb_color)

        if parts[0] == "FILL_CIRCLE":
            S = (int(parts[1]), int(parts[2]))
            r = int(parts[3])
            color = parts[4]
            rgb_color = hexColor(color)
            filled_circle(obr, S, r, rgb_color)

        if parts[0] == "LINE":
            A = (int(parts[1]), int(parts[3]))
            B = (int(parts[2]), int(parts[4]))
            color = parts[6]
            rgb_color = hexColor(color)
            thickness = int(parts[5])
            line1(obr, A, B, rgb_color, thickness)

        if parts[0] == "FILL_TRIANGLE":
            A = (int(parts[1]), int(parts[2]))
            B = (int(parts[3]), int(parts[4]))
            C = (int(parts[5]), int(parts[6]))
            color = parts[7]
            rgb_color = hexColor(color)
            triangle(obr, A, B, C, rgb_color)

        if parts[0] == "CIRCLE":
            farba = hexColor(parts[5])
            S = [int(parts[1]), int(parts[2])]
            r = int(parts[3])
            thickness = int(parts[4])
            filled_circle(obr, S, r, farba)

        if parts[0] == "GREYSCALE":
            obr = simulate_protanopia(obr)

        if parts[0] == "COLORBLIND":
            obr = simulate_protanopia(obr)

        if parts[0] == "INVERTED":
            obr = invert_colors(obr)

        if parts[0] == "BLUR":
            obr = blur_image(obr)

        if parts[0] == "TRIANGLE":
            color = parts[8]
            rgb_color = hexColor(color)
            thickness = parts[7]
            triangle(obr, (int(parts[1]), int(parts[2])), (int(parts[3]), int(parts[4])), rgb_color)

    img_io = io.BytesIO()
    obr.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return img_base64
