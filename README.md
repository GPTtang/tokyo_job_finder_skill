# tokyo_job_finder Skill

[English](#english) | [中文](#中文) | [日本語](#日本語)

---

## English

A job-matching Skill for Claude Code and OpenClaw. Describe your background in natural language, and the skill fetches jobs from public sources, scores them against your profile, and returns a prioritized match report.

### What's special for Chinese speakers

- **Chinese advantage scoring** — jobs that explicitly seek Chinese/Mandarin speakers get a +0.15 bonus
- **Bridge SE detection** — offshore coordination roles (日中ブリッジSE) get an additional +0.10 bonus
- **JLPT mismatch penalty** — roles requiring higher Japanese than you have are deprioritized (−0.20)
- **35 curated sources** in `sources.example.json`: Chinese-owned IT firms in Japan, Chinese big-tech subsidiaries, Japanese offshore clients, and aggregator platforms
- **Inline badges** on each result: `[中国語優遇 | Bridge SE | 日語N2+]`

### Install

```bash
git clone https://github.com/GPTtang/tokyo_job_finder_skill ~/.claude/skills/tokyo_job_finder
cd ~/.claude/skills/tokyo_job_finder
pip install -e .
cp config/sources.example.json config/sources.json
```

**Optional: headless browser support** (for JS-rendered / SPA career pages)

```bash
pip install -e ".[browser]"
playwright install chromium
```

Required for `browser_site` provider. Without it, the skill falls back to static extraction with a warning.

### Use in Claude Code

Add the skill to your global Claude config so Claude Code can find `SKILL.md`:

```bash
echo '\n@~/.claude/skills/tokyo_job_finder/SKILL.md' >> ~/.claude/CLAUDE.md
```

Then just talk to Claude:

```
Find me backend / AI Engineer jobs in Tokyo.
I have Python, FastAPI, RAG, and 3 years of experience.
My Japanese is N2. I'm a native Chinese speaker. Prefer English-friendly companies.
```

Claude will invoke the skill automatically and return a ranked match report.

### Use in OpenClaw

In OpenClaw, mount the skill package by pointing to this directory:

1. Open **Settings → Skills → Add Skill**
2. Set path to `~/.claude/skills/tokyo_job_finder` (or wherever you cloned it)
3. OpenClaw reads `SKILL.md` and registers the skill

Then in any conversation, describe your job search and OpenClaw will trigger the skill:

```
帮我找东京的 AI 工程师职位，我有 Python 和 N2 日语，偏向华人友好或英语工作环境的公司。
```

### Source config

Edit `config/sources.json` to list the companies and job boards to search.

**Supported providers:**

| Provider | Required field | Description |
|---|---|---|
| `greenhouse` | `token` | Greenhouse ATS API |
| `lever` | `company` | Lever ATS API |
| `ashby` | `board` | Ashby ATS API |
| `company_site` | `url` | Static HTML + JSON-LD extraction |
| `browser_site` | `url` | Headless browser (Playwright) — use for SPAs |
| `japan_dev` | — | japan-dev.com aggregator |
| `gaijinpot` | — | GaijinPot Jobs aggregator |
| `tokyodev` | — | TokyoDev aggregator |

`browser_site` is the same as `company_site` but uses a headless Chromium browser to render the page before extracting data. Use it for React / Vue / Next.js / Nuxt career pages.

**Example:**

```json
{
  "sources": [
    {
      "provider": "gaijinpot",
      "filters": { "keywords": ["engineer", "Python"], "locations": ["Tokyo"] }
    },
    {
      "provider": "greenhouse",
      "token": "mercari",
      "filters": { "keywords": ["backend", "software"], "locations": ["Tokyo"] }
    },
    {
      "provider": "browser_site",
      "url": "https://careers.example-spa.com/",
      "filters": { "keywords": ["engineer"], "locations": ["Tokyo"] }
    },
    {
      "provider": "company_site",
      "url": "https://careers.linecorp.com/jobs/",
      "filters": { "keywords": ["engineer"], "locations": ["Tokyo"] }
    }
  ]
}
```

You can add human-readable section separators using `_` prefixed keys — they are ignored by the validator:

```json
{ "_section": "Priority 1 — Chinese-owned firms", "_label": "Bridge SE specialists" }
```

Filters are also derived automatically from your query — no manual config needed for basic use.

**Tip: let AI generate your sources list**

Paste this into Claude:

> I'm a backend engineer with Python and N2 Japanese, looking for Tokyo jobs at English-friendly or Chinese-friendly companies. Generate a `sources.json` for the tokyo_job_finder skill. Include `gaijinpot`, `tokyodev`, `greenhouse`, `lever`, and `ashby` entries for 5–8 relevant companies. Each source needs `provider`, optional `token`/`company`/`board`/`url`, and a `filters` object with `keywords` and `locations`.

Claude outputs a ready-to-use `config/sources.json` tailored to your profile.

---

## 中文

面向 Claude Code 和 OpenClaw 的求职匹配技能。用自然语言描述你的背景，技能自动抓取公开职位、与简历匹配评分，返回优先级排序的求职报告。

### 中文母语者专属加分机制

- **中文优势加分** — 明确优先招募中文母语者的职位额外 +0.15 分
- **Bridge SE 识别** — 日中离岸协调（ブリッジSE）岗位额外 +0.10 分
- **JLPT 不匹配扣分** — 日语要求高于你当前等级的职位降权（−0.20）
- **35 个精选职位源** — `sources.example.json` 内置：中国系 IT 乙方、中国大厂日本法人、日本甲方客户、聚合平台
- **行内标签** — 每个结果标注：`[中国語優遇 | Bridge SE | 日語N2+]`

### 安装

```bash
git clone https://github.com/GPTtang/tokyo_job_finder_skill ~/.claude/skills/tokyo_job_finder
cd ~/.claude/skills/tokyo_job_finder
pip install -e .
cp config/sources.example.json config/sources.json
```

**可选：无头浏览器支持**（用于 JS 渲染 / SPA 类招聘页）

```bash
pip install -e ".[browser]"
playwright install chromium
```

启用后可使用 `browser_site` provider。未安装时会自动降级为静态抓取并给出提示。

### 在 Claude Code 中使用

将技能加入全局 Claude 配置，让 Claude Code 能找到 `SKILL.md`：

```bash
echo '\n@~/.claude/skills/tokyo_job_finder/SKILL.md' >> ~/.claude/CLAUDE.md
```

之后直接和 Claude 说话即可：

```
帮我在东京找后端 / AI 工程师职位。
我有 Python、FastAPI、RAG 经验，工作经验 3 年。
日语 N2，中文母语，希望英语工作环境或华人友好的公司。
```

Claude 会自动调用技能，返回匹配排名报告。

### 在 OpenClaw 中使用

在 OpenClaw 里挂载技能包，指向本目录：

1. 打开 **设置 → 技能 → 添加技能**
2. 路径填 `~/.claude/skills/tokyo_job_finder`（或你 clone 的位置）
3. OpenClaw 读取 `SKILL.md` 后自动注册技能

之后在任何对话里描述求职需求，OpenClaw 会触发技能：

```
帮我找东京的 AI 工程师职位，我有 Python 和 N2 日语，
偏向华人友好或英语工作环境的公司，最多列出 5 个。
```

### 职位源配置

编辑 `config/sources.json`，填入要搜索的公司和招聘平台。

**支持的 provider：**

| Provider | 必填字段 | 说明 |
|---|---|---|
| `greenhouse` | `token` | Greenhouse ATS API |
| `lever` | `company` | Lever ATS API |
| `ashby` | `board` | Ashby ATS API |
| `company_site` | `url` | 静态 HTML + JSON-LD 提取 |
| `browser_site` | `url` | 无头浏览器（Playwright）— 适合 SPA 页面 |
| `japan_dev` | — | japan-dev.com 聚合平台 |
| `gaijinpot` | — | GaijinPot Jobs 聚合平台 |
| `tokyodev` | — | TokyoDev 聚合平台 |

`browser_site` 与 `company_site` 相同，但使用无头 Chromium 渲染页面后再提取。适合 React / Vue / Next.js / Nuxt 类招聘页面。

**示例：**

```json
{
  "sources": [
    {
      "_section": "聚合平台",
      "_label": "外国人向け求人サイト"
    },
    {
      "provider": "gaijinpot",
      "filters": { "keywords": ["engineer", "Python", "N2"], "locations": ["Tokyo"] }
    },
    {
      "provider": "greenhouse",
      "token": "bytedance",
      "filters": { "keywords": ["engineer", "backend"], "locations": ["Tokyo"] }
    },
    {
      "provider": "browser_site",
      "url": "https://careers.example-spa.com/",
      "filters": { "keywords": ["エンジニア", "engineer"] }
    }
  ]
}
```

`_section` / `_label` 等以 `_` 开头的字段是注释分隔符，验证器会自动跳过。

过滤条件也会从查询中自动提取，基本使用无需手动配置。

**技巧：让 AI 帮你生成 sources 列表**

把下面这段提示词发给 Claude：

> 我是有 Python 经验、日语 N2 的后端工程师，中文母语，想在东京找对华人或英语友好的技术岗位（特别是 Bridge SE / 中国系 IT 公司）。请帮我生成 tokyo_job_finder 技能的 `sources.json`，包含 `gaijinpot`、`tokyodev`、`greenhouse`、`lever`、`ashby`、`company_site` 等 provider，针对 5～8 家合适的公司。格式：每条 source 含 `provider`，可选 `token`/`company`/`board`/`url`，以及带 `keywords` 和 `locations` 的 `filters` 对象。

Claude 会直接输出一份针对你背景定制好的 `config/sources.json`，复制粘贴即可使用。

---

## 日本語

Claude Code・OpenClaw 向けの求人マッチングスキル。自然言語で経歴を伝えると、公開求人を自動取得してプロフィールとマッチングし、優先順位付きのレポートを返します。

### 中国語話者向け加点機能

- **中国語アドバンテージ加点** — 中国語・中文を優遇するポジションに +0.15
- **Bridge SE 検出** — 日中オフショア連携職（ブリッジSE）にさらに +0.10
- **JLPT ミスマッチペナルティ** — 候補者レベルより高い日本語要件の求人は降格（−0.20）
- **35 件の厳選ソース** — `sources.example.json` に同梱：中国系 IT 乙方、中国大手 IT の日本法人、日本甲方クライアント、求人アグリゲーター
- **インラインバッジ** — 各結果に表示：`[中国語優遇 | Bridge SE | 日語N2+]`

### インストール

```bash
git clone https://github.com/GPTtang/tokyo_job_finder_skill ~/.claude/skills/tokyo_job_finder
cd ~/.claude/skills/tokyo_job_finder
pip install -e .
cp config/sources.example.json config/sources.json
```

**オプション：ヘッドレスブラウザサポート**（JS レンダリング / SPA 対応）

```bash
pip install -e ".[browser]"
playwright install chromium
```

`browser_site` プロバイダーに必要です。未インストール時は静的取得にフォールバックし、警告を出します。

### Claude Code での使い方

`SKILL.md` を Claude Code が読めるよう、グローバル設定に追加します：

```bash
echo '\n@~/.claude/skills/tokyo_job_finder/SKILL.md' >> ~/.claude/CLAUDE.md
```

あとは Claude に話しかけるだけです：

```
東京でバックエンド・AI エンジニアの求人を探してください。
Python・FastAPI・RAG の経験が 3 年あります。
日本語は N2、中国語ネイティブで、英語環境または中国語対応の会社を希望します。
```

Claude がスキルを自動で呼び出し、マッチング結果を返します。

### OpenClaw での使い方

OpenClaw でスキルパッケージをマウントします：

1. **設定 → スキル → スキルを追加** を開く
2. パスに `~/.claude/skills/tokyo_job_finder`（またはクローン先）を指定
3. OpenClaw が `SKILL.md` を読み込んでスキルを登録

あとは会話で求職条件を伝えるだけで、スキルが起動します：

```
東京で AI エンジニアの求人を探してください。
Python・N2 日本語スキルがあり、英語環境か中国語対応の会社を希望します。
上位 5 件をリストアップしてください。
```

### 求人ソース設定

`config/sources.json` を編集して、検索対象の企業や求人プラットフォームを追加します。

**対応 provider：**

| Provider | 必須フィールド | 説明 |
|---|---|---|
| `greenhouse` | `token` | Greenhouse ATS API |
| `lever` | `company` | Lever ATS API |
| `ashby` | `board` | Ashby ATS API |
| `company_site` | `url` | 静的 HTML + JSON-LD 抽出 |
| `browser_site` | `url` | ヘッドレスブラウザ（Playwright）— SPA 向け |
| `japan_dev` | — | japan-dev.com アグリゲーター |
| `gaijinpot` | — | GaijinPot Jobs アグリゲーター |
| `tokyodev` | — | TokyoDev アグリゲーター |

**設定例：**

```json
{
  "sources": [
    {
      "_section": "アグリゲーター",
      "_label": "外国人向け求人サイト"
    },
    {
      "provider": "gaijinpot",
      "filters": { "keywords": ["engineer", "Python", "N2"], "locations": ["Tokyo"] }
    },
    {
      "provider": "greenhouse",
      "token": "mercari",
      "filters": { "keywords": ["backend", "software"], "locations": ["Tokyo"] }
    },
    {
      "provider": "browser_site",
      "url": "https://careers.example-spa.com/",
      "filters": { "keywords": ["エンジニア", "engineer"], "locations": ["Tokyo"] }
    }
  ]
}
```

`_section` / `_label` などの `_` 始まりのキーはコメント用セパレーターとして扱われ、バリデーターにより自動スキップされます。

フィルターはクエリから自動抽出されるため、基本的な用途では手動設定不要です。

**ヒント：AI に sources リストを生成させる**

Claude に以下のプロンプトを送るだけで OK：

> Python スキルと日本語 N2（中国語ネイティブ）を持つバックエンドエンジニアとして、東京で英語または中国語対応の技術職（特に Bridge SE・中国系 IT 企業）を探しています。tokyo_job_finder スキル用の `sources.json` を生成してください。`gaijinpot`、`tokyodev`、`greenhouse`、`lever`、`ashby`、`browser_site` を組み合わせ、5〜8 社を対象にしてください。各 source に `provider`、任意で `token`/`company`/`board`/`url`、`keywords` と `locations` を含む `filters` オブジェクトを含めてください。

Claude がそのまま使える `config/sources.json` を出力してくれます。
