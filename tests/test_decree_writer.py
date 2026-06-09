"""诏书润色官护栏：公开诏不得含自指保密话术（B5 修复）。

LLM 输出非确定不可单测，这里确定性地验证「护栏指令已注入 prompt」；
行为层（密语草案→输出无保密话）由真实跑一次验证（见 docs/raw 或手动 smoke）。
"""

from __future__ import annotations

from types import SimpleNamespace

from ming_sim.decree import write_decree_with_agno
from ming_sim.models import GameState, LLMConfig


def test_decree_writer_prompt_has_secrecy_guardrail(game):
    _, _, content = game
    p = content.decree_writer_prompt
    assert "公开诏书禁含自指保密话术" in p          # 护栏标题在
    assert "严防外泄" in p and "防外朝物议" in p     # 列了要剥的保密措辞
    assert "明面事由" in p                          # 给了"只取可公开部分"的处理法


def test_write_decree_uses_streaming_agent_run(monkeypatch):
    calls = []

    class FakeAgent:
        model = SimpleNamespace(id="fake-model")

        def run(self, prompt, **kwargs):
            calls.append(kwargs)
            assert kwargs.get("stream") is True
            assert kwargs.get("stream_events") is True
            yield SimpleNamespace(content="奉天承运，")
            yield SimpleNamespace(content="皇帝诏曰。")
            yield SimpleNamespace(is_final=True, content="", metrics=None)

    monkeypatch.setattr("ming_sim.decree.create_decree_writer_agent", lambda *args, **kwargs: FakeAgent())

    text = write_decree_with_agno(
        LLMConfig(api_key="test", base_url="https://api.openai.com/v1", model="gpt-test"),
        agno_db=None,
        state=GameState(),
        directives=[{"text": "减免辽饷"}],
    )

    assert text == "奉天承运，皇帝诏曰。"
    assert calls
