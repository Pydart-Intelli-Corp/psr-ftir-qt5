
from PyQt5.QtCore import (
    Qt, QSize, QPoint, QPointF, QRectF,
    QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup,
    pyqtSlot, pyqtProperty
)
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtGui import QColor, QBrush, QPaintEvent, QPen, QPainter

from Controls.gpio_control import GPIOController

class Toggle(QCheckBox):

    _transparent_pen = QPen(Qt.transparent)
    _light_grey_pen = QPen(Qt.lightGray)

    def __init__(self,
                 parent=None,
                 bar_color=Qt.gray,
                 checked_color="#00B0FF",
                 handle_color=Qt.white):
        super().__init__(parent)
        self.controller = GPIOController()
        # Initialize color properties
        self._bar_brush = QBrush(QColor("green"))  # Set off-state color to green
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())
        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        # Setup the rest of the widget
        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0

        self.stateChanged.connect(self.handle_state_change)

    def sizeHint(self):
        return QSize(58, 45)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e: QPaintEvent):
        contRect = self.contentsRect()
        handleRadius = round(0.24 * contRect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(self._transparent_pen)

        # Draw bar
        barRect = QRectF(0, 0, contRect.width() - handleRadius, 0.40 * contRect.height())
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2
        trailLength = contRect.width() - 2 * handleRadius
        xPos = contRect.x() + handleRadius + trailLength * self._handle_position

        # Check if toggle is checked or unchecked
        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)
        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        # Draw handle
        p.drawEllipse(QPointF(xPos, barRect.center().y()), handleRadius, handleRadius)
        p.end()

    @pyqtSlot(int)
    def handle_state_change(self, value):
        
        
        self._handle_position = 1 if value else 0
        self.update()

    @pyqtProperty(float)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        self._handle_position = pos
        self.update()

    @pyqtProperty(float)
    def pulse_radius(self):
        return self._pulse_radius

    @pulse_radius.setter
    def pulse_radius(self, pos):
        self._pulse_radius = pos
        self.update()

class AnimatedToggle(Toggle):

    def __init__(self, *args,
                 pulse_unchecked_color="#44999999",
                 pulse_checked_color="#FFFFFFEE", **kwargs):
        super().__init__(*args, **kwargs)

        self._pulse_radius = 0

        # Animation setup
        self.animation = QPropertyAnimation(self, b"handle_position", self)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(200)

        self.pulse_anim = QPropertyAnimation(self, b"pulse_radius", self)
        self.pulse_anim.setDuration(350)
        self.pulse_anim.setStartValue(10)
        self.pulse_anim.setEndValue(20)

        self.animations_group = QSequentialAnimationGroup()
        self.animations_group.addAnimation(self.animation)
        self.animations_group.addAnimation(self.pulse_anim)

        self._pulse_unchecked_animation = QBrush(QColor(pulse_unchecked_color))
        self._pulse_checked_animation = QBrush(QColor(pulse_checked_color))

    @pyqtSlot(int)
    def handle_state_change(self, value):
        self.animations_group.stop()
        self.animation.setEndValue(1 if value else 0)
        self.animations_group.start()
        self.controller.start_wave(frequency=650, duration=0.03)

    def paintEvent(self, e: QPaintEvent):
        contRect = self.contentsRect()
        handleRadius = round(0.24 * contRect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(self._transparent_pen)

        barRect = QRectF(0, 0, contRect.width() - handleRadius, 0.40 * contRect.height())
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2
        trailLength = contRect.width() - 2 * handleRadius
        xPos = contRect.x() + handleRadius + trailLength * self._handle_position

        # Pulse effect
        if self.pulse_anim.state() == QPropertyAnimation.Running:
            p.setBrush(self._pulse_checked_animation if self.isChecked() else self._pulse_unchecked_animation)
            p.drawEllipse(QPointF(xPos, barRect.center().y()), self._pulse_radius, self._pulse_radius)

        # Draw bar and handle
        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)
        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        p.drawEllipse(QPointF(xPos, barRect.center().y()), handleRadius, handleRadius)
        p.end()
