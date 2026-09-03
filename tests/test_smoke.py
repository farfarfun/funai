"""funai 的冒烟测试。

funai 是对 OpenAI 兼容接口的大语言模型（Moonshot/DeepSeek）做的薄封装。
这些测试不发起任何真实网络请求，也不做任何真实的密钥读取：

- 所有对 OpenAI 兼容 `chat.completions.create` 的调用都被 mock 掉。
- 所有对 `funsecret.secret.read_cache_secret` 的调用都被 mock 掉，
  不会真的去本地/远程密钥存储里读取密钥。

这只是一套冒烟测试：验证包能正常导入，且核心公开类/函数在依赖被 mock 的
情况下行为符合预期，不验证真实的 LLM 效果。
"""

from unittest.mock import MagicMock, patch

import pytest


def _fake_chat_completion(content="hello world"):
    """构造一个真实的 ChatCompletion 实例（fun_chat 里有 isinstance 检查）。"""
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
    """顶层 `funai` 包必须能正常导入。"""
    import funai  # noqa: F401


def test_import_llm_submodule():
    """`funai.llm` 必须能正常导入并暴露文档里承诺的公开 API。"""
    from funai import llm

    assert hasattr(llm, "get_model")
    assert hasattr(llm, "Moonshot")
    assert hasattr(llm, "Deepseek")
    assert hasattr(llm, "UnsupportedProviderError")
    assert set(llm.__all__) == {
        "get_model",
        "Deepseek",
        "Moonshot",
        "UnsupportedProviderError",
    }


def test_import_models_submodule():
    """`funai.llm.models` 必须能正常导入并暴露核心类/函数。"""
    from funai.llm import models

    assert hasattr(models, "BaseModel")
    assert hasattr(models, "Moonshot")
    assert hasattr(models, "Deepseek")
    assert hasattr(models, "get_model")
    assert hasattr(models, "UnsupportedProviderError")


@patch("funai.llm.models.read_cache_secret")
def test_moonshot_construction_with_explicit_api_key(mock_read_secret):
    """显式传入 api_key 构造 Moonshot 时，不应该触碰 funsecret。"""
    from funai.llm import Moonshot

    model = Moonshot(api_key="sk-fake-key")

    assert model.model_name == "moonshot-v1-8k"
    assert model.llm_provider == "moonshot"
    assert model.base_url is not None
    mock_read_secret.assert_not_called()


@patch("funai.llm.models.read_cache_secret")
def test_deepseek_construction_with_explicit_api_key(mock_read_secret):
    """显式传入 api_key 构造 Deepseek 时，不应该触碰 funsecret。"""
    from funai.llm import Deepseek

    model = Deepseek(api_key="sk-fake-key")

    assert model.model_name == "deepseek-chat"
    assert model.llm_provider == "deepseek"
    mock_read_secret.assert_not_called()


@patch("funai.llm.models.read_cache_secret", return_value="sk-fake-from-secret")
def test_moonshot_construction_falls_back_to_funsecret(mock_read_secret):
    """不传 api_key 时，funai 必须向 funsecret 请求一个。

    funsecret 在这里被 mock 掉，不会发生真实的密钥存储读取。
    """
    from funai.llm import Moonshot

    model = Moonshot()

    mock_read_secret.assert_called_once_with("funai", "moonshot", "api_key")
    assert model.model_name == "moonshot-v1-8k"


@patch("funai.llm.models.read_cache_secret", return_value="sk-fake-from-secret")
def test_deepseek_construction_falls_back_to_funsecret(mock_read_secret):
    """不传 api_key 时，funai 必须向 funsecret 请求一个。"""
    from funai.llm import Deepseek

    model = Deepseek()

    mock_read_secret.assert_called_once_with("funai", "deepseek", "api_key")


def test_moonshot_fun_chat_with_mocked_completion():
    """fun_chat() 必须在 HTTP 调用被 mock 的情况下正确提取回复内容。"""
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
    """fun_chat() 对 Deepseek 同样应正确提取回复内容。"""
    from funai.llm import Deepseek

    model = Deepseek(api_key="sk-fake-key")
    model.chat.completions.create = MagicMock(
        return_value=_fake_chat_completion("hello from deepseek")
    )

    result = model.fun_chat("hi")

    assert result == "hello from deepseek"


def test_fun_chat_strips_newlines():
    """fun_chat() 应去除返回内容里的换行符。"""
    from funai.llm import Moonshot

    model = Moonshot(api_key="sk-fake-key")
    model.chat.completions.create = MagicMock(
        return_value=_fake_chat_completion("line1\nline2\nline3")
    )

    result = model.fun_chat("prompt")

    assert result == "line1line2line3"


def test_fun_chat_handles_empty_response():
    """fun_chat() 在客户端返回假值（如 None）时不应抛异常，返回空字符串。"""
    from funai.llm import Moonshot

    model = Moonshot(api_key="sk-fake-key")
    model.chat.completions.create = MagicMock(return_value=None)

    result = model.fun_chat("prompt")

    assert result == ""


def test_get_model_moonshot():
    """get_model("moonshot") 应返回 Moonshot 实例。"""
    with patch("funai.llm.models.read_cache_secret", return_value="sk-fake"):
        from funai.llm import Moonshot, get_model

        model = get_model("moonshot", api_key="sk-fake-key")

        assert isinstance(model, Moonshot)


def test_get_model_deepseek():
    """get_model("deepseek") 应返回 Deepseek 实例。"""
    with patch("funai.llm.models.read_cache_secret", return_value="sk-fake"):
        from funai.llm import Deepseek, get_model

        model = get_model("deepseek", api_key="sk-fake-key")

        assert isinstance(model, Deepseek)


def test_get_model_unsupported_provider_raises():
    """未知 provider 必须抛出 UnsupportedProviderError，而不是静默返回 None。"""
    from funai.llm import UnsupportedProviderError, get_model

    with pytest.raises(UnsupportedProviderError) as exc_info:
        get_model("unknown-provider")

    assert exc_info.value.provider == "unknown-provider"


def test_base_module_is_empty():
    """`funai.llm.base` 目前是空文件。

    这是仓库里已有的历史遗留（真实实现都在 `funai.llm.models` 里），不属于
    本次冒烟测试要修复的范围，这里只确认它作为包的一部分能正常导入。
    """
    import funai.llm.base as base_module

    assert base_module is not None


def test_no_cli_entry_point():
    """funai 目前没有声明 `[project.scripts]` CLI 入口。

    没有可测的 CLI，这里显式记录这一点，而不是悄悄跳过。
    """
    pytest.skip("funai 未在 pyproject.toml 中声明 [project.scripts]，无 CLI 可测试")
