"""Smoke tests for funai.

funai is a thin OpenAI-compatible LLM wrapper for Moonshot/DeepSeek. These
tests avoid any real network access and any real secret retrieval:

- All calls to the OpenAI-compatible `chat.completions.create` are mocked.
- All calls to `funsecret.secret.read_cache_secret` are mocked, so nothing
  ever tries to read a real API key from a local/remote secret store.

This is a smoke test suite only: it checks that the package imports and
that the core public classes/functions behave sanely with mocked
dependencies. It does not attempt to validate real LLM behavior.
"""

from unittest.mock import MagicMock, patch

import pytest


def _fake_chat_completion(content="hello world"):
    """Build a real ChatCompletion instance (fun_chat checks isinstance)."""
    from openai.types.chat import ChatCompletion
    from openai.types.chat.chat_completion import Choice
    from openai.types.chat.chat_completion_message import ChatCompletionMessage

    msg = ChatCompletionMessage(role="assistant", content=content)
    choice = Choice(finish_reason="stop", index=0, message=msg)
    return ChatCompletion(
        id="test-id",
        choices=[choice],
        created=0,
        model="test-model",
        object="chat.completion",
    )


def test_import_top_level_package():
    """The top-level `funai` package must import cleanly."""
    import funai  # noqa: F401


def test_import_llm_submodule():
    """`funai.llm` must import and expose the documented public API."""
    from funai import llm

    assert hasattr(llm, "get_model")
    assert hasattr(llm, "Moonshot")
    assert hasattr(llm, "Deepseek")
    assert llm.__all__ == ["get_model", "Deepseek", "Moonshot"]


def test_import_models_submodule():
    from funai.llm import models

    assert hasattr(models, "BaseModel")
    assert hasattr(models, "Moonshot")
    assert hasattr(models, "Deepseek")
    assert hasattr(models, "get_model")


@patch("funai.llm.models.read_cache_secret")
def test_moonshot_construction_with_explicit_api_key(mock_read_secret):
    """Constructing Moonshot with an explicit api_key must not touch funsecret."""
    from funai.llm import Moonshot

    model = Moonshot(api_key="sk-fake-key")

    assert model.model_name == "moonshot-v1-8k"
    assert model.llm_provider == "moonshot"
    assert model.base_url is not None
    mock_read_secret.assert_not_called()


@patch("funai.llm.models.read_cache_secret")
def test_deepseek_construction_with_explicit_api_key(mock_read_secret):
    """Constructing Deepseek with an explicit api_key must not touch funsecret."""
    from funai.llm import Deepseek

    model = Deepseek(api_key="sk-fake-key")

    assert model.model_name == "deepseek-chat"
    assert model.llm_provider == "deepseek"
    mock_read_secret.assert_not_called()


@patch("funai.llm.models.read_cache_secret", return_value="sk-fake-from-secret")
def test_moonshot_construction_falls_back_to_funsecret(mock_read_secret):
    """Without an explicit api_key, funai must ask funsecret for one.

    funsecret is mocked here so no real secret store lookup ever happens.
    """
    from funai.llm import Moonshot

    model = Moonshot()

    mock_read_secret.assert_called_once_with("funai", "moonshot", "api_key")
    assert model.model_name == "moonshot-v1-8k"


@patch("funai.llm.models.read_cache_secret", return_value="sk-fake-from-secret")
def test_deepseek_construction_falls_back_to_funsecret(mock_read_secret):
    from funai.llm import Deepseek

    model = Deepseek()

    mock_read_secret.assert_called_once_with("funai", "deepseek", "api_key")


def test_moonshot_fun_chat_with_mocked_completion():
    """fun_chat() must extract message content, with the HTTP call mocked out."""
    from funai.llm import Moonshot

    model = Moonshot(api_key="sk-fake-key")
    model.chat.completions.create = MagicMock(
        return_value=_fake_chat_completion("你好，我是 Moonshot")
    )

    result = model.fun_chat("你好")

    assert result == "你好，我是 Moonshot"
    model.chat.completions.create.assert_called_once()
    _, kwargs = model.chat.completions.create.call_args
    assert kwargs["model"] == "moonshot-v1-8k"
    assert kwargs["messages"] == [{"role": "user", "content": "你好"}]


def test_deepseek_fun_chat_with_mocked_completion():
    from funai.llm import Deepseek

    model = Deepseek(api_key="sk-fake-key")
    model.chat.completions.create = MagicMock(
        return_value=_fake_chat_completion("hello from deepseek")
    )

    result = model.fun_chat("hi")

    assert result == "hello from deepseek"


def test_fun_chat_strips_newlines():
    """fun_chat() replaces newlines in the returned content."""
    from funai.llm import Moonshot

    model = Moonshot(api_key="sk-fake-key")
    model.chat.completions.create = MagicMock(
        return_value=_fake_chat_completion("line1\nline2\nline3")
    )

    result = model.fun_chat("prompt")

    assert result == "line1line2line3"


def test_fun_chat_handles_empty_response():
    """fun_chat() must not raise when the client returns a falsy response."""
    from funai.llm import Moonshot

    model = Moonshot(api_key="sk-fake-key")
    model.chat.completions.create = MagicMock(return_value=None)

    result = model.fun_chat("prompt")

    assert result == ""


def test_get_model_moonshot():
    with patch("funai.llm.models.read_cache_secret", return_value="sk-fake"):
        from funai.llm import Moonshot, get_model

        model = get_model("moonshot", api_key="sk-fake-key")

        assert isinstance(model, Moonshot)


def test_get_model_deepseek():
    with patch("funai.llm.models.read_cache_secret", return_value="sk-fake"):
        from funai.llm import Deepseek, get_model

        model = get_model("deepseek", api_key="sk-fake-key")

        assert isinstance(model, Deepseek)


def test_get_model_unsupported_provider_returns_none():
    """Unknown providers just log an error and return None (no exception)."""
    from funai.llm import get_model

    result = get_model("unknown-provider")

    assert result is None


def test_base_module_is_empty():
    """`funai.llm.base` currently ships as an empty file.

    This is a pre-existing quirk of the repo (the real implementation lives
    in `funai.llm.models`), not something this smoke suite should fix. We
    just confirm it imports without error since it's part of the package.
    """
    import funai.llm.base as base_module

    assert base_module is not None


def test_no_cli_entry_point():
    """funai currently declares no [project.scripts] CLI entry point.

    Nothing to smoke-test here; documenting this explicitly instead of
    silently skipping a CLI check.
    """
    pytest.skip("funai 未在 pyproject.toml 中声明 [project.scripts]，无 CLI 可测试")
