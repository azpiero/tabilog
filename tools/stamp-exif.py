#!/usr/bin/env python3
"""local-data/ の写真に、辻褄の合う旅程の EXIF（撮影日時＋GPS）を焼き込む。

ファイル名を昇順に並べて下の ROUTE に順番どおり割り当てるだけ。
写真を入れ替えたら再実行する。元ファイルは上書きされる（テストデータ前提）。
"""
import sys
from pathlib import Path
from PIL import Image

# 東京 → 箱根 → 富士 → 東京 の1泊2日。時刻は日本時間
ROUTE = [
    ('2026:09:23 09:10:00', 35.6812, 139.7671, '東京駅'),
    ('2026:09:23 11:30:00', 35.2510, 139.1535, '小田原城'),
    ('2026:09:23 13:00:00', 35.2325, 139.1057, '箱根湯本'),
    ('2026:09:23 15:40:00', 35.2440, 139.0200, '大涌谷'),
    ('2026:09:23 18:20:00', 35.1900, 139.0240, '芦ノ湖・箱根町港'),
    ('2026:09:24 08:45:00', 35.3083, 138.9350, '御殿場'),
    ('2026:09:24 11:20:00', 35.3931, 138.7339, '富士山五合目'),
    ('2026:09:24 14:10:00', 35.5170, 138.7550, '河口湖'),
    ('2026:09:24 17:30:00', 35.6896, 139.7006, '新宿'),
]

def dms(v):
    v = abs(v); d = int(v); m = int((v - d) * 60)
    return (float(d), float(m), round((v - d - m / 60) * 3600, 4))

def stamp(path: Path, when: str, lat: float, lng: float):
    im = Image.open(path)
    ex = im.getexif()
    ex[0x0132] = when                                    # DateTime
    ex.get_ifd(0x8769).update({0x9003: when, 0x9004: when, 0x9011: '+09:00'})
    ex.get_ifd(0x8825).update({                          # GPS
        0: b'\x02\x03\x00\x00',
        1: 'N' if lat >= 0 else 'S', 2: dms(lat),
        3: 'E' if lng >= 0 else 'W', 4: dms(lng),
        5: b'\x00', 6: 0.0,
        29: when[:10].replace(':', ':'),
    })
    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')
    out = path if path.suffix.lower() in ('.jpg', '.jpeg', '.webp') else path.with_suffix('.jpg')
    im.save(out, exif=ex.tobytes(), quality=92)
    return out

def read_back(path: Path):
    ex = Image.open(path).getexif()
    gps = ex.get_ifd(0x8825)
    deg = lambda t: float(t[0]) + float(t[1]) / 60 + float(t[2]) / 3600
    return ex.get_ifd(0x8769).get(0x9003), deg(gps[2]), deg(gps[4])

def main(folder='local-data'):
    files = sorted(p for p in Path(folder).iterdir()
                   if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.heic'))
    if len(files) > len(ROUTE):
        sys.exit(f'写真{len(files)}枚に対しROUTEが{len(ROUTE)}地点しかない。ROUTEを足して。')

    for path, (when, lat, lng, place) in zip(files, ROUTE):
        out = stamp(path, when, lat, lng)
        got_when, got_lat, got_lng = read_back(out)
        assert got_when == when and abs(got_lat - lat) < 1e-4 and abs(got_lng - lng) < 1e-4, f'書き込み失敗: {out}'
        print(f'{when}  {lat:8.4f},{lng:9.4f}  {place:16s} <- {out.name}')

if __name__ == '__main__':
    main(*sys.argv[1:])
