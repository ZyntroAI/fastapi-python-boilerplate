python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------

@dataclass
class FakeSkill:
    id: str
    version: str = "1.0.0"
    platforms: set[str] = field(default_factory=set)
    capabilities: set[str] = field(default_factory=set)
    enabled: bool = True
    deprecated: bool = False

@dataclass
class FakeSkillRegistry:
    skills: dict[str, FakeSkill]

    def get(self, skill_id: str) -> FakeSkill | None:
        skill = self.skills.get(skill_id)

        if skill is None or not skill.enabled:
            return None

        return skill

    def find_compatible(
        self,
        skill_id: str,
        platform: str | None = None,
    ) -> FakeSkill | None:
        skill = self.get(skill_id)

        if skill is None:
            return None

        if platform and skill.platforms:
            if platform not in skill.platforms:
                return None

        return skill

@dataclass
class FakeResolverResult:
    skills: list[FakeSkill] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    fallbacks: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)

class FakeRequirement:
    def __init__(
        self,
        *,
        skills: list[str] | None = None,
        platforms: list[str] | None = None,
    ) -> None:
        self.skills = skills or []
        self.platforms = platforms or []

class FakeSkillResolver:
    """
    Minimal resolver contract used by these tests.

    Replace this import-free test double with the real resolver once
    core.tasks.resolver is implemented.
    """

    def __init__(
        self,
        registry: FakeSkillRegistry,
        fallback_map: dict[str, list[str]] | None = None,
    ) -> None:
        self.registry = registry
        self.fallback_map = fallback_map or {}

    def resolve(
        self,
        requirement: FakeRequirement,
    ) -> FakeResolverResult:
        result = FakeResolverResult(
            platforms=list(dict.fromkeys(requirement.platforms))
        )

        seen: set[str] = set()

        for skill_id in requirement.skills:
            if skill_id in seen:
                continue

            seen.add(skill_id)

            compatible = self._resolve_skill(
                skill_id,
                result.platforms,
                result,
            )

            if compatible is not None:
                result.skills.append(compatible)
                continue

            result.unresolved.append(skill_id)

        return result

    def _resolve_skill(
        self,
        skill_id: str,
        platforms: list[str],
        result: FakeResolverResult,
    ) -> FakeSkill | None:
        if not platforms:
            return self.registry.get(skill_id)

        for platform in platforms:
            skill = self.registry.find_compatible(
                skill_id,
                platform,
            )

            if skill is not None:
                return skill

        for fallback_id in self.fallback_map.get(skill_id, []):
            for platform in platforms:
                fallback = self.registry.find_compatible(
                    fallback_id,
                    platform,
                )

                if fallback is not None:
                    result.fallbacks.append(fallback_id)
                    return fallback

        return None

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def registry() -> FakeSkillRegistry:
    return FakeSkillRegistry(
        skills={
            "crystal-forms": FakeSkill(
                id="crystal-forms",
                platforms={"web", "android", "ios"},
                capabilities={"forms"},
            ),
            "crystal-form-validation": FakeSkill(
                id="crystal-form-validation",
                platforms={"web", "android", "ios"},
                capabilities={"validation"},
            ),
            "crystal-form-security": FakeSkill(
                id="crystal-form-security",
                platforms={"web", "android", "ios"},
                capabilities={"security"},
            ),
            "crystal-android-native": FakeSkill(
                id="crystal-android-native",
                platforms={"android"},
            ),
            "crystal-ios-native": FakeSkill(
                id="crystal-ios-native",
                platforms={"ios"},
            ),
            "crystal-form-basic": FakeSkill(
                id="crystal-form-basic",
                platforms={"web", "android", "ios"},
            ),
        }
    )

@pytest.fixture
def resolver(
    registry: FakeSkillRegistry,
) 
