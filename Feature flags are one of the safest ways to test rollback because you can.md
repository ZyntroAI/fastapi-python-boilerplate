This is a clear, practical explanation of feature-flag rollback testing. It effectively covers the deployment pattern, pipeline automation, canary rollout, validation checks, and expected success criteria.

### Pattern: Deploy Once, Roll Back via Flag

```text
Deploy v2 (Feature OFF)
      ↓
Verify application health
      ↓
Enable Feature Flag
      ↓
Run tests
      ↓
Detect issue
      ↓
Disable Feature Flag
      ↓
Run rollback validation
```

The "rollback" is simply turning the flag off.

### Example

```javascript
if (featureFlags.newCheckout) {
  return newCheckout();
} else {
  return legacyCheckout();
}
```

### CI/CD Rollback Test

```yaml
feature_flag_test:
  stage: test
  script:
    # Enable feature
    - ./set-flag.sh newCheckout true

    # Run tests
    - ./smoke-tests.sh

    # Simulate failure
    - ./inject-failure.sh

    # Roll back by disabling flag
    - ./set-flag.sh newCheckout false

    # Verify legacy flow works
    - ./smoke-tests.sh
```

### Canary Rollback Test

Expose the feature to a small percentage of users:

```text
0% → 5% → 25% → 100%
```

If metrics degrade:

```text
Feature Flag
     ↓
Off
     ↓
Traffic returns to stable path
```

This validates that flag-based rollback works before a full rollout.

### What to Verify After Disabling the Flag

Automate checks for:

```bash
curl -f https://app.example.com/health
./test-login.sh
./test-checkout.sh
./test-api.sh
```

Confirm:

- Health checks pass
- Critical user journeys succeed
- Error rates return to baseline
- Latency returns to normal

### Feature Flag Platforms

Common tools include:

- LaunchDarkly
- Unleash
- Azure App Configuration Feature Management
- ConfigCat
- Split

Most provide APIs that CI/CD pipelines can use to turn flags on and off automatically.

### Best Practice

Maintain both code paths during testing:

```text
New Feature Path
       ↕
Feature Flag
       ↕
Legacy Stable Path
```

A rollback test succeeds when disabling the flag immediately restores the stable path and all validation tests pass, without requiring a deployment rollback.