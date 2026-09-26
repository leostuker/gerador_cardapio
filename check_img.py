from PIL import Image

img = Image.open('static/output/Cardapio_Integral.png')
rgb_img = img.convert('RGB')
bg_color = (253, 248, 240)  # #fdf8f0

# Grid area is x: 35 to 1045, y: 200 to 1320
found_gap = False
for y in range(200, 1320):
    for x in range(35, 1045):
        if rgb_img.getpixel((x, y)) == bg_color:
            found_gap = True
            print(f"Gap found at {x}, {y}")
            break
    if found_gap:
        break

if not found_gap:
    print("No gaps found!")
