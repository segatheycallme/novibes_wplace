import urllib.request
from PIL import Image

color_lookup = {
    (0, 0, 0, 0): 0,
    (255, 255, 255, 0): 0,
    (0, 0, 0, 255): 1,
    (255, 255, 255, 255): 5,
}


def get_pixels(pixels_num: int, colors_bitmap: int, todo_pixels, skip_transparent=True):
    colors = []
    coords = []
    for tx in todo_pixels.keys():
        for ty in todo_pixels[tx].keys():
            for color in todo_pixels[tx][ty].keys():
                if skip_transparent and color == 0:
                    continue
                if color > 31:
                    # TODO: premium colors
                    continue
                while len(colors) < pixels_num and len(todo_pixels[tx][ty][color]) > 0:
                    pixel = todo_pixels[tx][ty][color].pop()
                    coords.append(pixel[0])
                    coords.append(pixel[1])
                    colors.append(color)
            if len(colors) > 0:
                return {"colors": colors, "coords": coords, "tx": tx, "ty": ty}

    # :(
    return {"colors": [], "coords": [], "tx": 0, "ty": 0}


def generate_pixels(png_path: str, tx: int, ty: int, px: int, py: int):
    new_todo = {}

    img = Image.open(png_path).convert("RGBA")
    w = img.width
    h = img.height
    img_data: list[tuple[int, int, int, int]] = list(img.getdata())

    for x in range((w - 1 + px) // 1000 + 1):
        new_todo[tx + x] = {}
        for y in range((h - 1 + py) // 1000 + 1):
            # bloat
            new_todo[tx + x][ty + y] = {i: set() for i in range(65)}

    x = px + tx * 1000
    y = py + ty * 1000
    for pixel in img_data:
        color = color_lookup.get(pixel)
        if color is None:
            color = 64  # impossible color
        new_todo[x // 1000][y // 1000][color].add((x % 1000, y % 1000))

        x += 1
        if x >= w + px + tx * 1000:
            x -= w
            y += 1

    return new_todo


def update_pixels(todo_pixels):
    new_todo = {}
    for tx in todo_pixels.keys():
        for ty in todo_pixels[tx].keys():
            print(tx, ty)
            urllib.request.urlretrieve(
                f"https://backend.wplace.live/files/s0/tiles/{tx}/{ty}.png",
                f"data/{tx}_{ty}.png",
            )
            gen = generate_pixels(f"data/{tx}_{ty}.png", tx, ty, 0, 0)
            if new_todo.get(tx) is None:
                new_todo[tx] = {}
            new_todo[tx][ty] = gen[tx][ty]

    for x in todo_pixels.keys():
        for y in todo_pixels[x].keys():
            for color in todo_pixels[x][y].keys():
                todo_pixels[x][y][color] -= new_todo[x][y][color]


# todo_pixels = generate_pixels("smile.png", 1141, 751, 995, 995)
# todo_pixels = generate_pixels("smile.png", 1141, 751, 440, 570)
# update_pixels(todo_pixels)
# print(todo_pixels)
# print(get_pixels(100, 0, todo_pixels))
