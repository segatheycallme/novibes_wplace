todo_pixels = {
    1141: {
        751: {
            1: {
                (420, 620),
                (421, 620),
                (420, 621),
                (421, 621),
                (421, 622),
                (422, 621),
            },
        },
    }
}


def get_pixels(pixels_num: int, colors_bitmap: int, todo_pixels=todo_pixels):
    colors = []
    coords = []
    for tx in todo_pixels.keys():
        for ty in todo_pixels[tx].keys():
            for color in todo_pixels[tx][ty].keys():
                while len(colors) < pixels_num and len(todo_pixels[tx][ty][color]) > 0:
                    pixel = todo_pixels[tx][ty][color].pop()
                    coords.append(pixel[0])
                    coords.append(pixel[1])
                    colors.append(color)
            if len(colors) > 0:
                return {"colors": colors, "coords": coords, "tx": tx, "ty": ty}

    # :(
    return {"colors": [], "coords": [], "tx": 0, "ty": 0}
