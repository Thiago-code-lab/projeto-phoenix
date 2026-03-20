from __future__ import annotations

import pytest
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QPushButton

from phoenix.ui.widgets.validated_fields import FormValidator, ValidatedDateEdit, ValidatedLineEdit, ValidatedSpinBox

pytestmark = [pytest.mark.ui]


def test_validated_line_edit_required(app) -> None:
    field = ValidatedLineEdit()
    field.set_required(True)
    assert field.validate() is False
    field.setText("Titulo")
    assert field.validate() is True


def test_validated_spinbox_range(app) -> None:
    field = ValidatedSpinBox()
    field.set_min_max(1, 5)
    field.setValue(3)
    assert field.validate() is True


def test_validated_date_edit_future_block(app) -> None:
    field = ValidatedDateEdit()
    field.set_allow_future(False)
    field.setDate(QDate.currentDate().addDays(1))
    assert field.validate() is False


def test_form_validator_disables_submit_button(app) -> None:
    line = ValidatedLineEdit()
    line.set_required(True)
    submit = QPushButton("Salvar")
    validator = FormValidator([line])
    validator.bind_submit_button(submit)

    assert submit.isEnabled() is False
    line.setText("ok")
    validator.is_valid()
    assert submit.isEnabled() is True
