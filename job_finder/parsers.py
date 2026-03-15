from __future__ import annotations

from typing import Dict, List


def parse_user_query(query: str) -> Dict[str, object]:
    text = query.strip()
    text_l = text.lower()

    roles = []
    role_vocab = [
        "AI Engineer", "LLM Engineer", "Applied AI Engineer", "RAG Engineer",
        "Backend Engineer", "Platform Engineer", "ML Engineer", "Data Engineer",
    ]
    for role in role_vocab:
        if role.lower() in text_l:
            roles.append(role)

    location_hits = []
    for loc in ["Tokyo", "Japan", "Remote", "Osaka", "Kyoto", "Yokohama"]:
        if loc.lower() in text_l:
            location_hits.append(loc)

    skills = []
    skill_vocab = [
        "Python", "FastAPI", "RAG", "LLM", "LangChain", "LangGraph",
        "OpenSearch", "Qdrant", "FAISS", "AWS", "GCP", "Azure",
        "Docker", "Kubernetes", "Go", "TypeScript", "React", "Agent",
        "Vector Search", "Machine Learning",
    ]
    for skill in skill_vocab:
        if skill.lower() in text_l:
            skills.append(skill)

    keyword_terms = []
    for term in role_vocab + skill_vocab + ["startup", "product", "backend", "platform", "applied ai"]:
        if term.lower() in text_l:
            keyword_terms.append(term)

    remote_preference = None
    if "remote only" in text_l or "fully remote" in text_l:
        remote_preference = "only"
    elif "remote" in text_l:
        remote_preference = "prefer"

    return {
        "raw_query": text,
        "target_roles": roles,
        "locations": location_hits,
        "skills": skills,
        "keyword_terms": keyword_terms,
        "remote_preference": remote_preference,
    }
