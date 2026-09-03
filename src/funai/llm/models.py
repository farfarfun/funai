from farlog import getLogger
from funsecret.secret import read_cache_secret
from openai import OpenAI
from openai.types.chat import ChatCompletion

logger = getLogger("funai")


class UnsupportedProviderError(ValueError):
    """请求了未注册的 LLM provider 时抛出。"""

    def __init__(self, provider: str):
        self.provider = provider
        super().__init__(
            f'unsupported provider: "{provider}", 目前仅支持 "moonshot"、"deepseek"'
        )


class BaseModel(OpenAI):
    """对 OpenAI 兼容 Chat Completions 接口的薄封装。

    子类通过设置 `llm_provider` 标识具体服务商，并在构造函数里传入对应的
    `api_key`、`model_name`、`base_url`。
    """

    llm_provider: str = "openai"

    def __init__(self, api_key: str, model_name: str, *args, **kwargs):
        """初始化模型客户端。

        Args:
            api_key: 服务商 API Key。
            model_name: 具体的模型名称，如 `"deepseek-chat"`。
            *args: 透传给 `openai.OpenAI` 的位置参数。
            **kwargs: 透传给 `openai.OpenAI` 的关键字参数（如 `base_url`）。
        """
        super().__init__(api_key=api_key, *args, **kwargs)
        self.model_name: str = model_name

    def fun_chat(
        self,
        prompt: str,
        messages: list[dict[str, str]] | None = None,
        *args,
        **kwargs,
    ) -> str:
        """发起一次对话补全，返回模型回复的纯文本内容。

        Args:
            prompt: 用户提问文本；当 `messages` 未提供时，会被包装成
                `[{"role": "user", "content": prompt}]`。
            messages: 完整的对话消息列表，提供时优先于 `prompt`。
            *args: 透传给 `chat.completions.create` 的位置参数。
            **kwargs: 透传给 `chat.completions.create` 的关键字参数。

        Returns:
            模型回复文本（已去除换行符）；请求返回空响应或非预期类型时返回空字符串。
        """
        response = self.chat.completions.create(
            model=self.model_name,
            messages=messages or [{"role": "user", "content": prompt}],
            *args,
            **kwargs,
        )
        content = ""
        if response:
            if isinstance(response, ChatCompletion):
                content = response.choices[0].message.content
            else:
                logger.error(
                    f'[{self.llm_provider}] returned an invalid response: "{response}", please check your network '
                    f"connection and try again."
                )
        else:
            logger.error(
                f"[{self.llm_provider}] returned an empty response, please check your network connection and try again."
            )
        return content.replace("\n", "")


class Moonshot(BaseModel):
    """月之暗面（Moonshot AI）模型封装。"""

    llm_provider = "moonshot"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "moonshot-v1-8k",
        base_url: str = "https://api.moonshot.cn/v1",
        *args,
        **kwargs,
    ):
        """初始化 Moonshot 客户端。

        Args:
            api_key: Moonshot API Key；为空时通过 `funsecret` 从本地缓存读取
                `("funai", "moonshot", "api_key")`。
            model_name: 模型名称，默认 `"moonshot-v1-8k"`。
            base_url: 接口地址，默认官方 `https://api.moonshot.cn/v1`。
        """
        api_key = api_key or read_cache_secret("funai", "moonshot", "api_key")
        super().__init__(
            api_key=api_key, model_name=model_name, base_url=base_url, *args, **kwargs
        )


class Deepseek(BaseModel):
    """DeepSeek 模型封装。"""

    llm_provider = "deepseek"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        *args,
        **kwargs,
    ):
        """初始化 DeepSeek 客户端。

        Args:
            api_key: DeepSeek API Key；为空时通过 `funsecret` 从本地缓存读取
                `("funai", "deepseek", "api_key")`。
            model_name: 模型名称，默认 `"deepseek-chat"`。
            base_url: 接口地址，默认官方 `https://api.deepseek.com`。
        """
        api_key = api_key or read_cache_secret("funai", "deepseek", "api_key")
        super().__init__(
            api_key=api_key, model_name=model_name, base_url=base_url, *args, **kwargs
        )


def get_model(provider: str, api_key: str | None = None) -> OpenAI:
    """按 provider 名称构造对应的模型客户端。

    Args:
        provider: 服务商标识，目前支持 `"moonshot"`、`"deepseek"`。
        api_key: 对应服务商的 API Key；为空时由具体 provider 从 `funsecret` 读取。

    Returns:
        对应 provider 的模型客户端实例。

    Raises:
        UnsupportedProviderError: `provider` 不在受支持列表中时抛出。
    """
    if provider == "moonshot":
        return Moonshot(api_key=api_key)
    elif provider == "deepseek":
        return Deepseek(api_key=api_key)
    else:
        raise UnsupportedProviderError(provider)
