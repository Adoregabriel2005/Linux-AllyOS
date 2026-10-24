"""Ícones originais: tinta escura, pigmentos suaves e detalhes de papel."""
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QImageReader
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=64)
def illustrated_icon(kind):
    if kind == 'wine':
        painted = Path(__file__).parent / 'assets/icons/wine-hand.png'
        if painted.is_file():
            reader = QImageReader(str(painted))
            reader.setScaledSize(QSize(192, 192))
            artwork = reader.read()
            if not artwork.isNull():
                return QIcon(QPixmap.fromImage(artwork))
    disconnected = kind.endswith('-off')
    kind = kind.removesuffix('-off')
    pix = QPixmap(128, 128)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(2, 2)
    ink = QColor('#25272e')
    p.setPen(QPen(ink, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.MiterJoin))

    def poly(points, fill):
        p.setBrush(QColor(fill))
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))

    if kind in ('volume', 'network', 'wifi', 'usb', 'disk', 'language', 'capture'):
        p.setBrush(QColor('#e6d9bd'))
        p.drawRect(6, 9, 51, 45)
        p.setPen(QPen(ink, 3))
        if kind == 'volume':
            poly([(13, 25), (22, 25), (32, 17), (32, 46), (22, 38), (13, 38)], '#c48fa0')
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(31, 18, 17, 28, -70 * 16, 140 * 16)
        elif kind in ('network', 'wifi'):
            if kind == 'wifi':
                p.setBrush(Qt.BrushStyle.NoBrush)
                for offset in (0, 10, 20):
                    p.drawArc(11 + offset // 2, 16 + offset // 2, 42 - offset, 35 - offset, 35 * 16, 110 * 16)
                p.drawPoint(32, 43)
            else:
                p.setBrush(QColor('#8bafa4'))
                p.drawRect(20, 17, 23, 19)
                p.drawLine(31, 36, 31, 45)
                p.drawLine(16, 45, 48, 45)
        elif kind == 'usb':
            p.drawLine(31, 44, 31, 17)
            p.drawLine(31, 35, 19, 26)
            p.drawLine(31, 30, 43, 22)
            poly([(26, 18), (31, 12), (36, 18)], '#8bafa4')
            p.drawRect(40, 17, 6, 6)
            p.drawEllipse(15, 20, 7, 7)
        elif kind == 'disk':
            p.setBrush(QColor('#8bafa4'))
            p.drawRect(15, 16, 34, 30)
            p.setBrush(QColor('#d3b679'))
            p.drawEllipse(22, 20, 19, 19)
            p.drawLine(32, 29, 44, 41)
            p.drawPoint(20, 42)
        elif kind == 'capture':
            p.drawRect(15, 21, 35, 23)
            p.drawRect(23, 16, 17, 5)
            p.setBrush(QColor('#8bafa4'))
            p.drawEllipse(26, 24, 14, 14)
        else:
            p.setPen(QPen(QColor('#946072'), 3))
            p.drawLine(19, 41, 29, 19)
            p.drawLine(29, 19, 39, 41)
            p.drawLine(23, 33, 35, 33)
            p.setPen(QPen(ink, 2))
            p.drawLine(40, 22, 49, 22)
            p.drawLine(44, 18, 44, 36)
    elif kind == 'files':
        poly([(13, 12), (38, 7), (51, 17), (49, 49), (19, 56), (10, 45)], '#759b8c')
        poly([(14, 10), (37, 6), (48, 16), (44, 48), (14, 53)], '#eee4c7')
        poly([(37, 6), (36, 18), (48, 16)], '#cfbaa0')
        p.setPen(QPen(QColor('#bca784'), 1))
        for y in (24, 30, 36, 42):
            p.drawLine(19, y, 37, y - 3)
        path = QPainterPath(QPointF(36, 21))
        path.lineTo(24, 38)
        path.cubicTo(19, 47, 31, 52, 36, 43)
        path.lineTo(48, 24)
        path.cubicTo(56, 11, 42, 3, 34, 15)
        path.lineTo(22, 33)
        p.setPen(QPen(ink, 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPath(path)
        p.setPen(QPen(QColor('#d9a4b0'), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPath(path)
        p.setPen(QPen(QColor('#fff0de'), 1))
        p.drawLine(35, 17, 25, 32)
    elif kind == 'editor':
        poly([(13, 8), (41, 8), (53, 20), (53, 55), (13, 55)], '#8eafa4')
        poly([(9, 5), (37, 5), (48, 17), (48, 52), (9, 52)], '#f2e6ce')
        poly([(37, 5), (37, 18), (48, 17)], '#d5baa5')
        p.setPen(QPen(QColor('#879d9e'), 1.2))
        for y in (23, 29, 35, 41):
            p.drawLine(16, y, 37, y)
        p.setPen(QPen(ink, 2.2))
        poly([(29, 48), (32, 37), (51, 13), (58, 19), (39, 43)], '#d9a052')
        poly([(29, 48), (32, 37), (39, 43)], '#ead7b9')
        poly([(29, 48), (31, 42), (34, 45)], '#34313a')
        poly([(49, 16), (53, 11), (60, 17), (56, 22)], '#ce8f9e')
        p.setPen(QPen(QColor('#f8df8e'), 1.5))
        p.drawLine(36, 36, 50, 19)
    elif kind == 'terminal':
        poly([(7, 15), (55, 15), (58, 50), (11, 54)], '#8bafa4')
        poly([(5, 10), (54, 10), (54, 48), (5, 48)], '#e0d5ba')
        poly([(10, 19), (49, 19), (49, 41), (10, 41)], '#303b42')
        p.setPen(QPen(QColor('#a9d2b6'), 3))
        p.drawLine(16, 25, 22, 30)
        p.drawLine(22, 30, 16, 35)
        p.drawLine(28, 35, 40, 35)
        p.setPen(QPen(QColor('#bc8393'), 2))
        p.drawLine(43, 14, 49, 14)
        p.setPen(QPen(ink, 2))
        p.drawLine(15, 56, 48, 56)
    elif kind == 'web':
        p.setBrush(QColor('#8ab0b5'))
        p.drawEllipse(9, 7, 46, 46)
        poly([(19, 12), (32, 9), (39, 17), (31, 22), (32, 29), (21, 28), (15, 20)], '#b6c28e')
        poly([(38, 29), (48, 26), (51, 37), (43, 47), (35, 40)], '#b6c28e')
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor('#e5d6bd'), 3))
        p.drawArc(4, 3, 55, 56, 205 * 16, 210 * 16)
        p.setPen(QPen(ink, 2))
        p.drawLine(30, 54, 30, 59)
        p.drawLine(18, 59, 44, 59)
    elif kind == 'jewel':
        poly([(32, 5), (39, 22), (57, 28), (42, 36), (40, 55), (32, 45), (23, 56), (22, 37), (7, 28), (25, 22)], '#c6a05b')
        poly([(32, 15), (43, 29), (32, 44), (21, 29)], '#729f91')
        poly([(32, 15), (33, 29), (21, 29)], '#c2d7bf')
        p.setPen(QPen(QColor('#f4e2ad'), 1.2))
        p.drawLine(32, 16, 33, 39)
        p.drawEllipse(29, 7, 5, 5)
    elif kind == 'wine':
        # Tinta e pigmentos do conjunto: mão delicada com unhas vermelhas.
        glass = QPainterPath(QPointF(24, 7))
        glass.lineTo(47, 7)
        glass.cubicTo(50, 23, 46, 31, 36, 32)
        glass.cubicTo(24, 31, 21, 23, 24, 7)
        p.setBrush(QColor('#dce4db'))
        p.drawPath(glass)
        wine = QPainterPath(QPointF(24, 18))
        wine.lineTo(47, 18)
        wine.cubicTo(47, 34, 26, 35, 24, 18)
        p.fillPath(wine, QColor('#8b354e'))
        p.drawLine(36, 32, 36, 50)
        p.setBrush(QColor('#dce4db'))
        p.drawEllipse(27, 49, 20, 5)
        hand = QPainterPath(QPointF(7, 57))
        hand.lineTo(15, 39)
        hand.cubicTo(17, 33, 25, 27, 29, 29)
        hand.cubicTo(33, 31, 26, 35, 24, 37)
        hand.lineTo(36, 34)
        hand.cubicTo(43, 32, 44, 37, 38, 39)
        hand.lineTo(28, 43)
        hand.cubicTo(23, 46, 23, 53, 20, 60)
        hand.closeSubpath()
        p.setBrush(QColor('#e6bfa3'))
        p.drawPath(hand)
        p.setPen(QPen(QColor('#9c293c'), 2.4))
        p.drawLine(27, 30, 30, 30)
        p.drawLine(38, 35, 41, 35)
        p.setPen(QPen(QColor('#fff0d8'), 1))
        p.drawLine(27, 10, 27, 16)
    elif kind == 'settings':
        poly([(8, 8), (52, 8), (52, 54), (8, 54)], '#d8ceba')
        for x, y, pigment in [(18, 23, '#bc8b9c'), (30, 37, '#85ada0'), (42, 20, '#d6b46a')]:
            p.setPen(QPen(ink, 2))
            p.drawLine(x, 15, x, 47)
            p.setBrush(QColor(pigment))
            p.drawRect(x - 4, y - 4, 8, 8)
    else:
        # Pequenos volumes de uma biblioteca desenhada, em vez de grade genérica.
        for points, fill in [([(7, 10), (20, 7), (24, 49), (10, 52)], '#c590a2'),
                             ([(24, 8), (37, 8), (37, 51), (24, 51)], '#97b3a0'),
                             ([(39, 13), (51, 9), (59, 49), (46, 53)], '#d9b365')]:
            p.setPen(QPen(ink, 2.2))
            poly(points, fill)
        p.setPen(QPen(QColor('#f3e5cc'), 2))
        p.drawLine(12, 18, 19, 17)
        p.drawLine(28, 17, 33, 17)
        p.drawLine(44, 21, 51, 19)
        p.setPen(QPen(ink, 2))
        p.drawLine(6, 56, 60, 56)
    if disconnected:
        p.setPen(QPen(QColor('#ac5968'), 4))
        p.drawLine(10, 54, 54, 10)
    p.end()
    return QIcon(pix)
