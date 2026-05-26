import re

_VARIANT_HEADER = re.compile(
    r"^(?:вариант|variant)\s*[#№]?\s*\d+\s*[-–—:]?\s*$",
    re.IGNORECASE,
)
_FRAME_LINE = re.compile(
    r"^[=\u2500\u2501\u2014\-_*#~·•\s]{2,}$",
)
_INLINE_FRAME = re.compile(r"^[=\u2500\u2014\-_*]+\s*|\s*[=\u2500\u2014\-_*]+$")


def clean_post_text(text: str) -> str:
    """Убирает служебные метки, рамки и лишние пустые строки."""
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if _VARIANT_HEADER.match(stripped):
            continue
        if _FRAME_LINE.match(stripped):
            continue
        if stripped in ("═══", "───", "---", "___", "***", "···"):
            continue
        cleaned_line = _INLINE_FRAME.sub("", stripped).strip()
        if cleaned_line:
            lines.append(cleaned_line)

    result = "\n".join(lines).strip()
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def split_variants(raw: str, max_count: int = 3) -> list[str]:
    """Разбивает ответ модели на отдельные варианты постов."""
    text = raw.strip()
    if not text:
        return []

    parts: list[str] = []

    if re.search(r"\n-{3,}\n", text):
        parts = [p.strip() for p in re.split(r"\n-{3,}\n", text) if p.strip()]

    if not parts:
        pattern = re.compile(
            r"(?:^|\n{2,})(?:ВАРИАНТ|Вариант|VARIANT)\s*[#№]?\s*\d+\s*\n?",
            re.IGNORECASE | re.MULTILINE,
        )
        matches = list(pattern.finditer(text))
        if matches:
            for i, match in enumerate(matches):
                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                chunk = text[start:end].strip()
                if chunk:
                    parts.append(chunk)

    if not parts:
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
        parts = chunks or [text]

    cleaned = []
    seen: set[str] = set()
    for part in parts[: max_count * 2]:
        post = clean_post_text(part)
        if not post:
            continue
        key = post.casefold()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(post)
        if len(cleaned) >= max_count:
            break

    return cleaned
