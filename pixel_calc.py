import urllib.request
from PIL import Image

color_lookup = {
    # trans
    (0, 0, 0, 0): 0,
    (255, 255, 255, 0): 0,
    # free
    (0, 0, 0, 255): 1,
    (60, 60, 60, 255): 2,
    (120, 120, 120, 255): 3,
    (210, 210, 210, 255): 4,
    (255, 255, 255, 255): 5,
    (96, 0, 24, 255): 6,
    (237, 28, 36, 255): 7,
    (255, 127, 39, 255): 8,
    (246, 170, 9, 255): 9,
    (249, 221, 59, 255): 10,
    (255, 250, 188, 255): 11,
    (14, 185, 104, 255): 12,
    (19, 230, 123, 255): 13,
    (135, 255, 94, 255): 14,
    (12, 129, 110, 255): 15,
    (16, 174, 166, 255): 16,
    (19, 225, 190, 255): 17,
    (96, 247, 242, 255): 18,
    (40, 80, 158, 255): 19,
    (64, 147, 228, 255): 20,
    (107, 80, 246, 255): 21,
    (153, 177, 251, 255): 22,
    (120, 12, 153, 255): 23,
    (170, 56, 185, 255): 24,
    (224, 159, 249, 255): 25,
    (203, 0, 122, 255): 26,
    (236, 31, 128, 255): 27,
    (243, 141, 169, 255): 28,
    (104, 70, 52, 255): 29,
    (149, 104, 42, 255): 30,
    (248, 178, 119, 255): 31,
    # paid
    (170, 170, 170, 255): 32,
    (165, 14, 30, 255): 33,
    (250, 128, 114, 255): 34,
    (228, 92, 26, 255): 35,
    (156, 132, 49, 255): 36,
    (197, 173, 49, 255): 37,
    (232, 212, 95, 255): 38,
    (74, 107, 58, 255): 39,
    (90, 148, 74, 255): 40,
    (132, 197, 115, 255): 41,
    (15, 121, 159, 255): 42,
    (187, 250, 242, 255): 43,
    (125, 199, 255, 255): 44,
    (77, 49, 184, 255): 45,
    (74, 66, 132, 255): 46,
    (122, 113, 196, 255): 47,
    (181, 174, 241, 255): 48,
    (155, 82, 73, 255): 49,
    (209, 128, 120, 255): 50,
    (250, 182, 164, 255): 51,
    (219, 164, 99, 255): 52,
    (123, 99, 82, 255): 53,
    (156, 132, 107, 255): 54,
    (214, 181, 148, 255): 55,
    (209, 128, 81, 255): 56,
    (255, 197, 165, 255): 57,
    (109, 100, 63, 255): 58,
    (148, 140, 107, 255): 59,
    (205, 197, 158, 255): 60,
    (51, 57, 65, 255): 61,
    (109, 117, 141, 255): 62,
    (179, 185, 209, 255): 63,
}


def get_pixels(pixels_num: int, colors_bitmap: int, todo_pixels, skip_transparent=True):
    colors = []
    coords = []
    for tx in todo_pixels.keys():
        for ty in todo_pixels[tx].keys():
            for color in todo_pixels[tx][ty].keys():
                if skip_transparent and color == 0:
                    continue
                if color == 64:
                    continue  # unavalaible color
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
        color = get_color(pixel)
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


def dict_union(a: dict, b: dict):
    final = {}
    for x in a.keys() | b.keys():
        final[x] = {}
        if a.get(x) is None:
            final[x] = b[x]
            continue
        if b.get(x) is None:
            final[x] = a[x]
            continue
        for y in a[x].keys() | b[x].keys():
            final[x][y] = {}
            if a[x].get(y) is None:
                final[x][y] = b[x][y]
                continue
            if b[x].get(y) is None:
                final[x][y] = a[x][y]
                continue
            for color in a[x][y].keys() | b[x][y].keys():
                final[x][y][color] = a[x][y][color] | b[x][y][color]

    return final


def get_color(color: tuple[int, int, int, int]) -> int | None:
    if color_lookup.get(color) is not None:
        return color_lookup[color]
    if color[3] != 255:
        return 0

    closest = None
    diff = 255**2 * 3
    for predefined_color in color_lookup.keys():
        if predefined_color[3] != 255:
            continue
        new_diff = (
            (predefined_color[0] - color[0]) ** 2
            + (predefined_color[1] - color[1]) ** 2
            + (predefined_color[2] - color[2]) ** 2
        )
        if new_diff < diff:
            diff = new_diff
            closest = color_lookup[predefined_color]

    return closest
