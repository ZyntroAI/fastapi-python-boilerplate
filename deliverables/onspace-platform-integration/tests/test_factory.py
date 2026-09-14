"""Factory/wiring tests — the composition root must be deterministic."""
from onspace.config import OnSpaceSettings, get_onspace_settings
from onspace.factory import build_providers, build_service
from onspace.providers import (
    AnthropicProvider,
    GoogleProvider,
    MockProvider,
    OpenAIProvider,
)


def test_no_keys_falls_back_to_mock():
    s = OnSpaceSettings(openai_api_key="", anthropic_api_key="", google_api_key="")
    chain = build_providers(s)
    assert len(chain) == 1
    assert isinstance(chain[0], MockProvider)


def test_provider_order_is_openai_anthropic_google():
    s = OnSpaceSettings(
        openai_api_key="a", anthropic_api_key="b", google_api_key="c"
    )
    chain = build_providers(s)
    assert [type(p) for p in chain] == [OpenAIProvider, AnthropicProvider, GoogleProvider]


def test_partial_keys_only_registers_present_providers():
    s = OnSpaceSettings(openai_api_key="", anthropic_api_key="b", google_api_key="")
    chain = build_providers(s)
    assert [type(p) for p in chain] == [AnthropicProvider]


def test_build_service_uses_settings_thresholds():
    s = OnSpaceSettings(circuit_failure_threshold=7, circuit_recovery_seconds=12.5)
    svc = build_service(settings=s)
    assert svc.settings.circuit_failure_threshold == 7


def test_env_prefix_is_onspace():
    s = OnSpaceSettings()
    assert s.app_name == "OnSpaceAI"
    assert get_onspace_settings() is get_onspace_settings()
