from PIL import Image, ImageDraw, ImageFont
import io
import struct

def byte_combiner():
    last = None
    while True:
        p1 = ((yield last) & 0x03) << 6
        p2 = ((yield) & 0x03) << 4
        p3 = ((yield) & 0x03) << 2
        p4 = ((yield) & 0x03)
        last = (p1 | p2 | p3 | p4)

def convert_for_output(im):
    out = []

    while len(im) % 4 != 0:
        im.append(0)

    for chunk in chunks(im, 4):
        b = 0
        for p in chunk:
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

def create_sprite(digit):
    base_image = Image.open("./talking_heads.png")
    segment_width = int(base_image.width / 4)
    segment_height = int(base_image.height / 4)
    print(f"{segment_width}, {segment_height}")

    image = Image.new("P", (segment_width, segment_height))
    image.palette = base_image.palette

    x = digit % 4
    y = int(digit / 4)

    image = base_image.crop((x * segment_width, y * segment_height, (x+1) * segment_width, (y+1) * segment_height))

    # image.paste(region, (0, 0, segment_width, segment_height))
    image.save(f"./tile{digit}.png")
    img_byte_arr = []
    for y in range(0, image.height):
        for x in range(0, image.width):
            img_byte_arr.append(image.getpixel((x, y)))
        for x in range(0, image.width % 4):
            img_byte_arr.append(0)
    img_byte_arr_conv = convert_for_output(img_byte_arr)
    return f"tile{digit+1}_bits", img_byte_arr_conv

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def create_header_file(imgs):
    with open("./tiles.rs", "w") as f:
        for (array_name, img_arr) in imgs:
            f.write(f"pub const {array_name}: [u8; {len(img_arr)}] = [\n")
            strs = []
            for chunk in chunks(img_arr, 16):
                strs.append(",".join(["0x{:02X}".format(x) for x in chunk]) + ",")
            strs[-1] = strs[-1][:-1]
            for str in strs:
                f.write(str + "\n")
            f.write("]; \n")

if __name__ == '__main__':
    create_header_file([create_sprite(x) for x in range(0, 16)])
