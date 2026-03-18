#!/usr/bin/env python3
# This file has 4 separate jobs
# 1. Parse resources.md and record incorrect syntax
# 2. Extract valid linkes from resources.md and update links.txt if missing
# 3. Generate an old school html browser bookmark import file (consumes links.txt)
# 4. Test URLs in resources.md and report 404 and related errors

from __future__ import annotations

import argparse
import html
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RESOURCES_PATH = ROOT / "resources.md"
LINKS_PATH = ROOT / "links.txt"
BOOKMARKS_PATH = ROOT / "learning-resources-bookmark.html"
BOOKMARKS_FOLDER = "DrSatrns Learning Resources"
DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_RETRIES = 2
USER_AGENT = "learning-resources-link-checker/1.0"
SKIPPED_STATUS_CODES = {401, 403, 405, 429}


@dataclass(frozen=True)
class LinkEntry:
    title: str
    url: str
    line_number: int


@dataclass(frozen=True)
class ValidationError:
    line_number: int
    column_number: int
    message: str


@dataclass(frozen=True)
class LinkCheckResult:
    url: str
    status: str
    detail: str
    line_numbers: tuple[int, ...]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Missing required file: {path}", file=sys.stderr)
        raise SystemExit(1) from None


def parse_markdown_links(text: str, *, source_name: str) -> tuple[list[LinkEntry], list[ValidationError]]:
    entries: list[LinkEntry] = []
    errors: list[ValidationError] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\n")
        index = 0
        while index < len(line):
            start = line.find("[", index)
            if start == -1:
                break

            if start > 0 and line[start - 1] in {"\\", "!"}:
                index = start + 1
                continue

            end_title = line.find("]", start + 1)
            if end_title == -1:
                errors.append(
                    ValidationError(
                        line_number=line_number,
                        column_number=start + 1,
                        message=f"{source_name}: unclosed '[' in Markdown link",
                    )
                )
                break

            title = line[start + 1 : end_title]
            if not title:
                errors.append(
                    ValidationError(
                        line_number=line_number,
                        column_number=start + 1,
                        message=f"{source_name}: link title cannot be empty",
                    )
                )

            if end_title + 1 >= len(line):
                index = end_title + 1
                continue

            if line[end_title + 1] == "(":
                url_start = end_title + 2
            else:
                cursor = end_title + 1
                while cursor < len(line) and line[cursor].isspace():
                    cursor += 1
                if cursor < len(line) and line[cursor] == "(":
                    errors.append(
                        ValidationError(
                            line_number=line_number,
                            column_number=end_title + 2,
                            message=f"{source_name}: Markdown links cannot contain spaces between ']' and '('",
                        )
                    )
                index = end_title + 1
                continue

            url_end = find_matching_paren(line, url_start - 1)
            if url_end is None:
                errors.append(
                    ValidationError(
                        line_number=line_number,
                        column_number=url_start + 1,
                        message=f"{source_name}: unclosed '(' in Markdown link",
                    )
                )
                break

            url = line[url_start:url_end]
            if not url:
                errors.append(
                    ValidationError(
                        line_number=line_number,
                        column_number=url_start + 1,
                        message=f"{source_name}: link URL cannot be empty",
                    )
                )
            elif url != url.strip():
                errors.append(
                    ValidationError(
                        line_number=line_number,
                        column_number=url_start + 1,
                        message=f"{source_name}: link URL cannot start or end with whitespace",
                    )
                )
            elif any(character.isspace() for character in url):
                errors.append(
                    ValidationError(
                        line_number=line_number,
                        column_number=url_start + 1,
                        message=f"{source_name}: link URL cannot contain whitespace",
                    )
                )
            else:
                entries.append(LinkEntry(title=title, url=url, line_number=line_number))

            index = url_end + 1

    return entries, errors


def find_matching_paren(line: str, open_paren_index: int) -> int | None:
    depth = 0
    for index in range(open_paren_index, len(line)):
        character = line[index]
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def filter_extractable_links(entries: Iterable[LinkEntry]) -> list[LinkEntry]:
    return [entry for entry in entries if entry.url.startswith(("http://", "https://"))]


def parse_resources_file() -> tuple[list[LinkEntry], list[ValidationError]]:
    text = read_text(RESOURCES_PATH)
    return parse_markdown_links(text, source_name=RESOURCES_PATH.name)


def parse_links_file() -> tuple[list[LinkEntry], list[ValidationError]]:
    entries, errors = parse_markdown_links(read_text(LINKS_PATH), source_name=LINKS_PATH.name)

    expected_line_numbers = {entry.line_number for entry in entries}
    for line_number, raw_line in enumerate(read_text(LINKS_PATH).splitlines(), start=1):
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue

        entries_on_line = [entry for entry in entries if entry.line_number == line_number]
        if not entries_on_line:
            errors.append(
                ValidationError(
                    line_number=line_number,
                    column_number=1,
                    message=f"{LINKS_PATH.name}: each non-empty line must contain exactly one Markdown link",
                )
            )
            continue

        if line_number not in expected_line_numbers:
            continue

        entry = entries_on_line[0]
        expected_line = f"[{entry.title}]({entry.url})"
        if stripped_line != expected_line:
            errors.append(
                ValidationError(
                    line_number=line_number,
                    column_number=1,
                    message=f"{LINKS_PATH.name}: each non-empty line must be a single Markdown link with no extra text",
                )
            )
        if len(entries_on_line) > 1:
            errors.append(
                ValidationError(
                    line_number=line_number,
                    column_number=1,
                    message=f"{LINKS_PATH.name}: each line may contain only one Markdown link",
                )
            )

    return filter_extractable_links(entries), errors


def write_links_file(entries: Iterable[LinkEntry]) -> None:
    content = "\n".join(f"[{entry.title}]({entry.url})" for entry in entries)
    if content:
        content += "\n"
    LINKS_PATH.write_text(content, encoding="utf-8")


def build_bookmarks_html(entries: Iterable[LinkEntry]) -> str:
    timestamp = str(int(time.time()))
    item_lines = [
        f'        <DT><A HREF="{html.escape(entry.url, quote=True)}" ADD_DATE="{timestamp}">{html.escape(entry.title)}</A>'
        for entry in entries
    ]

    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This file is generated. Changes may be overwritten. -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
        f'    <DT><H3 ADD_DATE="{timestamp}" LAST_MODIFIED="{timestamp}">{html.escape(BOOKMARKS_FOLDER)}</H3>',
        "    <DL><p>",
        *item_lines,
        "    </DL><p>",
        "</DL><p>",
        "",
    ]
    return "\n".join(lines)


def validate_resources_command(_: argparse.Namespace) -> int:
    entries, errors = parse_resources_file()
    extractable_entries = filter_extractable_links(entries)

    if errors:
        print_validation_errors(errors)
        return 1

    print(
        f"Validated {RESOURCES_PATH.name}: {len(extractable_entries)} extractable http(s) link(s) found."
    )
    return 0


def sync_links_command(args: argparse.Namespace) -> int:
    entries, errors = parse_resources_file()
    extractable_entries = filter_extractable_links(entries)

    if errors:
        print_validation_errors(errors)
        return 1

    existing_content = read_text(LINKS_PATH) if LINKS_PATH.exists() else ""
    updated_content = "\n".join(f"[{entry.title}]({entry.url})" for entry in extractable_entries)
    if updated_content:
        updated_content += "\n"

    if args.check:
        if existing_content != updated_content:
            print(f"{LINKS_PATH.name} is out of date with {RESOURCES_PATH.name}.", file=sys.stderr)
            return 1
        print(f"{LINKS_PATH.name} is up to date.")
        return 0

    write_links_file(extractable_entries)
    print(f"Updated {LINKS_PATH.name} with {len(extractable_entries)} link(s).")
    return 0


def export_bookmarks_command(_: argparse.Namespace) -> int:
    entries, errors = parse_links_file()
    if errors:
        print_validation_errors(errors)
        return 1

    BOOKMARKS_PATH.write_text(build_bookmarks_html(entries), encoding="utf-8")
    print(f"Wrote {BOOKMARKS_PATH.name} with {len(entries)} bookmark(s).")
    return 0


def check_links_command(args: argparse.Namespace) -> int:
    entries, errors = parse_resources_file()
    extractable_entries = filter_extractable_links(entries)

    if errors:
        print_validation_errors(errors)
        return 1

    url_to_lines: dict[str, list[int]] = {}
    for entry in extractable_entries:
        url_to_lines.setdefault(entry.url, []).append(entry.line_number)

    failures: list[LinkCheckResult] = []
    skipped: list[LinkCheckResult] = []

    for url, line_numbers in url_to_lines.items():
        result = check_single_link(url, tuple(line_numbers), retries=args.retries, timeout=args.timeout)
        if result.status == "failed":
            failures.append(result)
        elif result.status == "skipped":
            skipped.append(result)

    if skipped:
        for result in skipped:
            line_text = ", ".join(str(line_number) for line_number in result.line_numbers)
            print(
                f"Skipped inconclusive response for {result.url} (lines {line_text}): {result.detail}",
                file=sys.stderr,
            )

    if failures:
        for result in failures:
            line_text = ", ".join(str(line_number) for line_number in result.line_numbers)
            print(
                f"Broken link in {RESOURCES_PATH.name} line(s) {line_text}: {result.url} ({result.detail})",
                file=sys.stderr,
            )
        return 1

    print(f"Checked {len(url_to_lines)} unique http(s) link(s); no clear failures found.")
    return 0


def check_single_link(url: str, line_numbers: tuple[int, ...], *, retries: int, timeout: int) -> LinkCheckResult:
    last_detail = "request did not complete"

    for attempt in range(1, retries + 1):
        status_code, detail = attempt_link_request(url, timeout=timeout)
        last_detail = detail

        if status_code is None:
            if attempt < retries:
                time.sleep(1)
            continue

        if 200 <= status_code < 400:
            return LinkCheckResult(url=url, status="ok", detail=f"HTTP {status_code}", line_numbers=line_numbers)

        if status_code in SKIPPED_STATUS_CODES:
            return LinkCheckResult(
                url=url,
                status="skipped",
                detail=f"HTTP {status_code}",
                line_numbers=line_numbers,
            )

        if 500 <= status_code < 600 and attempt < retries:
            time.sleep(1)
            continue

        return LinkCheckResult(
            url=url,
            status="failed",
            detail=f"HTTP {status_code}",
            line_numbers=line_numbers,
        )

    return LinkCheckResult(url=url, status="failed", detail=last_detail, line_numbers=line_numbers)


def attempt_link_request(url: str, *, timeout: int) -> tuple[int | None, str]:
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "*/*",
            },
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, f"{method} HTTP {response.status}"
        except urllib.error.HTTPError as error:
            if method == "HEAD" and error.code in {401, 403, 405}:
                continue
            return error.code, f"{method} HTTP {error.code}"
        except urllib.error.URLError as error:
            if method == "HEAD":
                continue
            return None, f"{method} {error.reason}"

    return None, "request failed"


def print_validation_errors(errors: Iterable[ValidationError]) -> None:
    for error in errors:
        print(
            f"Line {error.line_number}, column {error.column_number}: {error.message}",
            file=sys.stderr,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate resources, sync links.txt, export bookmarks, and check live URLs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-resources", help="Validate resources.md link syntax.")
    validate_parser.set_defaults(func=validate_resources_command)

    sync_parser = subparsers.add_parser("sync-links", help="Update links.txt from resources.md.")
    sync_parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with a non-zero status if links.txt is not in sync.",
    )
    sync_parser.set_defaults(func=sync_links_command)

    export_parser = subparsers.add_parser(
        "export-bookmarks",
        help="Generate the browser-importable bookmarks HTML file from links.txt.",
    )
    export_parser.set_defaults(func=export_bookmarks_command)

    check_parser = subparsers.add_parser("check-links", help="Check live http(s) links from resources.md.")
    check_parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Number of attempts per URL before failing. Default: {DEFAULT_RETRIES}.",
    )
    check_parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Timeout in seconds for each request. Default: {DEFAULT_TIMEOUT_SECONDS}.",
    )
    check_parser.set_defaults(func=check_links_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
