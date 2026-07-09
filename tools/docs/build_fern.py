# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate Fern-compatible MDX from the Isaac Lab documentation sources."""

from __future__ import annotations

import argparse
import ast
import html
import json
import os
import re
import shutil
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

import pypandoc
import tomllib

ISAACLAB_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = ISAACLAB_ROOT / "docs"
SOURCE_ROOT = DOCS_ROOT / "source"
STATIC_ROOT = SOURCE_ROOT / "_static"
FERN_ROOT = ISAACLAB_ROOT / "fern"
GENERATED_ROOT = FERN_ROOT / "generated"
PAGES_ROOT = GENERATED_ROOT / "pages"
ASSETS_ROOT = GENERATED_ROOT / "assets"
GITHUB_BLOB_ROOT = "https://github.com/isaac-sim/IsaacLab/blob/develop"
BIBLIOGRAPHY_URL = f"{GITHUB_BLOB_ROOT}/docs/source/_static/refs.bib"

DIRECTIVE_PATTERN = re.compile(r"^(?P<indent> *)\.\. (?P<name>[A-Za-z0-9_-]+)::\s*(?P<argument>.*)$")
LABEL_PATTERN = re.compile(r"^(?P<indent> *)\.\. _(?P<label>[^:]+):\s*$", re.MULTILINE)
ROLE_PATTERN = re.compile(r":(?P<role>[A-Za-z0-9_-]+):`(?P<value>[^`]+)`")
LINK_PATTERN = re.compile(r"\]\((?P<target>[^)]+)\)")
HTML_ATTRIBUTE_PATTERN = re.compile(r"(?P<name>[A-Za-z_:][A-Za-z0-9_:.-]*)(?:=\"(?P<value>[^\"]*)\")?")

ADMONITION_COMPONENTS = {
    "attention": "Warning",
    "caution": "Warning",
    "danger": "Error",
    "error": "Error",
    "hint": "Tip",
    "important": "Info",
    "note": "Note",
    "seealso": "Info",
    "tip": "Tip",
    "warning": "Warning",
}

EMOJI_SUBSTITUTIONS = {
    "|:floppy_disk:|": "💾",
    "|:inbox_tray:|": "📥",
    "|:package:|": "📦",
    "|:rocket:|": "🚀",
    "|:smiley:|": "🙂",
    "|:tada:|": "🎉",
    "|:whale:|": "🐳",
    "|:x:|": "❌",
}

LANGUAGE_BY_SUFFIX = {
    ".bat": "batch",
    ".cpp": "cpp",
    ".css": "css",
    ".html": "html",
    ".json": "json",
    ".md": "markdown",
    ".py": "python",
    ".rst": "rst",
    ".sh": "bash",
    ".toml": "toml",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
}


@dataclass
class DivNode:
    """Represent a Pandoc directive div while it is converted to MDX."""

    classes: list[str]
    attributes: dict[str, str]
    children: list[str | DivNode] = field(default_factory=list)


def _read_versions() -> dict[str, str]:
    """Read externally pinned versions from the project configuration."""
    with (ISAACLAB_ROOT / "pyproject.toml").open("rb") as stream:
        return tomllib.load(stream)["tool"]["isaaclab"]["versions"]


def _documentation_files() -> list[Path]:
    """Return narrative reStructuredText files that should become Fern pages."""
    files = [DOCS_ROOT / "index.rst"]
    files.extend(
        path
        for path in SOURCE_ROOT.rglob("*.rst")
        if SOURCE_ROOT / "api" not in path.parents and "include" not in path.relative_to(SOURCE_ROOT).parts
    )
    included_files = _included_rst_files(files)
    return sorted(path for path in files if path not in included_files)


def _included_rst_files(files: list[Path]) -> set[Path]:
    """Find reStructuredText fragments consumed through include directives."""
    included: set[Path] = set()
    for source_path in files:
        for match in re.finditer(r"^ *\.\. include::\s*(.+?)\s*$", source_path.read_text(), re.MULTILINE):
            included_path = (source_path.parent / match.group(1)).resolve()
            if included_path.suffix == ".rst" and included_path.is_relative_to(DOCS_ROOT):
                included.add(included_path)
    return included


def _page_output_path(source_path: Path) -> Path:
    """Return the generated MDX path for a documentation source file."""
    if source_path == DOCS_ROOT / "index.rst":
        return GENERATED_ROOT / "index.mdx"
    relative_path = source_path.relative_to(SOURCE_ROOT).with_suffix(".mdx")
    return PAGES_ROOT / relative_path


def _page_url(source_path: Path) -> str:
    """Return the published Fern URL for a documentation source file."""
    if source_path == DOCS_ROOT / "index.rst":
        return "/welcome"
    relative_path = source_path.relative_to(SOURCE_ROOT).with_suffix("")
    parts = list(relative_path.parts)
    if parts[-1].lower() == "index":
        parts.pop()
    return "/" + "/".join(parts)


def _title(source_path: Path) -> str:
    """Extract the first reStructuredText heading from a source file."""
    lines = source_path.read_text().splitlines()
    for index in range(len(lines) - 1):
        text = lines[index].strip()
        underline = lines[index + 1].strip()
        if text and len(underline) >= len(text) and len(set(underline)) == 1 and underline[0] in "=-~^\"'`:+*#_":
            return text
    return source_path.stem.replace("_", " ").title()


def _navigation_positions(files: list[Path]) -> dict[Path, int]:
    """Infer page ordering from each directory's Sphinx toctree."""
    positions: dict[Path, int] = {}
    by_directory: dict[Path, list[Path]] = {}
    for source_path in files:
        by_directory.setdefault(source_path.parent, []).append(source_path)
    for directory_files in by_directory.values():
        index_path = next((path for path in directory_files if path.stem.lower() == "index"), None)
        if index_path is None:
            continue
        targets = _toctree_targets(index_path.read_text())
        position = 1
        for target in targets:
            target_path = (index_path.parent / target).with_suffix(".rst").resolve()
            if target_path in directory_files:
                positions[target_path] = position
                position += 1
    return positions


def _toctree_targets(source: str) -> list[str]:
    """Extract page targets from all toctree directives in a source document."""
    targets: list[str] = []
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        match = DIRECTIVE_PATTERN.match(lines[index])
        if match is None or match.group("name") != "toctree":
            index += 1
            continue
        end_index = _directive_end(lines, index, len(match.group("indent")))
        for line in lines[index + 1 : end_index]:
            value = line.strip()
            if not value or value.startswith(":"):
                continue
            explicit_match = re.match(r".*<(?P<target>[^>]+)>$", value)
            targets.append(explicit_match.group("target") if explicit_match else value)
        index = end_index
    return targets


def _label_map(files: list[Path]) -> dict[str, tuple[str, str]]:
    """Map Sphinx labels to Fern URLs and readable titles."""
    labels: dict[str, tuple[str, str]] = {}
    all_files = files + sorted((SOURCE_ROOT / "api").rglob("*.rst"))
    for source_path in all_files:
        source = source_path.read_text()
        for match in LABEL_PATTERN.finditer(source):
            label = match.group("label")
            if source_path.is_relative_to(SOURCE_ROOT / "api"):
                labels[label] = ("/api", label.replace("-", " ").title())
            else:
                labels[label] = (f"{_page_url(source_path)}#{label}", _title(source_path))
    return labels


def _directive_end(lines: list[str], start_index: int, base_indent: int) -> int:
    """Return the first line after a directive's indented body."""
    index = start_index + 1
    while index < len(lines):
        line = lines[index]
        if not line.strip() or len(line) - len(line.lstrip(" ")) > base_indent:
            index += 1
            continue
        break
    return index


def _directive_options(lines: list[str]) -> dict[str, str]:
    """Parse directive options from an indented directive body."""
    options: dict[str, str] = {}
    for line in lines:
        match = re.match(r"^\s*:([^:]+):\s*(.*)$", line)
        if match:
            options[match.group(1)] = match.group(2)
    return options


def _slice_text(content: str, options: dict[str, str]) -> str:
    """Apply Sphinx include line and marker selections to text."""
    lines = content.splitlines()
    if "start-after" in options:
        marker_index = next(index for index, line in enumerate(lines) if options["start-after"] in line)
        lines = lines[marker_index + 1 :]
    if "start-at" in options:
        marker_index = next(index for index, line in enumerate(lines) if options["start-at"] in line)
        lines = lines[marker_index:]
    if "end-before" in options:
        marker_index = next(index for index, line in enumerate(lines) if options["end-before"] in line)
        lines = lines[:marker_index]
    if "end-at" in options:
        marker_index = next(index for index, line in enumerate(lines) if options["end-at"] in line)
        lines = lines[: marker_index + 1]
    if "start-line" in options:
        lines = lines[int(options["start-line"]) :]
    if "end-line" in options:
        lines = lines[: int(options["end-line"])]
    if "lines" in options:
        selected_lines: list[str] = []
        for selection in options["lines"].split(","):
            bounds = selection.strip().split("-", maxsplit=1)
            start = int(bounds[0])
            end = int(bounds[-1])
            selected_lines.extend(lines[start - 1 : end])
        lines = selected_lines
    return "\n".join(lines)


def _extract_pyobject(content: str, qualified_name: str) -> str:
    """Extract a Python object using its AST source range."""
    tree = ast.parse(content)
    body: list[ast.stmt] = tree.body
    node: ast.AST | None = None
    for name in qualified_name.split("."):
        node = next(
            (
                candidate
                for candidate in body
                if isinstance(candidate, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef))
                and candidate.name == name
            ),
            None,
        )
        if node is None:
            raise ValueError(f"Unable to find Python object '{qualified_name}'")
        body = node.body if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef)) else []
    start_line = node.lineno
    decorators = getattr(node, "decorator_list", [])
    if decorators:
        start_line = min(start_line, *(decorator.lineno for decorator in decorators))
    return "\n".join(content.splitlines()[start_line - 1 : node.end_lineno])


def _literal_include(source_path: Path, target: str, options: dict[str, str]) -> str:
    """Materialize a Sphinx literalinclude directive as a code block."""
    included_path = (source_path.parent / target).resolve()
    content = included_path.read_text()
    if "pyobject" in options:
        content = _extract_pyobject(content, options["pyobject"])
    content = _slice_text(content, options)
    if "dedent" in options:
        dedent_value = options["dedent"]
        content = (
            textwrap.dedent(content)
            if not dedent_value
            else "\n".join(line[int(dedent_value) :] for line in content.splitlines())
        )
    language = options.get("language", LANGUAGE_BY_SUFFIX.get(included_path.suffix, "text"))
    caption = options.get("caption")
    prefix = f"**{caption}**\n\n" if caption else ""
    indented_content = textwrap.indent(content.rstrip(), "   ")
    return f"{prefix}.. code-block:: {language}\n\n{indented_content}\n"


def _expand_includes(source_path: Path, source: str, include_stack: tuple[Path, ...] = ()) -> str:
    """Expand include and literalinclude directives before Pandoc conversion."""
    lines = source.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        match = DIRECTIVE_PATTERN.match(lines[index])
        if match is None or match.group("name") not in {"include", "literalinclude"}:
            output.append(lines[index])
            index += 1
            continue
        base_indent = len(match.group("indent"))
        end_index = _directive_end(lines, index, base_indent)
        options = _directive_options(lines[index + 1 : end_index])
        target = match.group("argument").strip()
        if match.group("name") == "include":
            included_path = (source_path.parent / target).resolve()
            if included_path in include_stack:
                raise ValueError(f"Recursive include detected at '{included_path}'")
            included_source = _slice_text(included_path.read_text(), options)
            replacement = _expand_includes(included_path, included_source, include_stack + (source_path,))
        else:
            replacement = _literal_include(source_path, target, options)
        output.extend(f"{match.group('indent')}{line}" if line else "" for line in replacement.splitlines())
        output.append("")
        index = end_index
    return "\n".join(output)


def _custom_directive(name: str, argument: str, options: dict[str, str], versions: dict[str, str]) -> str:
    """Render an Isaac Lab Sphinx directive as ordinary reStructuredText."""
    branch = "develop"
    if name == "isaaclab-clone-commands":
        return f""".. tab-set::

   .. tab-item:: SSH

      .. code-block:: bash

         git clone git@github.com:isaac-sim/IsaacLab.git --branch {branch}
         cd IsaacLab

   .. tab-item:: HTTPS

      .. code-block:: bash

         git clone https://github.com/isaac-sim/IsaacLab.git --branch {branch}
         cd IsaacLab
"""
    if name == "isaaclab-clone-https":
        command = f"git clone https://github.com/isaac-sim/IsaacLab.git --branch {branch}\ncd IsaacLab"
    elif name == "isaaclab-kitless-install-snippet":
        command = (
            f"git clone https://github.com/isaac-sim/IsaacLab.git --branch {branch}\n"
            "cd IsaacLab\n"
            "./isaaclab.sh --install   # or ./isaaclab.sh -i"
        )
    elif name == "isaaclab-isaacsim-install":
        command = (
            f'uv pip install "isaacsim[all,extscache]=={versions["isaacsim"]}" '
            "--extra-index-url https://pypi.nvidia.com --index-strategy unsafe-best-match --prerelease=allow"
        )
    elif name == "isaaclab-torch-install":
        arguments = argument.split()
        installer = "pip" if len(arguments) > 1 and arguments[1] == "pip" else "uv pip"
        command = (
            f"{installer} install -U torch=={versions['torch']} torchvision=={versions['torchvision']} "
            f"--index-url https://download.pytorch.org/whl/{arguments[0]}"
        )
    elif name == "isaaclab-ovrtx-install":
        command = f'pip install --extra-index-url https://pypi.nvidia.com "ovrtx{versions["ovrtx"]}"'
    elif name == "isaaclab-quickstart-install":
        platform = options.get("platform", "linux")
        executable = "isaaclab.bat" if platform == "windows" else "./isaaclab.sh"
        command = f"git clone https://github.com/isaac-sim/IsaacLab.git --branch {branch}\ncd IsaacLab\n{executable} -i"
    else:
        raise ValueError(f"Unsupported Isaac Lab documentation directive '{name}'")
    return f".. code-block:: bash\n\n{textwrap.indent(command, '   ')}\n"


def _expand_custom_directives(source: str, versions: dict[str, str]) -> str:
    """Expand project-specific Sphinx directives before Pandoc conversion."""
    lines = source.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        match = DIRECTIVE_PATTERN.match(lines[index])
        if match is None or not match.group("name").startswith("isaaclab-"):
            output.append(lines[index])
            index += 1
            continue
        base_indent = len(match.group("indent"))
        end_index = _directive_end(lines, index, base_indent)
        options = _directive_options(lines[index + 1 : end_index])
        replacement = _custom_directive(match.group("name"), match.group("argument"), options, versions)
        output.extend(f"{match.group('indent')}{line}" if line else "" for line in replacement.splitlines())
        output.append("")
        index = end_index
    return "\n".join(output)


def _resolve_doc_target(source_path: Path, target: str) -> Path | None:
    """Resolve a Sphinx doc target to a reStructuredText source path."""
    clean_target = target.split("#", maxsplit=1)[0]
    if clean_target.startswith("/"):
        candidate = DOCS_ROOT / clean_target.lstrip("/")
    else:
        candidate = source_path.parent / clean_target
    if candidate.suffix != ".rst":
        candidate = candidate.with_suffix(".rst")
    candidate = candidate.resolve()
    return candidate if candidate.exists() and candidate.is_relative_to(DOCS_ROOT) else None


def _split_role_value(value: str) -> tuple[str | None, str]:
    """Split an explicit Sphinx role title from its target."""
    match = re.match(r"(?P<title>.+?)\s*<(?P<target>[^>]+)>$", value)
    if match:
        return match.group("title"), match.group("target")
    return None, value


def _replace_roles(source_path: Path, source: str, labels: dict[str, tuple[str, str]]) -> str:
    """Convert Sphinx roles and labels to Markdown or MDX equivalents."""

    def replace_role(match: re.Match[str]) -> str:
        role = match.group("role")
        explicit_title, target = _split_role_value(match.group("value"))
        target = target.strip()
        if role == "ref":
            label = labels.get(target)
            if label is None:
                return explicit_title or target.replace("-", " ").title()
            href, default_title = label
            return f"`{explicit_title or default_title} <{href}>`_"
        if role == "doc":
            target_path = _resolve_doc_target(source_path, target)
            if target_path is None:
                return f"``{explicit_title or target}``"
            return f"`{explicit_title or _title(target_path)} <{_page_url(target_path)}>`_"
        if role == "math":
            return f"${target}$"
        if role == "icon":
            return ""
        if role == "cite":
            return f"`{explicit_title or target} </refs/bibliography>`_"
        if role in {
            "attr",
            "class",
            "data",
            "exc",
            "file",
            "func",
            "meth",
            "mod",
            "obj",
            "p",
            "paramref",
            "t",
        }:
            return f"``{explicit_title or target.lstrip('~')}``"
        if role == "sup":
            return f"<sup>{html.escape(explicit_title or target)}</sup>"
        return f"`{explicit_title or target}`"

    source = ROLE_PATTERN.sub(replace_role, source)

    def replace_label(match: re.Match[str]) -> str:
        indent = match.group("indent")
        label = html.escape(match.group("label"), quote=True)
        return f'{indent}.. raw:: html\n\n{indent}   <Anchor id="{label}" />'

    return LABEL_PATTERN.sub(replace_label, source)


def _global_substitutions(versions: dict[str, str]) -> str:
    """Return substitutions normally injected by Sphinx's rst_prolog."""
    values = {
        "isaaclab_latest_branch": "develop",
        "isaacsim_version": versions["isaacsim"],
        "torch_version": versions["torch"],
        "torchvision_version": versions["torchvision"],
        "ovrtx_spec": versions["ovrtx"],
        "ovphysx_version": versions["ovphysx"],
    }
    return "\n".join(f".. |{name}| replace:: {value}" for name, value in values.items())


def _convert_gfm_alerts(markdown: str) -> str:
    """Convert Pandoc's GitHub alerts to Fern callout components."""
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        match = re.match(r"^> \[!(?P<kind>[A-Z]+)\]\s*$", lines[index])
        if match is None:
            output.append(lines[index])
            index += 1
            continue
        content: list[str] = []
        index += 1
        while index < len(lines) and (lines[index].startswith(">") or not lines[index].strip()):
            if not lines[index].strip():
                content.append("")
            else:
                content.append(re.sub(r"^> ?", "", lines[index]))
            index += 1
        component = ADMONITION_COMPONENTS.get(match.group("kind").lower(), "Info")
        output.extend([f"<{component}>", *content, f"</{component}>"])
    return "\n".join(output)


def _parse_divs(markdown: str) -> list[str | DivNode]:
    """Parse Pandoc directive divs without interpreting ordinary MDX."""
    root: list[str | DivNode] = []
    stack: list[list[str | DivNode]] = [root]
    lines = markdown.splitlines()
    index = 0
    fence: str | None = None
    while index < len(lines):
        line = lines[index]
        fence_match = re.match(r"^\s*(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            fence = None if fence == marker else marker
            stack[-1].append(line)
            index += 1
            continue
        if fence is not None:
            stack[-1].append(line)
            index += 1
            continue
        if line.lstrip().startswith("<div"):
            lookahead = index
            tag_lines = [line.strip()]
            while ">" not in tag_lines[-1] and lookahead + 1 < len(lines):
                lookahead += 1
                tag_lines.append(lines[lookahead].strip())
            tag = " ".join(tag_lines)
            if re.fullmatch(r"<div(?:\s[^>]*)?>", tag) is None:
                stack[-1].append(line)
                index += 1
                continue
            attributes = {
                match.group("name"): match.group("value") or ""
                for match in HTML_ATTRIBUTE_PATTERN.finditer(tag.removeprefix("<div").removesuffix(">").strip())
            }
            classes = attributes.pop("class", "").split()
            node = DivNode(classes=classes, attributes=attributes)
            stack[-1].append(node)
            stack.append(node.children)
            index = lookahead + 1
            continue
        if line.strip() == "</div>" and len(stack) > 1:
            stack.pop()
            index += 1
            continue
        stack[-1].append(line)
        index += 1
    if len(stack) != 1:
        raise ValueError("Unbalanced Pandoc directive divs")
    return root


def _extract_component_title(children: list[str | DivNode], default: str) -> tuple[str, list[str | DivNode]]:
    """Remove and return the first text line in a directive component."""
    remaining = list(children)
    while remaining and isinstance(remaining[0], str) and not remaining[0].strip():
        remaining.pop(0)
    if not remaining or not isinstance(remaining[0], str):
        return default, remaining
    title = remaining.pop(0).strip()
    title = re.sub(r"`fa-[^`]+`\s*", "", title)
    title = re.sub(r"\[([^]]+)\]\{[^}]+\}", r"\1", title)
    return title or default, remaining


def _render_nodes(nodes: list[str | DivNode]) -> str:
    """Render parsed Pandoc nodes as Fern MDX."""
    output: list[str] = []
    for node in nodes:
        if isinstance(node, str):
            output.append(node)
            continue
        primary_class = node.classes[0] if node.classes else ""
        if primary_class in {"contents", "currentmodule", "toctree"}:
            continue
        if primary_class == "tab-set":
            output.extend(["<Tabs>", _render_nodes(node.children), "</Tabs>"])
            continue
        if primary_class == "tab-item":
            title, children = _extract_component_title(node.children, "Option")
            language = node.attributes.get("sync")
            language_attribute = f" language={json.dumps(language)}" if language else ""
            output.extend([f"<Tab title={json.dumps(title)}{language_attribute}>", _render_nodes(children), "</Tab>"])
            continue
        if primary_class == "dropdown":
            title, children = _extract_component_title(node.children, "Details")
            output.extend([f"<Accordion title={json.dumps(title)}>", _render_nodes(children), "</Accordion>"])
            continue
        if primary_class in ADMONITION_COMPONENTS:
            component = ADMONITION_COMPONENTS[primary_class]
            title_attribute = ' title="See also"' if primary_class == "seealso" else ""
            output.extend([f"<{component}{title_attribute}>", _render_nodes(node.children), f"</{component}>"])
            continue
        if primary_class == "admonition":
            title, children = _extract_component_title(node.children, "Note")
            output.extend([f"<Info title={json.dumps(title)}>", _render_nodes(children), "</Info>"])
            continue
        if primary_class == "rubric":
            title, _ = _extract_component_title(node.children, "")
            output.append(f"### {title}")
            continue
        if primary_class == "centered":
            output.append(_render_nodes(node.children))
            continue
        if primary_class == "bibliography":
            output.append(f"The complete bibliography is maintained in [refs.bib]({BIBLIOGRAPHY_URL}).")
            continue
        if primary_class.startswith("auto"):
            title, _ = _extract_component_title(node.children, "this symbol")
            output.append(f"<Info>See `{title}` in the [Source API](/api).</Info>")
            continue
        if primary_class in {"include", "literalinclude"}:
            raise ValueError(f"Unexpanded '{primary_class}' directive")
        class_attribute = f" className={json.dumps(' '.join(node.classes))}" if node.classes else ""
        output.extend([f"<div{class_attribute}>", _render_nodes(node.children), "</div>"])
    return "\n".join(output)


def _rewrite_target(source_path: Path, target: str) -> str:
    """Rewrite a Pandoc link target for its generated Fern page."""
    target = unquote(target)
    legacy_prefix = "https://isaac-sim.github.io/IsaacLab/"
    if target.startswith(legacy_prefix):
        legacy_path, separator, anchor = target.removeprefix(legacy_prefix).partition("#")
        parts = legacy_path.split("/")
        if parts[0] in {"main", "develop"} or parts[0].startswith("release"):
            parts.pop(0)
        if parts and parts[0] == "source":
            parts.pop(0)
        if parts:
            parts[-1] = parts[-1].removesuffix(".html")
        if parts and parts[-1] == "index":
            parts.pop()
        rewritten = "/" + "/".join(parts)
        return f"{rewritten}{separator}{anchor}" if separator else rewritten
    if target.startswith("/source/_static/"):
        asset_path = Path(target.removeprefix("/source/_static/"))
        output_path = _page_output_path(source_path)
        return Path(os.path.relpath(ASSETS_ROOT / asset_path, output_path.parent)).as_posix()
    if target.startswith("/source/"):
        docs_target = _resolve_doc_target(source_path, target)
        if docs_target is not None:
            return _page_url(docs_target)
    if target.startswith(("#", "/", "http://", "https://", "mailto:")):
        return target
    target_path, separator, anchor = target.partition("#")
    resolved = (source_path.parent / target_path).resolve()
    docs_target = _resolve_doc_target(source_path, target_path)
    if docs_target is not None:
        rewritten = _page_url(docs_target)
    elif resolved.is_relative_to(STATIC_ROOT):
        asset_path = resolved.relative_to(STATIC_ROOT)
        output_path = _page_output_path(source_path)
        rewritten = Path(os.path.relpath(ASSETS_ROOT / asset_path, output_path.parent)).as_posix()
    elif resolved.exists() and resolved.is_relative_to(ISAACLAB_ROOT):
        rewritten = f"{GITHUB_BLOB_ROOT}/{resolved.relative_to(ISAACLAB_ROOT).as_posix()}"
    else:
        rewritten = target_path.replace("source/_static", "assets").replace("_static", "assets")
    return f"{rewritten}{separator}{anchor}" if separator else rewritten


def _rewrite_links(source_path: Path, markdown: str) -> str:
    """Rewrite Markdown links and image paths for the Fern output tree."""

    def replace_link(match: re.Match[str]) -> str:
        target = match.group("target")
        if " " in target and not target.startswith("http"):
            path, title = target.split(" ", maxsplit=1)
            return f"]({_rewrite_target(source_path, path)} {title})"
        return f"]({_rewrite_target(source_path, target)})"

    markdown = LINK_PATTERN.sub(replace_link, markdown)

    def replace_src(match: re.Match[str]) -> str:
        return f'src="{_rewrite_target(source_path, match.group("target"))}"'

    return re.sub(r'src="(?P<target>[^"]+)"', replace_src, markdown)


def _normalize_mdx(markdown: str) -> str:
    """Normalize Pandoc HTML so it is valid JSX inside MDX."""
    markdown = re.sub(r"(<img\b[^>]*?)\s+style=\"[^\"]*\"", r"\1", markdown, flags=re.DOTALL)
    markdown = re.sub(r"\bclass=", "className=", markdown)
    markdown = re.sub(r"<br\s*>", "<br />", markdown)
    lines = markdown.splitlines()
    normalized_lines: list[str] = []
    fence: str | None = None
    for line in lines:
        fence_match = re.match(r"^\s*(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            fence = None if fence == marker else marker
        if fence is None:
            line = re.sub(r"<(https?://[^>]+)>", r"[\1](\1)", line)
            line = re.sub(r"<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>", r"[\1](mailto:\1)", line)
            line = re.sub(r"\\\$(.+?)\\\$", r"$\1$", line)
            line = _escape_mdx_braces(line)
        normalized_lines.append(line)
    markdown = "\n".join(normalized_lines)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


def _escape_mdx_braces(line: str) -> str:
    """Escape prose braces while preserving inline code and math."""
    output: list[str] = []
    index = 0
    code_delimiter = 0
    in_math = False
    while index < len(line):
        if line[index] == "`":
            run_end = index
            while run_end < len(line) and line[run_end] == "`":
                run_end += 1
            run_length = run_end - index
            code_delimiter = 0 if code_delimiter == run_length else run_length
            output.append(line[index:run_end])
            index = run_end
            continue
        if line[index] == "$" and code_delimiter == 0 and (index == 0 or line[index - 1] != "\\"):
            in_math = not in_math
        if line[index] == "{" and code_delimiter == 0 and not in_math:
            output.append("&#123;")
        elif line[index] == "}" and code_delimiter == 0 and not in_math:
            output.append("&#125;")
        else:
            output.append(line[index])
        index += 1
    return "".join(output)


def _strip_page_heading(markdown: str, title: str) -> str:
    """Remove the source H1 because Fern generates it from navigation metadata."""
    lines = markdown.splitlines()
    output: list[str] = []
    removed = False
    fence: str | None = None
    for line in lines:
        fence_match = re.match(r"^\s*(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            fence = None if fence == marker else marker
            output.append(line)
            continue
        if fence is None and not removed and line.startswith("# ") and line[2:].strip() == title:
            removed = True
            continue
        output.append(f"#{line}" if fence is None and line.startswith("# ") else line)
    return "\n".join(output)


def _frontmatter(title: str, position: int | None) -> str:
    """Build Fern page frontmatter."""
    lines = ["---", f"title: {json.dumps(title)}"]
    if position is not None:
        lines.append(f"position: {position}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def _convert_page(
    source_path: Path,
    output_path: Path,
    labels: dict[str, tuple[str, str]],
    versions: dict[str, str],
    position: int | None,
) -> None:
    """Convert one reStructuredText page to Fern MDX."""
    source = _expand_includes(source_path, source_path.read_text())
    source = _expand_custom_directives(source, versions)
    for substitution, emoji in EMOJI_SUBSTITUTIONS.items():
        source = source.replace(substitution, emoji)
    source = _replace_roles(source_path, source, labels)
    source = f"{_global_substitutions(versions)}\n\n{source}"
    markdown = pypandoc.convert_text(source, to="gfm", format="rst", extra_args=["--wrap=none"])
    markdown = _convert_gfm_alerts(markdown)
    markdown = _render_nodes(_parse_divs(markdown))
    markdown = _rewrite_links(source_path, markdown)
    markdown = _normalize_mdx(markdown)
    title = _title(source_path)
    markdown = _strip_page_heading(markdown, title)
    if source_path == DOCS_ROOT / "index.rst":
        markdown = re.sub(r"\n## Table of Contents\s*\n", "\n", markdown)
        markdown = re.sub(r"\n## Indices and tables\s*\n.*$", "", markdown, flags=re.DOTALL)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{_frontmatter(title, position)}{markdown}\n")


def build() -> None:
    """Generate all Fern guide pages and static assets."""
    files = _documentation_files()
    versions = _read_versions()
    labels = _label_map(files)
    positions = _navigation_positions(files)
    shutil.rmtree(GENERATED_ROOT, ignore_errors=True)
    shutil.copytree(STATIC_ROOT, ASSETS_ROOT)
    for source_path in files:
        try:
            _convert_page(source_path, _page_output_path(source_path), labels, versions, positions.get(source_path))
        except Exception as error:
            raise RuntimeError(f"Failed to convert '{source_path.relative_to(ISAACLAB_ROOT)}'") from error
    generated_pages = list(GENERATED_ROOT.rglob("*.mdx"))
    if len(generated_pages) != len(files):
        raise RuntimeError(f"Generated {len(generated_pages)} pages from {len(files)} sources")
    print(f"Generated {len(generated_pages)} Fern pages and copied assets to {GENERATED_ROOT}")


def main() -> None:
    """Run the Fern documentation generator."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    build()


if __name__ == "__main__":
    main()
