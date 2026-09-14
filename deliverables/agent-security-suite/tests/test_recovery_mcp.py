"""Recovery + MCP modules — lazy-import behavior when langgraph/mcp absent."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_tmp = tempfile.mkdtemp()
os.environ["AUDIT_DB_PATH"] = os.path.join(_tmp, "audit_test.db")

from agent_security_suite import recovery, mcp_client


def test_recovery_build_graph_raises_without_langgraph():
    # langgraph not installed in sandbox -> build_graph raises ImportError
    import pytest
    with pytest.raises(ImportError):
        recovery.build_graph()


def test_recovery_rollback_reports_missing():
    # get_graph() will raise ImportError first (langgraph absent) — surface cleanly
    import pytest
    with pytest.raises(ImportError):
        recovery.get_graph()


def test_mcp_client_raises_without_mcp():
    import pytest
    with pytest.raises(ModuleNotFoundError):
        mcp_client.MCPClient(["echo"])


def test_lazy_modules_importable():
    # modules themselves import fine (lazy deps); only constructors raise
    assert hasattr(recovery, "build_graph")
    assert hasattr(mcp_client, "MCPClient")
