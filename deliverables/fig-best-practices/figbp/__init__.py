"""figbp — the FIG best-practices gate engine.

Import surface kept small on purpose:

    from figbp import load_policy, run_gate
"""

from .policy import Policy, load_policy, glob_to_regex, iter_files
from .gate import CriterionResult, GateReport, run_gate

__all__ = [
    "Policy",
    "load_policy",
    "glob_to_regex",
    "iter_files",
    "CriterionResult",
    "GateReport",
    "run_gate",
]

__version__ = "1.0.0"
