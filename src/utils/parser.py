import re


def split_variants(raw: str, max_count: int = 3) -> list[str]:
    """Разбивает ответ модели на отдельные варианты постов."""
    text = raw.strip()
    if not text:
        return []

    pattern = re.compile(
        r"(?:^|\n{2,})(?:ВАРИАНТ|Вариант|VARIANT)\s*[#№]?\s*(\d+)\s*\n?",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(pattern.finditer(text))

    if len(matches) >= 1:
        parts: list[str] = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk = text[start:end].strip()
            if chunk:
                parts.append(chunk)
        if parts:
            return parts[:max_count]

    chunks: list[str] = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip():
            buf.append(line)
        elif buf:
            chunks.append("\n".join(buf))
            buf = []
    if buf:
        chunks.append("\n".join(buf))

    if len(chunks) == 1 and len(chunks[0]) > 400:
        sep_parts = re.split(r"\n{3,}", chunks[0])
        if len(sep_parts) > 1:
            chunks = [p.strip() for p in sep_parts if p.strip()]

    return (chunks or [text])[:max_count]
