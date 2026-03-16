# job_finder Skill

[English](#english) | [中文](#中文) | [日本語](#日本語)

---

## English

A job-matching Skill for Claude Code workflows. Takes a natural-language query, fetches jobs from public sources, ranks them against your profile, and returns a prioritized report.

### Quick start

```bash
cp config/sources.example.json config/sources.json
python examples/demo_run.py
```

Or in Python:

```python
from job_finder.skill import job_finder

result = job_finder(
    "Find me AI Engineer roles in Tokyo. I have Python, FastAPI, and RAG experience.",
    top_n=5,
    config_path="config/sources.json"
)
print(result)
```

### CLI

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

JSON output:

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

### Source config

`config/sources.json` is **gitignored** — your personal sources are never committed. Copy the template to get started:

```bash
cp config/sources.example.json config/sources.json
```

Edit `config/sources.json` to add job sources. Each source supports optional filters:

```json
{
  "provider": "greenhouse",
  "token": "openai",
  "filters": {
    "keywords": ["AI", "LLM"],
    "locations": ["Tokyo"],
    "remote_preferred": true
  }
}
```

Filters are also derived automatically from your query — no manual config needed for basic use.

---

## 中文

面向 Claude Code 工作流的求职匹配技能。输入自然语言求职需求，自动抓取公开职位，与你的简历匹配评分，返回优先级排序报告。

### 快速开始

```bash
cp config/sources.example.json config/sources.json
python examples/demo_run.py
```

或在 Python 中调用：

```python
from job_finder.skill import job_finder

result = job_finder(
    "帮我在东京找 AI 工程师职位，我有 Python、FastAPI 和 RAG 经验。",
    top_n=5,
    config_path="config/sources.json"
)
print(result)
```

### 命令行

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

JSON 输出：

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

### 职位源配置

`config/sources.json` **不纳入版本控制**，你的个人配置不会被提交。先复制模板：

```bash
cp config/sources.example.json config/sources.json
```

编辑 `config/sources.json` 添加职位来源，每个来源支持可选过滤条件：

```json
{
  "provider": "greenhouse",
  "token": "openai",
  "filters": {
    "keywords": ["AI", "LLM"],
    "locations": ["Tokyo"],
    "remote_preferred": true
  }
}
```

过滤条件也会从你的查询中自动提取，基本使用无需手动配置。

---

## 日本語

Claude Code ワークフロー向けの求人マッチングスキル。自然言語で求職条件を入力すると、公開求人を自動取得し、プロフィールとマッチングして優先順位付きレポートを返します。

### クイックスタート

```bash
cp config/sources.example.json config/sources.json
python examples/demo_run.py
```

Python から使用：

```python
from job_finder.skill import job_finder

result = job_finder(
    "東京で AI エンジニアのポジションを探してください。Python、FastAPI、RAG の経験があります。",
    top_n=5,
    config_path="config/sources.json"
)
print(result)
```

### CLI

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

JSON 出力：

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

### 求人ソース設定

`config/sources.json` は **gitignore 対象**のため、個人設定がコミットされることはありません。まずテンプレートをコピーしてください：

```bash
cp config/sources.example.json config/sources.json
```

`config/sources.json` を編集して求人ソースを追加。各ソースにフィルターを設定できます：

```json
{
  "provider": "greenhouse",
  "token": "openai",
  "filters": {
    "keywords": ["AI", "LLM"],
    "locations": ["Tokyo"],
    "remote_preferred": true
  }
}
```

フィルターはクエリから自動抽出されるため、基本的な用途では手動設定不要です。
