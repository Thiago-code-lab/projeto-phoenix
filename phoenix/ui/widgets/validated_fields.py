from __future__ import annotations

"""Campos validados reutilizaveis para formularios PyQt6.

Este modulo centraliza validacao inline e agregacao por formulario.
"""

from collections.abc import Callable
from datetime import date

from PyQt6.QtCore import QObject, QDate, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QDateEdit, QDoubleSpinBox, QLabel, QLineEdit, QPushButton

ValidationRule = Callable[[object], tuple[bool, str]]


class _FieldValidationMixin:
    """Comportamento compartilhado de validacao para campos visuais.

    Attributes:
        error_label: Label exibida abaixo do campo com mensagem de erro.
    """

    def _init_validation(self) -> None:
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ef4444; font-size: 11px;")
        self._required = False
        self._rules: list[ValidationRule] = []
        self._is_valid = True
        self._error_message = ""

    def set_required(self, required: bool = True) -> None:
        """Marca o campo como obrigatorio.

        Args:
            required: Quando True, o campo nao pode ficar vazio.
        """

        self._required = required

    def add_rule(self, rule: ValidationRule) -> None:
        """Adiciona regra customizada de validacao.

        Args:
            rule: Funcao que recebe valor e retorna (is_valid, mensagem).
        """

        self._rules.append(rule)

    def validate(self) -> bool:
        """Executa validacao do campo e atualiza feedback inline."""

        value = self._value_for_validation()
        is_empty = value in (None, "", 0)
        if self._required and is_empty:
            self._set_invalid("Campo obrigatorio.")
            return False

        for rule in self._rules:
            ok, message = rule(value)
            if not ok:
                self._set_invalid(message or "Valor invalido.")
                return False

        self._set_valid()
        return True

    def error(self) -> str:
        """Retorna a mensagem de erro atual do campo."""

        return self._error_message

    def _set_invalid(self, message: str) -> None:
        self._is_valid = False
        self._error_message = message
        self.error_label.setText(message)
        self.setProperty("invalid", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def _set_valid(self) -> None:
        self._is_valid = True
        self._error_message = ""
        self.error_label.setText("")
        self.setProperty("invalid", False)
        self.style().unpolish(self)
        self.style().polish(self)


class ValidatedLineEdit(QLineEdit, _FieldValidationMixin):
    """QLineEdit com validacao inline e mensagem abaixo do campo."""

    def __init__(self, text: str = "") -> None:
        super().__init__(text)
        self._init_validation()
        self.editingFinished.connect(self.validate)

    def _value_for_validation(self) -> object:
        return self.text().strip()


class ValidatedDateEdit(QDateEdit, _FieldValidationMixin):
    """QDateEdit com validacao de data e controle de data futura."""

    def __init__(self) -> None:
        super().__init__()
        self._init_validation()
        self.setCalendarPopup(True)
        self._allow_future = True
        self.editingFinished.connect(self.validate)

    def set_allow_future(self, allow_future: bool) -> None:
        """Controla se datas futuras sao permitidas.

        Args:
            allow_future: Se False, bloqueia valores apos hoje.
        """

        self._allow_future = allow_future

    def validate(self, *args: object) -> object:
        if args:
            return super().validate(*args)  # type: ignore[misc]
        if not self._allow_future and self.date().toPyDate() > date.today():
            self._set_invalid("Data futura nao permitida.")
            return False
        return _FieldValidationMixin.validate(self)

    def _value_for_validation(self) -> object:
        return self.date().toPyDate()


class ValidatedSpinBox(QDoubleSpinBox, _FieldValidationMixin):
    """QDoubleSpinBox com validacao de limites e feedback visual."""

    def __init__(self) -> None:
        super().__init__()
        self._init_validation()
        self.valueChanged.connect(lambda _: self.validate())

    def set_min_max(self, min_value: float, max_value: float) -> None:
        """Define limites minimos e maximos para validacao.

        Args:
            min_value: Limite minimo aceito.
            max_value: Limite maximo aceito.
        """

        self.setRange(min_value, max_value)

    def validate(self, *args: object) -> object:
        if args:
            return super().validate(*args)  # type: ignore[misc]
        value = self.value()
        if value < self.minimum() or value > self.maximum():
            self._set_invalid(f"Valor deve estar entre {self.minimum()} e {self.maximum()}.")
            return False
        return _FieldValidationMixin.validate(self)

    def _value_for_validation(self) -> object:
        return self.value()


class ValidatedComboBox(QComboBox, _FieldValidationMixin):
    """QComboBox com validacao de selecao obrigatoria."""

    def __init__(self) -> None:
        super().__init__()
        self._init_validation()
        self.currentIndexChanged.connect(lambda _: self.validate())

    def validate(self) -> bool:
        if self._required and (self.currentIndex() < 0 or not self.currentText().strip()):
            self._set_invalid("Selecione uma opcao valida.")
            return False
        return _FieldValidationMixin.validate(self)

    def _value_for_validation(self) -> object:
        return self.currentText().strip()


class FormValidator(QObject):
    """Agrega validacao de multiplos campos de formulario.

    Signals:
        validated: Emite ``True`` quando o formulario esta valido.
    """

    validated = pyqtSignal(bool)

    def __init__(self, fields: list[object] | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._fields: list[object] = fields or []
        self._submit_buttons: list[QPushButton] = []

    def add_field(self, field: object) -> None:
        """Registra um campo no validador."""

        self._fields.append(field)

    def bind_submit_button(self, button: QPushButton) -> None:
        """Conecta um botao de submit ao estado do formulario."""

        self._submit_buttons.append(button)
        button.setEnabled(self.is_valid())

    def errors(self) -> dict[str, str]:
        """Retorna mapa de erros por objectName de campo."""

        payload: dict[str, str] = {}
        for field in self._fields:
            if hasattr(field, "validate") and hasattr(field, "error"):
                if not field.validate():
                    key = field.objectName() or field.__class__.__name__
                    payload[key] = field.error()
        return payload

    def is_valid(self) -> bool:
        """Valida todos os campos registrados."""

        all_valid = True
        for field in self._fields:
            if hasattr(field, "validate"):
                all_valid = bool(field.validate()) and all_valid
        for button in self._submit_buttons:
            button.setEnabled(all_valid)
        self.validated.emit(all_valid)
        return all_valid

    @property
    def fields(self) -> list[object]:
        """Retorna campos registrados para uso externo."""

        return self._fields
