from flask import Flask, render_template, jsonify
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
    obr = Image.new('RGB', (width, height), color)
    return obr

def filled_circle(im, S, r, color):
    if r <= 0:
        return
    draw = ImageDraw.Draw(im)
    left_up = (S[0] - r, S[1] - r)
    right_down = (S[0] + r, S[1] + r)
    draw.ellipse([left_up, right_down], fill=color)

sunset_colors = ["#FFEB99", "#FFD170", "#FFB84D","#FFAA3E", "#F99B72", "#F28A8B","#E37F9E", "#D86F94", "#D15F8C", "#B9446E"]

def filled_rectangle(im, x1, x2, y1, y2, color):
    for x in range(x1, x2):
        for y in range(y1, y2):
            obr.putpixel((x, y), color)
    return obr

def line1(im, A, B, color, thickness):
    draw = ImageDraw.Draw(im)
    draw.line([A, B], fill=color, width=thickness)

def getY(point):
    return point[1]

def linePixels(A, B):
    pixels = []
    if A[0] == B[0]:
        if A[1] > B[1]:
            A, B = B, A
        for y in range(A[1], B[1] + 1):
            pixels.append((A[0], y))
    elif A[1] == B[1]:
        if A[0] > B[0]:
            A, B = B, A
        for x in range(A[0], B[0] + 1):
            pixels.append((x, A[1]))
    else:
        if A[0] > B[0]:
            A, B = B, A
        dx = B[0] - A[0]
        dy = B[1] - A[1]
        if abs(dy/dx) > 1:
            for y in range(min(A[1], B[1]), max(A[1], B[1]) + 1):
                x = int((y - A[1] + (dy/dx) * A[0]) * (dx/dy))
                pixels.append((x, y))
        else:
            for x in range(min(A[0], B[0]), max(A[0], B[0]) + 1):
                y = int((B[1] - A[1]) / (B[0] - A[0]) * (x - A[0]) + A[1])
                pixels.append((x, y))
    return pixels

def triangle(im, A, B, C, color):
    V = sorted([A, B, C], key=getY)
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

def line2(im, A, B, color):
    if A[0] == B[0]:
        if A[1] > B[1]:
            A, B = B, A
        for y in range(A[1], B[1] + 1):
            im.putpixel((A[0], y), color)
    elif A[1] == B[1]:
        if A[0] > B[0]:
            A, B = B, A
        for x in range(A[0], B[0] + 1):
            im.putpixel((x, A[1]), color)
    else:
        if A[0] > B[0]:
            A, B = B, A
        dx = B[0] - A[0]
        dy = B[1] - A[1]
        if abs(dy) > abs(dx):
            for y in range(min(A[1], B[1]), max(A[1], B[1]) + 1):
                x = int((y - A[1]) * dx / dy + A[0])
                im.putpixel((x, y), color)
        else:
            for x in range(A[0], B[0] + 1):
                y = int((y - A[0]) * dy / dx + A[1])
                im.putpixel((x, y), color)

def circle(im, S, r, color, thickness):
    for i in range(r, r - thickness, -1):
        for x in range(0, int(i / 2 ** (1 / 2)) + 1):
            y = int((i ** 2 - x ** 2) ** (1 / 2))

            im.putpixel((x + S[0], y + S[1]), color)
            im.putpixel((y + S[0], x + S[1]), color)
            im.putpixel((y + S[0], -x + S[1]), color)
            im.putpixel((x + S[0], -y + S[1]), color)
            im.putpixel((-x + S[0], -y + S[1]), color)
            im.putpixel((-y + S[0], -x + S[1]), color)
            im.putpixel((-y + S[0], x + S[1]), color)
            im.putpixel((-x + S[0], y + S[1]), color)

def thick_line(im, A, B, thickness, color):
  pixels = linePixels(A, B)
  for X in pixels:
    filled_circle(im, X, int(thickness)/2, color)

def grayscale(im):
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = im.getpixel((x, y))
            gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
            im.putpixel((x, y), (gray, gray, gray))
    return im

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

def generate_image_from_ves():
    obr = None
    with open("ves_code.txt", 'r') as f:
        for line in f:
            line = line.strip()
            parts = line.split()

            if parts[0] == "VES":
                width = int(parts[2])
                height = int(parts[3])
                color = parts[4]
                rgb_color = hexColor(color)
                obr = platno(width, height, rgb_color)

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
                circle(obr, S, r, farba, thickness)

            if parts[0] == "GREYSCALE":
                obr = grayscale(obr)

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
                thick_line(obr, (int(parts[1]), int(parts[2])), (int(parts[3]), int(parts[4])), thickness, color)
                thick_line(obr, (int(parts[1]), int(parts[2])), (int(parts[5]), int(parts[6])), thickness, color)
                thick_line(obr, (int(parts[3]), int(parts[4])), (int(parts[5]), int(parts[6])), thickness, color)

    img_io = io.BytesIO()
    obr.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return img_base64

