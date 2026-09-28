from PIL import Image, ImageColor
from image_generator import WIDTH, HEIGHT, HEADER_H, COLOR_BG

img = Image.open('static/output/Cardapio_Integral.png').convert('RGB')
bg = ImageColor.getrgb(COLOR_BG)

# A grade ocupa toda a largura, de HEADER_H até o fim da imagem
grid = img.crop((0, HEADER_H, WIDTH, HEIGHT))
colors = dict((c, n) for n, c in grid.getcolors(maxcolors=1_000_000))

if bg in colors:
    print(f"Gap found! {colors[bg]} pixels with background color inside the grid")
else:
    print("No gaps found!")
