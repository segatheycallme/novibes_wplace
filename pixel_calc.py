import urllib.request
from PIL import Image

color_lookup = {
    # basic
    (0, 0, 0, 0): 0,
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
    (40, 80, 158, 255): 18,
    (64, 147, 228, 255): 19,
    (96, 247, 242, 255): 20,
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
    # extra
    (170, 170, 170, 255): 32,
    (165, 14, 30, 255): 33,
    (250, 128, 114, 255): 34,
    (228, 92, 26, 255): 35,
    (214, 181, 148, 255): 36,
    (156, 132, 49, 255): 37,
    (197, 173, 49, 255): 38,
    (232, 212, 95, 255): 39,
    (74, 107, 58, 255): 40,
    (90, 148, 74, 255): 41,
    (132, 197, 115, 255): 42,
    (15, 121, 159, 255): 43,
    (187, 250, 242, 255): 44,
    (125, 199, 255, 255): 45,
    (77, 49, 184, 255): 46,
    (74, 66, 132, 255): 47,
    (122, 113, 196, 255): 48,
    (181, 174, 241, 255): 49,
    (219, 164, 99, 255): 50,
    (209, 128, 81, 255): 51,
    (255, 197, 165, 255): 52,
    (155, 82, 73, 255): 53,
    (209, 128, 120, 255): 54,
    (250, 182, 164, 255): 55,
    (123, 99, 82, 255): 56,
    (156, 132, 107, 255): 57,
    (51, 57, 65, 255): 58,
    (109, 117, 141, 255): 59,
    (179, 185, 209, 255): 60,
    (109, 100, 63, 255): 61,
    (148, 140, 107, 255): 62,
    (205, 197, 158, 255): 63,
}


def get_pixels(pixels_num: int, colors_bitmap: int, todo_pixels, skip_transparent=True):
    colors = []
    coords = []
    for tx in todo_pixels.keys():
        for ty in todo_pixels[tx].keys():
            for x in range(1000):
                for y in range(1000):
                    color = todo_pixels[tx][ty][x][y]
                    if color == 64:
                        continue
                    if skip_transparent and color == 0:
                        continue
                    if color > 31 and not (colors_bitmap & (1 << (color - 32))):
                        # premium color not avalaible
                        continue
                    if len(colors) >= pixels_num:
                        break

                    coords.append(x)
                    coords.append(y)
                    colors.append(color)
                    todo_pixels[tx][ty][x][y] = 64
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
            new_todo[tx + x][ty + y] = [[64 for _ in range(1000)] for _ in range(1000)]

    x = px + tx * 1000
    y = py + ty * 1000
    for pixel in img_data:
        color = get_color(pixel)
        if color is None:
            color = 64  # impossible color
        new_todo[x // 1000][y // 1000][x % 1000][y % 1000] = color

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

    for tx in todo_pixels.keys():
        for ty in todo_pixels[tx].keys():
            for x in range(1000):
                for y in range(1000):
                    if todo_pixels[tx][ty][x][y] == new_todo[tx][ty][x][y]:
                        todo_pixels[tx][ty][x][y] = 64


def dict_union(a: dict, b: dict):
    final = {}
    for tx in a.keys() | b.keys():
        final[tx] = {}
        if a.get(tx) is None:
            final[tx] = b[tx]
            continue
        if b.get(tx) is None:
            final[tx] = a[tx]
            continue
        for ty in a[tx].keys() | b[tx].keys():
            final[tx][ty] = {}
            if a[tx].get(ty) is None:
                final[tx][ty] = b[tx][ty]
                continue
            if b[tx].get(ty) is None:
                final[tx][ty] = a[tx][ty]
                continue
            final[tx][ty] = tile_union(a[tx][ty], b[tx][ty])

    return final


def tile_union(a: list[list[int]], b: list[list[int]]):
    res = a
    for x in range(1000):
        for y in range(1000):
            if b[x][y] != 64:
                res[x][y] = b[x][y]

    return res


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


# inverse_lookup = {v: k for k, v in color_lookup.items()}
# inverse_lookup[64] = (0, 0, 0, 0)
#
# pixels = generate_pixels("smile.png", 1141, 752, 440, 160)
# update_pixels(pixels)
# print(get_pixels(100, 0, pixels))
# img = Image.new("RGBA", (1000, 1000))
# for x in range(1000):
#     for y in range(1000):
#         img.putpixel((x, y), inverse_lookup[pixels[1141][752][x][y]])
#
# img.save("hi.png")
