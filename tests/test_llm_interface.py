from types import SimpleNamespace

from config.settings import Settings
from core.llm_interface import generate_structured
from schemas.step0_refinement import RefinementOutput


def test_real_llm_uses_fallback_and_validates_schema(monkeypatch):
    calls = []

    def fake_call(model, prompt, schema, settings):
        calls.append(model)
        if model == "primary":
            raise RuntimeError("primary unavailable")
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"refined_ticket":"done","gaps":[],"questions":[],"assumptions":[]}'
                    )
                )
            ]
        )

    monkeypatch.setattr("core.llm_interface._call_model", fake_call)
    settings = Settings(
        use_mock_llm=False,
        primary_model="primary",
        fallback_model="fallback",
        local_model="local",
    )

    output = generate_structured("refine", RefinementOutput, use_mock=False, settings=settings)

    assert output.refined_ticket == "done"
    assert calls == ["primary", "fallback"]
