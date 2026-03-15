# Provider capability matrix

| Provider      | Public source type | Structured data | Notes |
|---------------|--------------------|-----------------|-------|
| greenhouse    | Job board API      | Strong          | Best first-choice source |
| lever         | Public postings    | Strong          | Good for startup/public postings |
| ashby         | Public board API   | Strong          | Useful when company uses Ashby |
| company_site  | Careers page       | Weak to medium  | Depends on JSON-LD or discoverable job pages |

## Recommendation
Prefer API-backed providers first, then fall back to `company_site`.
