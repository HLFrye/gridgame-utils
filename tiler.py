from PIL import Image
import os.path
from functools import partial

def byte_combiner():
    last = None
    while True:
        p1 = ((yield last) & 0x03) << 6
        p2 = ((yield) & 0x03) << 4
        p3 = ((yield) & 0x03) << 2
        p4 = ((yield) & 0x03)
        last = (p1 | p2 | p3 | p4)

def convert_for_output(im, reorderer):
    out = []

    # while len(im) % 4 != 0:
    #     im.append(0)

    for chunk in chunks(im, 4):
        b = 0
        for p in chunk:
            p = reorderer(p)
            b = (b<<2) | (p & 0x03)
        out.append(b)

    # combiner = byte_combiner()
    # combiner.send(None)

    # for b in im:
    #     res = combiner.send(b)
    #     if res is not None:
    #         out.append(res)

    # extra = (len(im) % 4) + 1
    # for _ in range(0, extra):
    #     res = combiner.send(0)
    #     if res is not None:
    #         out.append(res)

    return out

def convert_palette(palette_bytes): 
    return [
        (palette_bytes[0] << 16 ) | (palette_bytes[1] << 8) | palette_bytes[2],
        (palette_bytes[3] << 16 ) | (palette_bytes[4] << 8) | palette_bytes[5],
        (palette_bytes[6] << 16 ) | (palette_bytes[7] << 8) | palette_bytes[8],
        (palette_bytes[9] << 16 ) | (palette_bytes[10] << 8) | palette_bytes[11],
    ]

def reorder(palette):
    brightest = palette.index(max(palette))
    darkest = palette.index(min(palette))
    palette_copy = [palette[i] for i in range(len(palette)) if i != brightest and i != darkest]
    others = [palette.index(color) for color in palette_copy]

    pal_map = [brightest, darkest, *others]

    new_palette = [palette[x] for x in pal_map]

    reverse_map = [new_palette.index(x) for x in palette]

    def renderlogger(renderer, input):
        output = renderer(input)
        return output

    def reorderer(input):
        return reverse_map[input]

    return new_palette, partial(renderlogger,reorderer)


def create_sprites(image_name):
    base_image = Image.open(image_name)
    segment_width = int(base_image.width / 4)
    segment_height = int(base_image.height / 4)
    print(f"{segment_width}, {segment_height}")

    image = Image.new("P", (segment_width, segment_height))
    image.palette = base_image.palette

    palette = None

    output = []

    for digit in range(16):
        x = digit % 4
        y = int(digit / 4)

        image = base_image.crop((x * segment_width, y * segment_height, (x+1) * segment_width, (y+1) * segment_height))

        image.save(f"./tile{digit}.png")
        img_byte_arr = []
        for y in range(0, image.height):
            for x in range(0, image.width):
                img_byte_arr.append(image.getpixel((x, y)))
            for x in range(0, image.width % 4):
                img_byte_arr.append(0)
        palette = convert_palette(base_image.palette.tobytes())

        palette, reordering = reorder(palette)

        img_byte_arr_conv = convert_for_output(img_byte_arr, reordering)

        output.append((f"_TILE{digit+1}", img_byte_arr_conv))

    return palette, output

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def create_header_file(filename):
    with open("./tiles.rs", "w") as f:
        palette, sprites = create_sprites(filename)
        pal_str = ",".join(["0x{:X}".format(x) for x in palette])

        base_name = os.path.basename(filename).split(".")[0]

        f.write(f"pub const {base_name.upper()}_PALETTE: [u32; 4] = [{pal_str}];\n")

        names = []

        for (array_name, img_arr) in sprites:
            array_name = f"{base_name}{array_name}"
            names.append(array_name.upper())
            f.write(f"pub const {array_name.upper()}: [u8; {len(img_arr)}] = [\n")
            strs = []
            for chunk in chunks(img_arr, 16):
                strs.append(",".join(["0x{:02X}".format(x) for x in chunk]) + ",")
            strs[-1] = strs[-1][:-1]
            for str in strs:
                f.write(str + "\n")
            f.write("]; \n")

        f.write(f"pub const {base_name.upper()}: [&[u8]; {len(names)}] = [\n")
        for name in names:
            f.write(f"    &{name},\n")
        f.write("];\n")

if __name__ == '__main__':
    create_header_file("./frye_small_color.png")
