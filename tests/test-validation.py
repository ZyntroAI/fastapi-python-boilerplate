from ..validator import validate_all

def test_valid_workflow(tmp_path):
    f = tmp_path / "ok.yml"
    f.write_text("name: Test\non: push\njobs: {}\n")
    result = validate_all(str(f))
    assert result["yaml"]["pass"]
