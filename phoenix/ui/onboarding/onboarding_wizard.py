from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from phoenix.core.models import Goal, Habit, Transaction


class PhoenixLogoLabel(QLabel):
    """Renderiza o texto Phoenix com gradiente no topo do wizard."""

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor("#C0392B"))
        gradient.setColorAt(1.0, QColor("#F39C12"))
        painter.setPen(QPen(gradient, 1))
        painter.setFont(self.font())
        painter.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), self.text())


class ThinProgressBar(QWidget):
    """Barra de progresso horizontal fina para steps do onboarding."""

    def __init__(self) -> None:
        super().__init__()
        self._value = 1
        self._total = 7
        self.setFixedHeight(4)

    def set_progress(self, value: int, total: int) -> None:
        self._value = max(1, value)
        self._total = max(1, total)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        painter.setBrush(QColor("#1E1E1E"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 2, 2)

        ratio = self._value / self._total
        fill = rect.adjusted(0, 0, -int((1 - ratio) * rect.width()), 0)
        gradient = QLinearGradient(fill.left(), 0, fill.right(), 0)
        gradient.setColorAt(0.0, QColor("#C0392B"))
        gradient.setColorAt(1.0, QColor("#F39C12"))
        painter.setBrush(gradient)
        painter.drawRoundedRect(fill, 2, 2)


class OnboardingWizard(QDialog):
    """Fluxo de onboarding com 7 passos para configuração inicial."""

    _HABIT_OPTIONS = [
        "🏃 Exercício",
        "💧 Água",
        "📚 Leitura",
        "🧘 Meditação",
        "😴 Sono",
        "💊 Suplementos",
        "✍️ Journaling",
        "🎯 Foco",
        "🥗 Alimentação",
    ]

    _FIN_CATEGORIES = [
        "🍔 Alimentação",
        "🚗 Transporte",
        "🏠 Moradia",
        "🎮 Lazer",
        "💪 Saúde",
        "📚 Educação",
        "👗 Compras",
        "💰 Investimentos",
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Onboarding Phoenix")
        self.setModal(True)
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        self._step = 0
        self._steps_total = 7
        self._focus_duration = 25
        self._daily_goal_hours = 2

        self._data: dict[str, object] = {
            "name": "",
            "life_focus": "Equilíbrio geral",
            "habits": [],
            "habit_frequency": 5,
            "goals": [],
            "income_range": "Prefiro não informar",
            "budget_categories": [],
            "focus_duration": 25,
            "daily_goal_hours": 2,
            "peak_time": "Manhã (6h-12h)",
            "load_demo_data": False,
        }

        self.setStyleSheet(
            "QDialog { background: #0D0D0D; }"
            "QFrame#onboarding-card { background: #111111; border: 1px solid #1E1E1E; border-radius: 16px; }"
            "QLabel#step-indicator { color: #555555; font-size: 11px; }"
            "QLabel#step-title { color: #F0F0F0; font-size: 22px; font-weight: 600; }"
            "QLabel#step-subtitle { color: #666666; font-size: 13px; }"
            "QCheckBox#habit-card, QCheckBox#cat-card, QCheckBox#focus-card {"
            "background: #161616; border: 1px solid #2A2A2A; border-radius: 10px; padding: 10px; color: #AAAAAA;"
            "}"
            "QCheckBox#habit-card:hover, QCheckBox#cat-card:hover, QCheckBox#focus-card:hover {"
            "border-color: #E67E22; color: #F0F0F0;"
            "}"
            "QCheckBox#habit-card:checked, QCheckBox#cat-card:checked, QCheckBox#focus-card:checked {"
            "background: rgba(230,126,34,0.12); border-color: #E67E22; color: #F39C12;"
            "}"
        )

        self._build_ui()
        self._update_step_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.addStretch(1)

        card = QFrame()
        card.setObjectName("onboarding-card")
        card.setFixedSize(640, 560)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 22, 28, 22)
        card_layout.setSpacing(10)

        self.logo = PhoenixLogoLabel("Phoenix")
        self.logo.setStyleSheet("font-size: 34px; font-weight: 700;")
        self.logo.setFixedHeight(52)
        card_layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.progress = ThinProgressBar()
        card_layout.addWidget(self.progress)

        self.step_indicator = QLabel()
        self.step_indicator.setObjectName("step-indicator")
        card_layout.addWidget(self.step_indicator)

        self.step_title = QLabel()
        self.step_title.setObjectName("step-title")
        card_layout.addWidget(self.step_title)

        self.step_subtitle = QLabel()
        self.step_subtitle.setObjectName("step-subtitle")
        self.step_subtitle.setWordWrap(True)
        card_layout.addWidget(self.step_subtitle)

        self.stack = QStackedWidget()
        card_layout.addWidget(self.stack, 1)

        nav = QHBoxLayout()
        self.prev_btn = QPushButton("Anterior")
        self.prev_btn.setObjectName("btn-ghost")
        self.next_btn = QPushButton("Próximo")
        self.next_btn.setObjectName("btn-primary")
        nav.addWidget(self.prev_btn)
        nav.addStretch(1)
        nav.addWidget(self.next_btn)
        card_layout.addLayout(nav)

        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addStretch(1)

        self._build_step_pages()
        self._build_logo_pulse()

        self.prev_btn.clicked.connect(self._go_prev)
        self.next_btn.clicked.connect(self._go_next)

    def _build_logo_pulse(self) -> None:
        effect = QGraphicsOpacityEffect(self._welcome_logo)
        self._welcome_logo.setGraphicsEffect(effect)
        self._pulse = QPropertyAnimation(effect, b"opacity", self)
        self._pulse.setDuration(1200)
        self._pulse.setStartValue(0.35)
        self._pulse.setEndValue(1.0)
        self._pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse.setLoopCount(-1)
        self._pulse.start()

    def _build_step_pages(self) -> None:
        self.stack.addWidget(self._build_step_welcome())
        self.stack.addWidget(self._build_step_profile())
        self.stack.addWidget(self._build_step_habits())
        self.stack.addWidget(self._build_step_goals())
        self.stack.addWidget(self._build_step_finance())
        self.stack.addWidget(self._build_step_focus())
        self.stack.addWidget(self._build_step_confirmation())

    def _build_step_welcome(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(14)
        self._welcome_logo = PhoenixLogoLabel("PHOENIX 2.0")
        self._welcome_logo.setFixedHeight(60)
        self._welcome_logo.setStyleSheet("font-size: 38px; font-weight: 700;")
        msg = QLabel("Seu cockpit pessoal de foco, hábitos e metas começa agora.")
        msg.setWordWrap(True)
        msg.setStyleSheet("color: #AAAAAA; font-size: 14px;")
        layout.addStretch(1)
        layout.addWidget(self._welcome_logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(msg, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        return page

    def _build_step_profile(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Como podemos te chamar?"))
        self.name_input = QLineEdit()
        self.name_input.setObjectName("inp-name")
        self.name_input.setPlaceholderText("Seu nome")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Qual é seu maior foco de vida agora?"))
        self.life_focus = QComboBox()
        self.life_focus.addItems(
            [
                "Carreira e produtividade",
                "Saúde e bem-estar",
                "Aprendizado e crescimento",
                "Finanças pessoais",
                "Projetos pessoais",
                "Equilíbrio geral",
            ]
        )
        layout.addWidget(self.life_focus)
        layout.addStretch(1)
        return page

    def _build_step_habits(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        info = QLabel("Selecione os hábitos que quer acompanhar (pode escolher vários):")
        info.setWordWrap(True)
        info.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(info)

        grid = QGridLayout()
        self.habit_checks: list[QCheckBox] = []
        for i, name in enumerate(self._HABIT_OPTIONS):
            chk = QCheckBox(name)
            chk.setObjectName("habit-card")
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            grid.addWidget(chk, i // 3, i % 3)
            self.habit_checks.append(chk)
        layout.addLayout(grid)

        self.habit_freq_label = QLabel("5× por semana")
        self.habit_freq_label.setStyleSheet("color: #E67E22;")
        self.habit_freq = QSlider(Qt.Orientation.Horizontal)
        self.habit_freq.setRange(3, 7)
        self.habit_freq.setValue(5)
        self.habit_freq.valueChanged.connect(lambda v: self.habit_freq_label.setText(f"{v}× por semana"))

        layout.addWidget(QLabel("Quantas vezes por semana você quer manter cada hábito?"))
        layout.addWidget(self.habit_freq)
        layout.addWidget(self.habit_freq_label)
        layout.addStretch(1)
        return page

    def _build_step_goals(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        helper = QLabel("Adicione até 3 metas que quer alcançar nos próximos meses:")
        helper.setWordWrap(True)
        helper.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(helper)

        self.goal_inputs: list[tuple[QLineEdit, QComboBox]] = []
        for _ in range(3):
            row = QHBoxLayout()
            title = QLineEdit()
            title.setPlaceholderText("Ex: Aprender Python avançado")
            deadline = QComboBox()
            deadline.addItems(["1 mês", "3 meses", "6 meses", "1 ano"])
            row.addWidget(title, 1)
            row.addWidget(deadline)
            layout.addLayout(row)
            self.goal_inputs.append((title, deadline))

        layout.addStretch(1)
        return page

    def _build_step_finance(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Qual é sua renda mensal aproximada?"))
        self.income_combo = QComboBox()
        self.income_combo.addItems(
            [
                "Prefiro não informar",
                "Até R$ 2.000",
                "R$ 2-5k",
                "R$ 5-10k",
                "Acima de R$ 10k",
            ]
        )
        layout.addWidget(self.income_combo)

        layout.addWidget(QLabel("Quais categorias de gasto quer monitorar?"))
        grid = QGridLayout()
        self.fin_checks: list[QCheckBox] = []
        for i, name in enumerate(self._FIN_CATEGORIES):
            chk = QCheckBox(name)
            chk.setObjectName("cat-card")
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            grid.addWidget(chk, i // 4, i % 4)
            self.fin_checks.append(chk)
        layout.addLayout(grid)
        layout.addStretch(1)
        return page

    def _build_step_focus(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Qual duração de sessão funciona melhor para você?"))
        row = QHBoxLayout()
        self.focus_cards: list[QCheckBox] = []
        for text, value in [("25 min - Sprint clássico", 25), ("50 min - Deep work", 50), ("90 min - Flow state", 90)]:
            card = QCheckBox(text)
            card.setObjectName("focus-card")
            card.setProperty("minutes", value)
            card.stateChanged.connect(lambda _, c=card: self._select_focus_card(c))
            row.addWidget(card)
            self.focus_cards.append(card)
        self.focus_cards[0].setChecked(True)
        layout.addLayout(row)

        layout.addWidget(QLabel("Meta de horas focadas por dia:"))
        self.hours_slider = QSlider(Qt.Orientation.Horizontal)
        self.hours_slider.setRange(1, 8)
        self.hours_slider.setValue(2)
        self.hours_label = QLabel("2 horas/dia")
        self.hours_label.setStyleSheet("color: #E67E22;")
        self.hours_slider.valueChanged.connect(lambda v: self.hours_label.setText(f"{v} horas/dia"))
        layout.addWidget(self.hours_slider)
        layout.addWidget(self.hours_label)

        layout.addWidget(QLabel("Qual seu horário de pico de produtividade?"))
        self.peak_combo = QComboBox()
        self.peak_combo.addItems(
            [
                "Manhã (6h-12h)",
                "Tarde (12h-18h)",
                "Noite (18h-24h)",
                "Madrugada",
            ]
        )
        layout.addWidget(self.peak_combo)
        layout.addStretch(1)
        return page

    def _build_step_confirmation(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        self.confirm_title = QLabel("Tudo pronto!")
        self.confirm_title.setStyleSheet("font-size: 18px; color: #F0F0F0; font-weight: 600;")
        layout.addWidget(self.confirm_title)

        self.summary = QLabel("")
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet("color: #AAAAAA; line-height: 1.7;")
        layout.addWidget(self.summary)

        self.load_demo = QCheckBox("Carregar dados de demonstração para explorar o app")
        self.load_demo.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(self.load_demo)
        layout.addStretch(1)
        return page

    def _select_focus_card(self, selected: QCheckBox) -> None:
        for card in self.focus_cards:
            if card is not selected:
                card.blockSignals(True)
                card.setChecked(False)
                card.blockSignals(False)
        self._focus_duration = int(selected.property("minutes") or 25)

    def _go_prev(self) -> None:
        if self._step == 0:
            return
        self._animate_to(self._step - 1)

    def _go_next(self) -> None:
        if not self._persist_current_step():
            return
        if self._step == self._steps_total - 1:
            self.accept()
            return
        self._animate_to(self._step + 1)

    def _animate_to(self, next_step: int) -> None:
        current = self.stack.currentWidget()
        target = self.stack.widget(next_step)
        if current is None or target is None:
            self._step = next_step
            self.stack.setCurrentIndex(next_step)
            self._update_step_ui()
            return

        direction = 1 if next_step > self._step else -1
        width = self.stack.width()
        target.move(QPoint(direction * width, 0))
        target.show()

        anim_out = QPropertyAnimation(current, b"pos", self)
        anim_out.setDuration(300)
        anim_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim_out.setStartValue(QPoint(0, 0))
        anim_out.setEndValue(QPoint(-direction * width, 0))

        anim_in = QPropertyAnimation(target, b"pos", self)
        anim_in.setDuration(300)
        anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim_in.setStartValue(QPoint(direction * width, 0))
        anim_in.setEndValue(QPoint(0, 0))

        group = QParallelAnimationGroup(self)
        group.addAnimation(anim_out)
        group.addAnimation(anim_in)

        def finalize() -> None:
            self.stack.setCurrentIndex(next_step)
            current.move(QPoint(0, 0))
            target.move(QPoint(0, 0))
            self._step = next_step
            self._update_step_ui()

        group.finished.connect(finalize)
        group.start()

    def _persist_current_step(self) -> bool:
        if self._step == 1:
            self._data["name"] = self.name_input.text().strip() or "Usuário"
            self._data["life_focus"] = self.life_focus.currentText()

        if self._step == 2:
            habits = [chk.text() for chk in self.habit_checks if chk.isChecked()]
            self._data["habits"] = habits
            self._data["habit_frequency"] = self.habit_freq.value()

        if self._step == 3:
            goals: list[dict[str, object]] = []
            offsets = {"1 mês": 30, "3 meses": 90, "6 meses": 180, "1 ano": 365}
            for title, deadline in self.goal_inputs:
                value = title.text().strip()
                if value:
                    goals.append({"title": value, "deadline_offset": offsets.get(deadline.currentText(), 90)})
            self._data["goals"] = goals

        if self._step == 4:
            self._data["income_range"] = self.income_combo.currentText()
            self._data["budget_categories"] = [chk.text() for chk in self.fin_checks if chk.isChecked()]

        if self._step == 5:
            self._data["focus_duration"] = self._focus_duration
            self._data["daily_goal_hours"] = self.hours_slider.value()
            self._data["peak_time"] = self.peak_combo.currentText()
            self._refresh_confirmation()

        if self._step == 6:
            self._data["load_demo_data"] = self.load_demo.isChecked()

        return True

    def _refresh_confirmation(self) -> None:
        name = str(self._data.get("name", "Usuário"))
        habits_count = len(self._data.get("habits", []))
        goals_count = len(self._data.get("goals", []))
        cats_count = len(self._data.get("budget_categories", []))
        hours = self._data.get("daily_goal_hours", 2)
        self.confirm_title.setText(f"Tudo pronto, {name}! 🔥")
        self.summary.setText(
            f"✓ {habits_count} hábitos configurados\n"
            f"✓ {goals_count} metas criadas\n"
            f"✓ {cats_count} categorias financeiras\n"
            f"✓ Meta de {hours}h de foco/dia"
        )

    def _update_step_ui(self) -> None:
        titles = [
            ("Bem-vindo ao Phoenix", "Vamos personalizar sua experiência em menos de 2 minutos."),
            ("Perfil básico", "Conte para o Phoenix como personalizar sua jornada."),
            ("Seus hábitos", "Crie sua base de consistência diária."),
            ("Suas metas para este ano", "Defina alvos claros para os próximos meses."),
            ("Controle financeiro", "Selecione faixas e categorias para acompanhar."),
            ("Sua rotina de trabalho", "Configure blocos de foco alinhados ao seu ritmo."),
            ("Confirmação", "Revise tudo antes de entrar no Phoenix."),
        ]
        title, subtitle = titles[self._step]
        self.progress.set_progress(self._step + 1, self._steps_total)
        self.step_indicator.setText(f"Passo {self._step + 1} de {self._steps_total}")
        self.step_title.setText(title)
        self.step_subtitle.setText(subtitle)

        self.prev_btn.setVisible(self._step > 0)
        if self._step == 0:
            self.next_btn.setText("Começar")
        elif self._step == self._steps_total - 1:
            self.next_btn.setText("Entrar no Phoenix")
        else:
            self.next_btn.setText("Próximo")

    def get_data(self) -> dict[str, object]:
        return dict(self._data)


def is_first_run(session: Session) -> bool:
    """Indica se o banco ainda não possui dados principais de uso."""

    goals = session.scalar(select(func.count(Goal.id))) or 0
    habits = session.scalar(select(func.count(Habit.id))) or 0
    txs = session.scalar(select(func.count(Transaction.id))) or 0
    return goals == 0 and habits == 0 and txs == 0
