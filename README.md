# funai

对 OpenAI 兼容接口的大语言模型做了一层薄封装，目前内置了 Moonshot（月之暗面）和 DeepSeek 两个 provider，API Key 通过 [funsecret](https://github.com/farfarfun/funsecret) 统一管理。

## 安装

需要 Python 3.10 或更高版本。

```bash
pip install funai
```

## 快速开始

`funai` 默认通过 `funsecret` 读取本机保存的 API Key。以下示例使用
DeepSeek；请将尖括号中的内容替换为你自己的真实 API Key：

```bash
funsecret write "<your-deepseek-api-key>" funai deepseek api_key
```

```python
from funai.llm import get_model

model = get_model("deepseek")
answer = model.fun_chat("你好，介绍一下你自己")
```

使用 Moonshot 时，写入对应 provider 的 Key：

```bash
funsecret write "<your-moonshot-api-key>" funai moonshot api_key
```

也可以直接实例化具体的 provider：

```python
from funai.llm import Deepseek, Moonshot

model = Deepseek(api_key="<your-deepseek-api-key>", model_name="deepseek-chat")
# 不传 api_key 时会用 funsecret 从本地缓存读取 "funai"/"deepseek"/"api_key"
answer = model.fun_chat("讲个笑话")
```

- `Moonshot`：默认 `model_name="moonshot-v1-8k"`，`base_url="https://api.moonshot.cn/v1"`
- `Deepseek`：默认 `model_name="deepseek-chat"`，`base_url="https://api.deepseek.com"`

两者都继承自 `funai.llm.models.BaseModel`（本质是 `openai.OpenAI` 客户端的子类）。`fun_chat()` 是对 `chat.completions.create` 的简单封装：传入 prompt（或自定义 `messages`），直接返回模型回复的文本内容。

传入不支持的 provider 时，`get_model()` 会抛出 `funai.llm.UnsupportedProviderError`。

## 构建与发布

开发环境安装依赖后，使用组织统一的 `funbuild` 管理版本递增、构建、安装校验和发布：

```bash
uv sync --group dev
funbuild install  # 仅构建并安装校验，不发布
funbuild build    # 完整发布流程：递增版本、构建、安装校验、发布、提交并打标签
```

发布前还应运行 `uv run ruff check .`、`uv run ruff format --check .` 与
`uv run pytest -q`，并更新 `CHANGELOG.md`。`funbuild build` 会修改版本并推送提交与标签，
仅应在准备正式发布时执行。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
