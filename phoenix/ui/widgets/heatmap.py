from __future__ import annotations

from datetime import date, timedelta

from PyQt6.QtCore import QEasingCurve, QPoint, QRect, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QMouseEvent, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QToolTip, QWidget


class HeatmapWidget(QWidget):
    def __init__(self, completion_map: dict[date, float] | None = None) -> None:
        super().__init__()
        self._completion_map = completion_map or {}
        self._cells: dict[QRect, date] = {}
        self._hover_rect: QRect | None = None
        self._hover_scale = 1.0
        self._hover_anim = QPropertyAnimation(self, b"hoverScale", self)
        self._hover_anim.setDuration(140)
        self._hover_anim.setStartValue(1.0)
        self._hover_anim.setEndValue(1.3)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(243, 156, 18, 130))
        self._shadow.setOffset(0, 0)

        self.setMinimumHeight(170)
        self.setMouseTracking(True)

    def set_completion_map(self, completion_map: dict[date, float]) -> None:
        self._completion_map = completion_map
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._cells.clear()
        size = 12
        gap = 4
        end_date = date.today()
        start_date = end_date - timedelta(days=363)
        current = start_date - timedelta(days=start_date.weekday())

        for week in range(52):
            for weekday in range(7):
                day = current + timedelta(days=week * 7 + weekday)
                rect = QRect(week * (size + gap), weekday * (size + gap), size, size)
                draw_rect = rect
                if self._hover_rect is not None and rect == self._hover_rect:
                    cx = rect.center().x()
                    cy = rect.center().y()
                    half = int((size * self._hover_scale) / 2)
                    draw_rect = QRect(cx - half, cy - half, half * 2, half * 2)
                color = self._color_for_ratio(self._completion_map.get(day, 0.0))
                painter.fillRect(draw_rect, color)
                self._cells[rect] = day

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        point = event.position().toPoint()
        cell_date = self._cell_date(point)
        if cell_date is None:
            if self._hover_rect is not None:
                self._hover_rect = None
                self._hover_anim.stop()
                self._hover_scale = 1.0
                self.update()
            return

        for rect, day in self._cells.items():
            if day == cell_date:
                if rect != self._hover_rect:
                    self._hover_rect = rect
                    self._hover_anim.stop()
                    self._hover_anim.setStartValue(1.0)
                    self._hover_anim.setEndValue(1.3)
                    self._hover_anim.start()
                break

        ratio = self._completion_map.get(cell_date, 0.0)
        QToolTip.showText(
            event.globalPosition().toPoint(),
            f"{cell_date.strftime('%d/%m/%Y')} | {int(ratio * 100)}% concluido",
            self,
        )
        self.update()

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._hover_rect = None
        self._hover_scale = 1.0
        self.update()
        super().leaveEvent(event)

    def _cell_date(self, point: QPoint) -> date | None:
        for rect, cell_date in self._cells.items():
            if rect.contains(point):
                return cell_date
        return None

    def _color_for_ratio(self, ratio: float) -> QColor:
        if ratio <= 0:
            return QColor("#1E1E1E")
        if ratio <= 0.25:
            return QColor(192, 57, 43, 76)
        if ratio <= 0.50:
            return QColor(192, 57, 43, 140)
        if ratio <= 0.75:
            return QColor(230, 126, 34, 179)
        return QColor("#F39C12")

    def _set_hover_scale(self, value: float) -> None:
        self._hover_scale = value
        self.update()

    def _get_hover_scale(self) -> float:
        return self._hover_scale

    hoverScale = pyqtProperty(float, fget=_get_hover_scale, fset=_set_hover_scale)
