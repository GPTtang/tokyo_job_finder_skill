from __future__ import annotations

from typing import Dict, List


# Roles: English + Japanese variants
_ROLE_VOCAB = [
    # AI / LLM
    "AI Engineer", "LLM Engineer", "Applied AI Engineer", "RAG Engineer",
    "ML Engineer", "Machine Learning Engineer", "Data Engineer", "Data Scientist",
    "AI Researcher", "Prompt Engineer",
    # Backend / Platform
    "Backend Engineer", "Platform Engineer", "Software Engineer",
    "Full-Stack Engineer", "Full Stack Engineer", "Frontend Engineer",
    "Infrastructure Engineer", "Cloud Engineer", "DevOps Engineer",
    # Management & Consulting
    "Project Manager", "Product Manager", "IT Consultant", "DX Consultant",
    "System Architect", "Solution Architect", "Technical Lead",
    # Japan-specific
    "Bridge SE", "ブリッジSE", "ブリッジエンジニア",
    "システムエンジニア", "プロジェクトマネージャー", "プロダクトマネージャー",
    "開発エンジニア", "インフラエンジニア", "クラウドエンジニア",
    "ITコンサルタント", "アーキテクト",
]

# Skills: English + Japanese variants
_SKILL_VOCAB = [
    # AI / LLM
    "Python", "RAG", "LLM", "LangChain", "LangGraph", "Agent",
    "Vector Search", "Machine Learning", "FastAPI",
    "OpenSearch", "Elasticsearch", "Qdrant", "FAISS",
    "PyTorch", "TensorFlow", "Dify", "Ollama",
    # Backend languages
    "Java", "C#", ".NET", ".NET Core", "Go", "TypeScript", "JavaScript",
    "PHP", "Ruby", "Kotlin", "Scala",
    # Frontend
    "React", "Vue", "Angular",
    # Cloud & Infra
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Jenkins",
    "Nginx", "Redis", "RabbitMQ",
    # Databases
    "SQL Server", "MySQL", "PostgreSQL", "MongoDB", "Oracle",
    # Microsoft ecosystem
    "SharePoint", "Office365", "Dynamics 365", "Power Platform",
    # Domain
    "BIM", "CAD", "SAP", "ERP",
    # Japanese market
    "オフショア", "offshore", "マイクロサービス", "microservices",
]

# JLPT level keywords
_JLPT_MAP = {
    "n1": "N1", "jlpt n1": "N1", "日本語n1": "N1",
    "n2": "N2", "jlpt n2": "N2", "日本語n2": "N2",
    "n3": "N3", "jlpt n3": "N3",
    "business japanese": "N2", "ビジネス日本語": "N2",
    "native japanese": "N1", "日本語ネイティブ": "N1",
    "conversational japanese": "N3", "日常会話": "N3",
}

# Chinese speaker advantage signals
_CHINESE_SIGNALS = [
    "中国語", "chinese", "中文", "mandarin", "普通话",
    "中国系", "中国人", "华人", "オフショア", "offshore",
    "bridge se", "ブリッジse", "ブリッジエンジニア",
    "大連", "上海", "北京", "深圳", "沈阳", "dalian",
]


def parse_user_query(query: str) -> Dict[str, object]:
    text = query.strip()
    text_l = text.lower()

    roles = [r for r in _ROLE_VOCAB if r.lower() in text_l]

    location_hits = []
    for loc in ["Tokyo", "Japan", "Remote", "Osaka", "Kyoto", "Yokohama",
                "東京", "大阪", "京都", "横浜",
                "东京", "日本", "大阪市", "京都市"]:
        if loc.lower() in text_l:
            location_hits.append(loc)

    skills = [s for s in _SKILL_VOCAB if s.lower() in text_l]

    keyword_terms = list({
        t for t in _ROLE_VOCAB + _SKILL_VOCAB + [
            "startup", "product", "backend", "platform", "applied ai",
            "DX", "SES", "SIer", "consulting",
        ]
        if t.lower() in text_l
    })

    remote_preference = None
    if "remote only" in text_l or "fully remote" in text_l or "纯远程" in text_l:
        remote_preference = "only"
    elif "remote" in text_l or "远程" in text_l or "リモート" in text_l:
        remote_preference = "prefer"

    # JLPT level declared in query — prefer the highest explicit level found
    # (e.g. "I have N2, working towards N1" → N2 is the current cert)
    _JLPT_RANK_MAP = {"N1": 1, "N2": 2, "N3": 3}
    jlpt_hits = [level for pattern, level in _JLPT_MAP.items() if pattern in text_l]
    jlpt_level = min(jlpt_hits, key=lambda x: _JLPT_RANK_MAP[x]) if jlpt_hits else None

    # Chinese speaker flag
    is_chinese_speaker = any(sig in text_l for sig in [
        "chinese speaker", "中文母语", "native chinese", "中国人",
        "chinese native", "mandarin native",
    ])

    return {
        "raw_query": text,
        "target_roles": roles,
        "locations": location_hits,
        "skills": skills,
        "keyword_terms": keyword_terms,
        "remote_preference": remote_preference,
        "jlpt_level": jlpt_level,
        "is_chinese_speaker": is_chinese_speaker,
    }
