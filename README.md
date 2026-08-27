# funai

对 OpenAI 兼容接口的大语言模型做了一层薄封装，目前内置了 Moonshot（月之暗面）和 DeepSeek 两个 provider，API Key 通过 [funsecret](https://github.com/farfarfun/funsecret) 统一管理。

## 安装

```bash
pip install funai
```

## 用法示例

```python
from funai.llm import get_model

model = get_model("deepseek")  # 或 "moonshot"
answer = model.fun_chat("你好，介绍一下你自己")
```

也可以直接实例化具体的 provider：

```python
from funai.llm import Deepseek, Moonshot

model = Deepseek(api_key="sk-xxx", model_name="deepseek-chat")
# 不传 api_key 时会用 funsecret 从本地缓存读取 "funai"/"deepseek"/"api_key"
answer = model.fun_chat("讲个笑话")
```

- `Moonshot`：默认 `model_name="moonshot-v1-8k"`，`base_url="https://api.moonshot.cn/v1"`
- `Deepseek`：默认 `model_name="deepseek-chat"`，`base_url="https://api.deepseek.com"`

两者都继承自 `funai.llm.models.BaseModel`（本质是 `openai.OpenAI` 客户端的子类）。`fun_chat()` 是对 `chat.completions.create` 的简单封装：传入 prompt（或自定义 `messages`），直接返回模型回复的文本内容。
