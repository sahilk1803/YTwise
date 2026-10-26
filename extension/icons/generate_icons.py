import struct
import zlib
import os

def create_png(width, height, color=(37, 99, 235), border_color=(255, 255, 255)):
    """Generates a raw PNG with a rounded glowing smart icon."""
    raw_data = bytearray()
    
    for y in range(height):
        raw_data.append(0)  # Filter type None
        for x in range(width):
            # Normalized coordinates
            nx = (x - width / 2) / (width / 2)
            ny = (y - height / 2) / (height / 2)
            dist = nx * nx + ny * ny
            
            # Draw rounded badge
            if dist <= 0.75:
                # Play triangle or brain spark center
                is_inner_symbol = False
                # Play triangle shape in center
                cx = (x - width * 0.42) / (width * 0.28)
                cy = (y - height * 0.5) / (height * 0.28)
                if -0.6 <= cx <= 0.6 and abs(cy) <= (0.6 - cx * 0.5) * 1.0 and cx > -0.5:
                    is_inner_symbol = True
                
                if is_inner_symbol:
                    r, g, b, a = 255, 255, 255, 255  # White symbol
                else:
                    # Gradient background: Violet/Blue to Emerald
                    r = int(79 + (nx + 1) * 30)
                    g = int(70 + (ny + 1) * 40)
                    b = int(229)
                    a = 255
            elif dist <= 0.88:
                # Border glow
                r, g, b, a = 129, 140, 248, int(255 * (0.88 - dist) / 0.13)
            else:
                r, g, b, a = 0, 0, 0, 0  # Transparent
                
            raw_data.extend([r, g, b, a])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw_data)))
    png += chunk(b'IEND', b'')
    return png

icons_dir = r"C:\Users\dell7\.gemini\antigravity\scratch\youtubewise\extension\icons"
os.makedirs(icons_dir, exist_ok=True)

for size in [16, 48, 128]:
    path = os.path.join(icons_dir, f"icon-{size}.png")
    with open(path, "wb") as f:
        f.write(create_png(size, size))
    print(f"Created {path} ({size}x{size})")
