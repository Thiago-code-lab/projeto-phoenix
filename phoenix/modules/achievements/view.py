from __future__ import annotations

from PyQt6.QtWidgets import QComboBox, QFrame, QGridLayout, QLabel, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from phoenix.modules.achievements.controller import AchievementsController


class AchievementCard(QFrame):
    """Card visual de conquista."""

    def __init__(self, data: dict[str, object], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        unlocked = bool(data.get("unlocked", False))
        rarity = str(data.get("rarity", "common"))
        palette = {
            "common": "#2a2a2a",
            "rare": "#0d1f3c",
            "epic": "#1a0d2e",
            "legendary": "#1f1000",
        }
        color = palette.get(rarity, "#2a2a2a") if unlocked else "#1a1a1a"
        self.setStyleSheet(f"background: {color}; border: 1px solid #3a3a3a; border-radius: 10px;")

        layout = QVBoxLayout(self)
        title = QLabel(f"{data.get('icon', '*')}  {data.get('name', 'Conquista')}")
        title.setObjectName("label-title")
        desc = QLabel(str(data.get("description", "")))
        desc.setWordWrap(True)
        xp = QLabel(f"+{data.get('xp_reward', 0)} XP")
        xp.setStyleSheet("color: #E67E22;")
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(xp)


class AchievementsView(QWidget):
    """Tela de consulta de conquistas desbloqueadas e bloqueadas."""

    def __init__(self) -> None:
        super().__init__()
        self.controller = AchievementsController()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        header = QLabel("Conquistas")
        header.setObjectName("label-title")
        root.addWidget(header)

        self.rarity_filter = QComboBox()
        self.rarity_filter.addItems(["all", "common", "rare", "epic", "legendary"])
        self.rarity_filter.currentTextChanged.connect(self.refresh)
        root.addWidget(self.rarity_filter)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self.refresh()

    def refresh(self) -> None:
        all_data = self.controller.list_all()
        selected_rarity = self.rarity_filter.currentText()
        if selected_rarity != "all":
            all_data = [item for item in all_data if item.get("rarity") == selected_rarity]

        categories = ["all", "habits", "goals", "finances", "focus", "general"]
        self.tabs.clear()
        for category in categories:
            filtered = all_data if category == "all" else [item for item in all_data if item.get("category") == category]
            self.tabs.addTab(self._build_tab(filtered), category.capitalize())

    def _build_tab(self, rows: list[dict[str, object]]) -> QWidget:
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(10)

        for idx, row in enumerate(rows):
            grid.addWidget(AchievementCard(row), idx // 2, idx % 2)

        if not rows:
            grid.addWidget(QLabel("Nenhuma conquista para o filtro selecionado."), 0, 0)

        holder = QWidget()
        layout = QVBoxLayout(holder)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        return holder
