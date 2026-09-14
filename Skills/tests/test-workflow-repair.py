from ..repair.actions import pin_all_actions

def test_pins_checkout():
    yaml_text = "uses: actions/checkout@v4"
    result = pin_all_actions(yaml_text)
    assert "11bd71901bbe5b1630ceea73d2759718672a689f" in result
