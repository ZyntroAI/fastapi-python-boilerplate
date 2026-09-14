from ..git_ops import current_branch

def test_branch_name():
    branch = current_branch()
    assert branch  # non-empty string
