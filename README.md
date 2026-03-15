# job_finder Skill

[English](#english) | [中文](#中文) | [日本語](#日本語)

---

## English

`job_finder` is a single-run job-matching Skill for OpenClaw / Claude Code style workflows.

It takes a natural-language job search request, fetches jobs from configured public sources, ranks them against the user's profile, and returns a compact report.

### What this package is
- one Skill
- no database
- no persistent storage
- no SaaS backend
- no background workers

### Typical use case
- find AI / LLM / backend jobs in Japan
- compare jobs against a resume or self-description
- produce an application priority list

### Package layout
- `SKILL.md` — Skill contract
- `job_finder/` — implementation
- `config/sources.example.json` — example job sources
- `examples/` — runnable examples
- `docs/` — design and integration notes

### Quick start
```bash
python examples/demo_run.py
```

Or in Python:

```python
from job_finder.skill import job_finder

query = """
I live in Japan and want Tokyo or remote AI Engineer / LLM Engineer roles.
I have Python, FastAPI, RAG, vector search, and AI agent experience.
My Japanese is intermediate.
Find the best matching jobs for me.
"""

print(job_finder(query, top_n=5, config_path="config/sources.json"))
```

### Config
```bash
cp config/sources.example.json config/sources.json
```

Then replace the example company / board values with the public sources you want to search.

### Fetch tuning
`config/sources.example.json` supports runtime fetch options:

- `timeout_seconds`
- `max_retries`
- `retry_backoff_seconds`
- `max_follow_links`

### CLI
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

After editable install:
```bash
job-finder --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

### JSON output
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

### Provider-level filters
Each source can define pre-filters:

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

### Automatic provider filters
The Skill derives provider filters from the user's query:
- role names → provider keywords
- detected skills → provider keywords
- detected locations → provider location filters
- remote preference → `remote_only` or `remote_preferred`

### Notes
This package is intentionally small and ephemeral. It favors clear matching output over system complexity.

---

## 中文

`job_finder` 是一个为 OpenClaw / Claude Code 工作流设计的一次性职位匹配技能（Skill）。

它接收自然语言的求职请求，从配置的公开职位源抓取职位，与用户简历进行匹配评分，并返回简洁的报告。

### 功能特点
- 单一技能，职责清晰
- 无数据库
- 无持久化存储
- 无 SaaS 后端
- 无后台工作进程

### 典型使用场景
- 在日本寻找 AI / LLM / 后端开发职位
- 将职位与简历或自我描述进行比较
- 生成求职优先级列表

### 项目结构
- `SKILL.md` — Skill 契约文件
- `job_finder/` — 核心实现
- `config/sources.example.json` — 职位源配置示例
- `examples/` — 可运行示例
- `docs/` — 设计文档与集成说明

### 快速开始
```bash
python examples/demo_run.py
```

或在 Python 中使用：

```python
from job_finder.skill import job_finder

query = """
我住在日本，希望找东京或远程的 AI 工程师 / LLM 工程师职位。
我有 Python、FastAPI、RAG、向量检索和 AI Agent 开发经验。
我的日语水平为中级。
请为我找出最匹配的职位。
"""

print(job_finder(query, top_n=5, config_path="config/sources.json"))
```

### 配置
```bash
cp config/sources.example.json config/sources.json
```

将示例中的公司和职位板块替换为你想搜索的公开来源。

### 抓取参数调优
`config/sources.example.json` 支持以下运行时抓取选项：

- `timeout_seconds` — 超时时间（秒）
- `max_retries` — 最大重试次数
- `retry_backoff_seconds` — 重试退避时间（秒）
- `max_follow_links` — 最大链接跟踪数

### 命令行使用
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

安装后直接使用：
```bash
job-finder --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

### JSON 输出
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

### 提供商级别过滤器
每个职位源可配置预过滤条件：

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

### 自动过滤器
Skill 会自动从用户查询中提取过滤条件：
- 职位名称 → 关键词过滤
- 检测到的技能 → 关键词过滤
- 检测到的地点 → 地点过滤
- 远程偏好 → `remote_only` 或 `remote_preferred`

### 说明
本项目有意保持轻量和简洁，优先追求清晰的匹配输出，而非系统复杂性。

---

## 日本語

`job_finder` は OpenClaw / Claude Code スタイルのワークフロー向けに設計された、単発実行型の求人マッチングスキルです。

自然言語の求職リクエストを受け取り、設定済みの公開求人ソースから求人情報を取得し、ユーザーのプロフィールとマッチングスコアを計算して、コンパクトなレポートを返します。

### 特徴
- 単一スキル、シンプルな責務
- データベース不要
- 永続ストレージ不要
- SaaS バックエンド不要
- バックグラウンドワーカー不要

### 主な用途
- 日本国内の AI / LLM / バックエンド求人を探す
- 履歴書や自己紹介と求人を比較する
- 応募優先リストを作成する

### パッケージ構成
- `SKILL.md` — スキル仕様書
- `job_finder/` — 実装コード
- `config/sources.example.json` — 求人ソース設定例
- `examples/` — 実行可能なサンプル
- `docs/` — 設計資料・統合ガイド

### クイックスタート
```bash
python examples/demo_run.py
```

Python コードから使用する場合：

```python
from job_finder.skill import job_finder

query = """
日本在住で、東京またはリモートの AI エンジニア / LLM エンジニアポジションを探しています。
Python、FastAPI、RAG、ベクトル検索、AI エージェント開発の経験があります。
日本語は中級レベルです。
最もマッチする求人を見つけてください。
"""

print(job_finder(query, top_n=5, config_path="config/sources.json"))
```

### 設定
```bash
cp config/sources.example.json config/sources.json
```

サンプル内の企業・求人ボードの値を、検索したい公開ソースに置き換えてください。

### フェッチパラメータの調整
`config/sources.example.json` は以下の実行時オプションに対応しています：

- `timeout_seconds` — タイムアウト時間（秒）
- `max_retries` — 最大リトライ回数
- `retry_backoff_seconds` — リトライ待機時間（秒）
- `max_follow_links` — 最大リンク追跡数

### CLI 使用方法
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

インストール後はコマンドとして直接実行可能：
```bash
job-finder --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

### JSON 出力
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

### プロバイダーレベルのフィルター
各求人ソースに事前フィルターを設定できます：

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

### 自動フィルター
スキルはユーザーのクエリから自動的にフィルター条件を抽出します：
- 職種名 → プロバイダーキーワード
- 検出されたスキル → プロバイダーキーワード
- 検出された場所 → 場所フィルター
- リモート希望 → `remote_only` または `remote_preferred`

### 備考
このパッケージは意図的にシンプルかつ軽量に設計されています。システムの複雑さよりも、明確なマッチング出力を優先しています。
