# Changelog

本项目的版本记录遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 风格。

## [1.0.12]

### 新增

- `tests/` 补充畸形响应的边界用例：非 `ChatCompletion` 类型（dict / 字符串 / 任意对象）、空 `choices`、`content=None`、`content=""`、多候选项取首个
- `pyproject.toml` 增加 `[tool.ruff]` / `[tool.ruff.lint]` 配置（`target-version = "py310"`，启用 `E`/`F`/`I`/`UP`/`B`/`SIM`/`RUF`）
- 新增 `.github/workflows/ci.yml`，push / PR 时执行 `ruff check`、`ruff format --check` 与 `pytest`

### 修复

- `fun_chat()` 对响应的边界判定改为逐情形处理：响应为空、类型非 `ChatCompletion`、`choices` 为空、`message.content` 为 `None` 时分别记录错误日志并返回空字符串，不会再出现 `IndexError`/`AttributeError`

### 变更

- `pyproject.toml` 的 `description` 由占位值 `"funai"` 改为真实功能描述（PyPI 摘要下次发版后生效）

### 废弃

- 无

## [1.0.11]

### 新增

- 无

### 修复

- `get_model()` 遇到不支持的 provider 时改为抛出 `UnsupportedProviderError`（此前仅记录错误日志并静默返回 `None`）

### 变更

- 日志入口从 `funutil.getLogger` 改为组织统一的 `farlog.getLogger`，同步移除 `funutil` 依赖
- `pyproject.toml` 显式声明 `license = "MIT"` 与 `license-files = ["LICENSE"]`
- `BaseModel`/`Moonshot`/`Deepseek`/`get_model` 补充完整类型标注与中文 docstring

### 废弃

- 无

## [1.0.10]

### 新增

- Moonshot、DeepSeek 两个 provider 的基础封装

### 修复

- 无

### 变更

- 无

### 废弃

- 无
