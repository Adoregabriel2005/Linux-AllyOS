"""Verifica coleção completa e seleção automática por formato de monitor."""
from PySide6.QtGui import QImageReader
from wallpapers import bundled_wallpapers, wallpaper_variant

files = bundled_wallpapers()
assert len(files) == 8
for source in files:
    for width, height, folder in [(1280, 1024, '5x4'), (1920, 1080, '16x9'), (1024, 768, '4x3')]:
        variant = wallpaper_variant(str(source), width, height)
        assert variant.parent.name == folder, variant
        reader = QImageReader(str(variant))
        size = reader.size()
        assert reader.canRead() and size.isValid(), variant
        assert abs(size.width() / size.height() - width / height) < 0.003, variant
assert str(wallpaper_variant('/tmp/user-photo.jpg', 1280, 1024)) == '/tmp/user-photo.jpg'
print('VARIANTS OK: 8 wallpapers x 3 proporcoes, selecao automatica e foto pessoal preservada')
