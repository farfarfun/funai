# Changelog

本项目的版本记录遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 风格。

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
