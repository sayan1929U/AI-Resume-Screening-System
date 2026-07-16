"""
Section Detector

Extracts major resume sections.

Returned example:

{
    "summary": "...",
    "experience": "...",
    "education": "...",
    "projects": "...",
    "skills": "...",
    "certifications": "...",
    "achievements": "...",
    "languages": "...",
}
"""

from __future__ import annotations

import re


SECTION_HEADERS = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
        "about me",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
    ],

    "education": [
        "education",
        "academic",
        "qualification",
        "qualifications",
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "technologies",
        "tech stack",
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses",
    ],

    "achievements": [
        "achievements",
        "awards",
        "honors",
        "accomplishments",
    ],

    "languages": [
        "languages",
    ],
}


def normalize_text(text: str) -> str:
    """
    Normalize resume text.
    """

    text = text.replace("\r", "")
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def build_header_map():
    """
    alias -> canonical
    """

    mapping = {}

    for canonical, aliases in SECTION_HEADERS.items():
        for alias in aliases:
            mapping[alias.lower()] = canonical

    return mapping


HEADER_MAP = build_header_map()


def detect_headers(lines):
    """
    Find every section header.
    """

    found = []

    for index, line in enumerate(lines):

        clean = line.strip().lower()

        if clean in HEADER_MAP:

            found.append(
                (
                    HEADER_MAP[clean],
                    index,
                )
            )

    return found


def extract_sections(text: str) -> dict[str, str]:

    text = normalize_text(text)

    lines = text.split("\n")

    headers = detect_headers(lines)

    if not headers:
        return {}

    sections = {}

    for i, (section_name, start_index) in enumerate(headers):

        if i == len(headers) - 1:
            end_index = len(lines)
        else:
            end_index = headers[i + 1][1]

        content = "\n".join(
            lines[start_index + 1 : end_index]
        ).strip()

        sections[section_name] = content

    return sections


def has_section(text: str, section: str) -> bool:

    sections = extract_sections(text)

    return section in sections


def missing_sections(text: str):

    sections = extract_sections(text)

    missing = []

    for sec in SECTION_HEADERS:

        if sec not in sections:
            missing.append(sec)

    return missing


def section_statistics(text: str):

    sections = extract_sections(text)

    stats = {}

    for name, value in sections.items():

        stats[name] = {
            "characters": len(value),
            "words": len(value.split()),
            "lines": len(value.splitlines()),
        }

    return stats