function governanceGate(result) {
  const checks = {
    lint: result.lint === "passed",
    test: result.test === "passed",
    coverage: result.coverage === "passed",
    security: result.security === "passed",
  };

  const passed = Object.values(checks).every(Boolean);

  return {
    status: passed ? "passed" : "failed",
    checks,
    releaseAllowed: passed,
  };
}

module.exports = {
  governanceGate,
};
