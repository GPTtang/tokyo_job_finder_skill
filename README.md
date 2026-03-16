# tokyo_job_finder Skill

[English](#english) | [中文](#中文) | [日本語](#日本語)

---

## English

A job-matching Skill for Claude Code and OpenClaw. Describe your background in natural language, and the skill fetches jobs from public sources, scores them against your profile, and returns a prioritized match report.

### Install

```bash
git clone https://github.com/GPTtang/tokyo_job_finder_skill ~/.claude/skills/tokyo_job_finder
cd ~/.claude/skills/tokyo_job_finder
pip install -e .
cp config/sources.example.json config/sources.json
```

### Use in Claude Code

Add the skill to your project or global Claude config so Claude Code can find `SKILL.md`:

```bash
# Add to global skills (available in any project)
echo '\n@~/.claude/skills/tokyo_job_finder/SKILL.md' >> ~/.claude/CLAUDE.md
```

Then just talk to Claude:

```
Find me backend / AI Engineer jobs in Tokyo.
I have Python, FastAPI, RAG, and 3 years of experience.
My Japanese is N2. Prefer English-friendly companies.
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

Edit `config/sources.json` to list the companies and job boards to search. Supported providers: `greenhouse`, `lever`, `ashby`, `gaijinpot`, `tokyodev`, `japan_dev`, `company_site`.

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
      "provider": "lever",
      "company": "smartnews",
      "filters": { "locations": ["Tokyo", "Remote"] }
    },
    {
      "provider": "company_site",
      "url": "https://careers.linecorp.com/jobs/",
      "filters": { "keywords": ["engineer"], "locations": ["Tokyo"] }
    }
  ]
}
```

Filters are also derived automatically from your query — no manual config needed for basic use.

**Tip: let AI generate your sources list**

Paste this into Claude:

> I'm a backend engineer with Python and N2 Japanese, looking for Tokyo jobs at English-friendly or Chinese-friendly companies. Generate a `sources.json` for the tokyo_job_finder skill. Include `gaijinpot`, `tokyodev`, `greenhouse`, `lever`, and `ashby` entries for 5–8 relevant companies. Each source needs `provider`, optional `token`/`company`/`board`/`url`, and a `filters` object with `keywords` and `locations`.

Claude outputs a ready-to-use `config/sources.json` tailored to your profile.

---

## 中文

面向 Claude Code 和 OpenClaw 的求职匹配技能。用自然语言描述你的背景，技能自动抓取公开职位、与简历匹配评分，返回优先级排序的求职报告。

### 安装

```bash
git clone https://github.com/GPTtang/tokyo_job_finder_skill ~/.claude/skills/tokyo_job_finder
cd ~/.claude/skills/tokyo_job_finder
pip install -e .
cp config/sources.example.json config/sources.json
```

### 在 Claude Code 中使用

将技能加入全局 Claude 配置，让 Claude Code 能找到 `SKILL.md`：

```bash
echo '\n@~/.claude/skills/tokyo_job_finder/SKILL.md' >> ~/.claude/CLAUDE.md
```

之后直接和 Claude 说话即可：

```
帮我在东京找后端 / AI 工程师职位。
我有 Python、FastAPI、RAG 经验，工作经验 3 年。
日语 N2，希望英语工作环境或华人友好的公司。
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

编辑 `config/sources.json`，填入要搜索的公司和招聘平台。支持的 provider：`greenhouse`、`lever`、`ashby`、`gaijinpot`、`tokyodev`、`japan_dev`、`company_site`。

**示例：**

```json
{
  "sources": [
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
      "provider": "lever",
      "company": "mercari",
      "filters": { "locations": ["Tokyo", "Remote"] }
    },
    {
      "provider": "company_site",
      "url": "https://careers.linecorp.com/jobs/",
      "filters": { "keywords": ["エンジニア", "engineer"], "locations": ["Tokyo"] }
    }
  ]
}
```

过滤条件也会从查询中自动提取，基本使用无需手动配置。

**技巧：让 AI 帮你生成 sources 列表**

把下面这段提示词发给 Claude：

> 我是有 Python 经验、日语 N2 的后端工程师，想在东京找对华人或英语友好的技术岗位。请帮我生成 tokyo_job_finder 技能的 `sources.json`，包含 `gaijinpot`、`tokyodev`、`greenhouse`、`lever`、`ashby` 等 provider，针对 5～8 家合适的公司。格式：每条 source 含 `provider`，可选 `token`/`company`/`board`/`url`，以及带 `keywords` 和 `locations` 的 `filters` 对象。

Claude 会直接输出一份针对你背景定制好的 `config/sources.json`，复制粘贴即可使用。

---

## 日本語

Claude Code・OpenClaw 向けの求人マッチングスキル。自然言語で経歴を伝えると、公開求人を自動取得してプロフィールとマッチングし、優先順位付きのレポートを返します。

### インストール

```bash
git clone https://github.com/GPTtang/tokyo_job_finder_skill ~/.claude/skills/tokyo_job_finder
cd ~/.claude/skills/tokyo_job_finder
pip install -e .
cp config/sources.example.json config/sources.json
```

### Claude Code での使い方

`SKILL.md` を Claude Code が読めるよう、グローバル設定に追加します：

```bash
echo '\n@~/.claude/skills/tokyo_job_finder/SKILL.md' >> ~/.claude/CLAUDE.md
```

あとは Claude に話しかけるだけです：

```
東京でバックエンド・AI エンジニアの求人を探してください。
Python・FastAPI・RAG の経験が 3 年あります。
日本語は N2 で、英語環境または中国語対応の会社を希望します。
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

`config/sources.json` を編集して、検索対象の企業や求人プラットフォームを追加します。対応 provider：`greenhouse`、`lever`、`ashby`、`gaijinpot`、`tokyodev`、`japan_dev`、`company_site`。

**設定例：**

```json
{
  "sources": [
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
      "provider": "lever",
      "company": "smartnews",
      "filters": { "locations": ["Tokyo", "Remote"] }
    },
    {
      "provider": "company_site",
      "url": "https://careers.linecorp.com/jobs/",
      "filters": { "keywords": ["エンジニア", "engineer"], "locations": ["Tokyo"] }
    }
  ]
}
```

フィルターはクエリから自動抽出されるため、基本的な用途では手動設定不要です。

**ヒント：AI に sources リストを生成させる**

Claude に以下のプロンプトを送るだけで OK：

> Python スキルと日本語 N2 を持つバックエンドエンジニアとして、東京で英語または中国語対応の技術職を探しています。tokyo_job_finder スキル用の `sources.json` を生成してください。`gaijinpot`、`tokyodev`、`greenhouse`、`lever`、`ashby` を組み合わせ、5〜8 社を対象にしてください。フォーマット：各 source に `provider`、任意で `token`/`company`/`board`/`url`、`keywords` と `locations` を含む `filters` オブジェクトを含めてください。

Claude がそのまま使える `config/sources.json` を出力してくれます。
