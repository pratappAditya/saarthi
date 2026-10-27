import os
from PIL import Image

def generate_assets():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    src_icon_path = os.path.join(project_root, "frontend", "public", "saarthi-icon.png")
    assets_dir = os.path.join(base_dir, "msix", "Assets")
    os.makedirs(assets_dir, exist_ok=True)

    src_img = Image.open(src_icon_path).convert("RGBA")
    print(f"Loaded source icon: {src_icon_path} ({src_img.size})")

    # 1. Square44x44Logo.png
    sq44 = src_img.resize((44, 44), Image.Resampling.LANCZOS)
    sq44.save(os.path.join(assets_dir, "Square44x44Logo.png"), "PNG")
    print("Created Square44x44Logo.png")

    # 2. Square150x150Logo.png
    sq150 = src_img.resize((150, 150), Image.Resampling.LANCZOS)
    sq150.save(os.path.join(assets_dir, "Square150x150Logo.png"), "PNG")
    print("Created Square150x150Logo.png")

    # 3. StoreLogo.png (50x50)
    store_logo = src_img.resize((50, 50), Image.Resampling.LANCZOS)
    store_logo.save(os.path.join(assets_dir, "StoreLogo.png"), "PNG")
    print("Created StoreLogo.png")

    # 4. Wide310x150Logo.png (310x150 canvas, centered 110x110 icon)
    wide_img = Image.new("RGBA", (310, 150), (10, 13, 20, 255))
    icon_resized = src_img.resize((110, 110), Image.Resampling.LANCZOS)
    offset = ((310 - 110) // 2, (150 - 110) // 2)
    wide_img.paste(icon_resized, offset, icon_resized)
    wide_img.save(os.path.join(assets_dir, "Wide310x150Logo.png"), "PNG")
    print("Created Wide310x150Logo.png")

    # 5. SplashScreen.png (620x300 canvas, centered 160x160 icon)
    splash_img = Image.new("RGBA", (620, 300), (10, 13, 20, 255))
    splash_icon = src_img.resize((160, 160), Image.Resampling.LANCZOS)
    splash_offset = ((620 - 160) // 2, (300 - 160) // 2)
    splash_img.paste(splash_icon, splash_offset, splash_icon)
    splash_img.save(os.path.join(assets_dir, "SplashScreen.png"), "PNG")
    print("Created SplashScreen.png")

if __name__ == "__main__":
    generate_assets()
