"""pr-triage-automove — relocate misplaced root files during PR triage,
while keeping the FastAPI app bootable.

Public entry points:

    from pr_triage_automove import config, classify, probe, automove

    cfg = config.load_config(repo)
    items, meta = classify.classify(repo, cfg, "2026-09")
    before = probe.probe(repo, probe.detect_targets(repo), env)
    report = automove.run(repo, apply=True)
"""
__all__ = ["config", "classify", "probe", "automove"]
__version__ = "1.0.0"
