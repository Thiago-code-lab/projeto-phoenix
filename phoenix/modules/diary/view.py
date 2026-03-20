from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QColor, QKeySequence, QShortcut, QTextCharFormat, QSyntaxHighlighter
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from phoenix.core.events import EventBus
from phoenix.modules.journal.controller import JournalController
from phoenix.utils.constants import Events

try:
    import markdown as md_lib
except ImportError:  # pragma: no cover
    md_lib = None


class DiaryHighlighter(QSyntaxHighlighter):
    """Realce basico para marcacoes markdown no diario."""

    def highlightBlock(self, text: str) -> None:  # type: ignore[override]
        if text.startswith("#"):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#C0392B"))
            fmt.setFontWeight(700)
            self.setFormat(0, len(text), fmt)
        if text.startswith(">"):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#666666"))
            fmt.setFontItalic(True)
            self.setFormat(0, len(text), fmt)


class DiaryView(QWidget):
    """Editor de diario rico com markdown e mood tracker."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self.controller = JournalController()
        self.event_bus = event_bus
        self._selected_id: int | None = None
        self._started_at = datetime.now()
        self._active_template = "entrada_livre"
        self._mood_value: int | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(8)

        self.title = QLineEdit()
        self.title.setPlaceholderText("Titulo da entrada")
        root.addWidget(self.title)

        self.toolbar = QToolBar()
        root.addWidget(self.toolbar)
        self._build_toolbar()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Escreva sua entrada...")
        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        self.splitter.setSizes([500, 500])
        root.addWidget(self.splitter, 1)

        self.highlighter = DiaryHighlighter(self.editor.document())

        mood_row = QHBoxLayout()
        mood_row.addWidget(QLabel("Mood:"))
        self._mood_buttons: list[QPushButton] = []
        for value, emoji in [(1, ":("), (2, ":/"), (3, ":|"), (4, ":)"), (5, ":D")]:
            button = QPushButton(emoji)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, v=value: self._set_mood(v, checked))
            mood_row.addWidget(button)
            self._mood_buttons.append(button)
        mood_row.addStretch(1)
        root.addLayout(mood_row)

        action_row = QHBoxLayout()
        self.new_menu_btn = QPushButton("Novo")
        self.new_menu = QMenu(self)
        self.new_menu.addAction("Entrada livre", lambda: self._apply_template("entrada_livre"))
        self.new_menu.addAction("Reflexao diaria", lambda: self._apply_template("reflexao_diaria"))
        self.new_menu.addAction("Revisao semanal", lambda: self._apply_template("revisao_semanal"))
        self.new_menu.addAction("Planejamento do dia", lambda: self._apply_template("planejamento_dia"))
        self.new_menu_btn.setMenu(self.new_menu)
        self.save_btn = QPushButton("Salvar")
        self.save_btn.setObjectName("btn-primary")
        action_row.addWidget(self.new_menu_btn)
        action_row.addStretch(1)
        action_row.addWidget(self.save_btn)
        root.addLayout(action_row)

        self.stats = QLabel("0 palavras | 0 caracteres | ~0 min leitura | Escrevendo ha 0 min")
        root.addWidget(self.stats)

        self.save_btn.clicked.connect(self._save)
        self.editor.textChanged.connect(self._on_text_changed)
        self.title.textChanged.connect(self._on_text_changed)
        QShortcut(QKeySequence("Ctrl+Shift+P"), self, activated=self._toggle_preview)

        self._stats_timer = QTimer(self)
        self._stats_timer.setInterval(500)
        self._stats_timer.timeout.connect(self._refresh_stats)
        self._stats_timer.start()
        self._apply_template("entrada_livre")

    def _build_toolbar(self) -> None:
        self._add_insert_action("Negrito", "**texto**", "Ctrl+B")
        self._add_insert_action("Italico", "*texto*", "Ctrl+I")
        self._add_insert_action("Sublinhado", "<u>texto</u>", "Ctrl+U")
        self._add_insert_action("H1", "# ")
        self._add_insert_action("H2", "## ")
        self._add_insert_action("H3", "### ")
        self._add_insert_action("Bullet", "- item")
        self._add_insert_action("Numerada", "1. item")
        self._add_insert_action("Citacao", "> texto")
        self._add_insert_action("Codigo", "`codigo`")
        self._add_insert_action("Bloco", "```\n\n```")
        self._add_insert_action("Separador", "\n---\n")

        image_action = QAction("Imagem", self)
        image_action.triggered.connect(self._insert_image)
        self.toolbar.addAction(image_action)

        preview_action = QAction("Toggle Preview", self)
        preview_action.triggered.connect(self._toggle_preview)
        self.toolbar.addAction(preview_action)

    def _add_insert_action(self, text: str, token: str, shortcut: str | None = None) -> None:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(lambda: self.editor.insertPlainText(token))
        self.toolbar.addAction(action)

    def _insert_image(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Selecionar imagem", "", "Imagens (*.png *.jpg *.jpeg *.webp)")
        if not selected:
            return
        assets_dir = Path(__file__).resolve().parents[2] / "assets" / "diary_images"
        assets_dir.mkdir(parents=True, exist_ok=True)
        source = Path(selected)
        target = assets_dir / source.name
        if source != target:
            target.write_bytes(source.read_bytes())
        self.editor.insertPlainText(f"![{target.stem}](assets/diary_images/{target.name})")

    def _toggle_preview(self) -> None:
        self.preview.setVisible(not self.preview.isVisible())

    def _set_mood(self, value: int, checked: bool) -> None:
        if not checked:
            return
        self._mood_value = value
        for button in self._mood_buttons:
            if button is not self.sender():
                button.setChecked(False)

    def _apply_template(self, kind: str) -> None:
        self._active_template = kind
        today = date.today().isoformat()
        templates = {
            "entrada_livre": "",
            "reflexao_diaria": f"## Reflexao - {today}\n\n### O que foi bom hoje?\n\n### O que poderia ter sido melhor?\n\n### Gratidao do dia\n",
            "revisao_semanal": "## Revisao semanal\n\n### Conquistas\n\n### Aprendizados\n\n### Proxima semana\n",
            "planejamento_dia": f"## Planejamento - {today}\n\n### Manha\n\n### Tarde\n\n### Noite\n",
        }
        self.editor.setPlainText(templates.get(kind, ""))

    def _on_text_changed(self) -> None:
        text = self.editor.toPlainText()
        if md_lib is not None:
            html = md_lib.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
        else:
            html = f"<pre>{text}</pre>"
        self.preview.setHtml(
            "<style>body{color:#f0f0f0;background:#161616;font-family:Segoe UI;padding:12px}</style>" + html
        )

    def _refresh_stats(self) -> None:
        text = self.editor.toPlainText()
        words = len([part for part in text.split() if part.strip()])
        chars = len(text)
        read_min = max(1, int(words / 200)) if words else 0
        writing_min = int((datetime.now() - self._started_at).total_seconds() / 60)
        self.stats.setText(
            f"{words} palavras | {chars} caracteres | ~{read_min} min leitura | Escrevendo ha {writing_min} min"
        )

    def _save(self) -> None:
        content = self.editor.toPlainText().strip()
        if not content:
            self._toast("Conteudo vazio nao pode ser salvo.", "warning")
            return
        words = len([part for part in content.split() if part.strip()])
        payload = {
            "date": date.today(),
            "title": self.title.text().strip() or "Entrada",
            "content": content,
            "mood": self._mood_value,
            "tags": None,
            "word_count": words,
            "template": self._active_template,
        }
        if self._selected_id is None:
            entry = self.controller.create(payload)
            self._selected_id = entry.id
        else:
            self.controller.update(self._selected_id, payload)
        self._toast("Entrada salva.", "success")
        if self.event_bus is not None:
            self.event_bus.publish(Events.DATA_CHANGED, {"module": "diary"})

    def _toast(self, message: str, kind: str) -> None:
        if self.event_bus is None:
            return
        self.event_bus.publish(Events.SHOW_TOAST, {"message": f"[{kind}] {message}"})

