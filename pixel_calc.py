from PIL import Image

color_lookup = {
    (0, 0, 0, 0): 0,
    (255, 255, 255, 0): 0,
    (0, 0, 0, 255): 1,
    (255, 255, 255, 255): 5,
}


# TODO: color_bitmap
def get_pixels(pixels_num: int, colors_bitmap: int, todo_pixels, skip_transparent=True):
    colors = []
    coords = []
    for tx in todo_pixels.keys():
        for ty in todo_pixels[tx].keys():
            for color in todo_pixels[tx][ty].keys():
                if skip_transparent and color == 0:
                    continue
                while len(colors) < pixels_num and len(todo_pixels[tx][ty][color]) > 0:
                    pixel = todo_pixels[tx][ty][color].pop()
                    coords.append(pixel[0])
                    coords.append(pixel[1])
                    colors.append(color)
            if len(colors) > 0:
                return {"colors": colors, "coords": coords, "tx": tx, "ty": ty}

    print(todo_pixels)
    # :(
    return {"colors": [], "coords": [], "tx": 0, "ty": 0}


def generate_pixels(png_path: str, tx: int, ty: int, px: int, py: int):
    new_todo = {}

    img = Image.open(png_path)
    w = img.width
    h = img.height
    img_data = list(img.getdata())

    for x in range((w + px) // 1000 + 1):
        new_todo[tx + x] = {}
        for y in range((h + py) // 1000 + 1):
            # bloat
            new_todo[tx + x][ty + y] = {i: set() for i in range(64)}

    x = px + tx * 1000
    y = py + ty * 1000
    for pixel in img_data:
        new_todo[x // 1000][y // 1000][color_lookup[pixel]].add((x % 1000, y % 1000))

        x += 1
        if x >= w + px + tx * 1000:
            x -= w
            y += 1

    print(new_todo)
    return new_todo
