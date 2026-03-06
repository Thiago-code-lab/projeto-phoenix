from phoenix.ui.widgets.stat_card import StatCard


def test_stat_card_updates(app) -> None:
    card = StatCard("Teste", "10", "+1")
    card.update_values("12", "+2")
    assert card.value_widget.text() == "12"
