import re


TREE_SYMBOLS = (
    "\u251c",
    "\u2514",
    "\u2502",
    "\u2500",
    "\u00e2\u20ac\u009d\u0153",
    "\u00e2\u20ac\u009d\u201d",
    "\u00e2\u20ac\u009d\u201a",
    "\u00e2\u20ac\u009d\u201a\u00ac",
    "|-",
    "+-",
)
COMMAND_PREFIXES = (
    "python ",
    "python3 ",
    "pip ",
    "pip3 ",
    "npm ",
    "node ",
    "make ",
    "docker ",
    "git ",
    "uv ",
    "pytest ",
    "poetry ",
)
PYTHON_PATH_RE = re.compile(r"[A-Za-z0-9_./\\-]+?\.py")
ENTRYPOINT_HINT_RE = re.compile(
    r"\b(entrypoint|main script|run this|run the pipeline|start with)\b",
    re.IGNORECASE,
)
NOISE_PREFIXES = (
    "files",
    "file",
    "entrypoint",
    "entrypoints",
    "logic",
    "prompt",
    "llm",
    "format",
    "instructions",
    "indexing",
    "point",
)


def _dedupe_preserve_order(items, key=None):
    seen = set()
    output = []
    for item in items:
        marker = key(item) if key else item
        if marker in seen:
            continue
        seen.add(marker)
        output.append(item)
    return output


def _dedupe_keep_last(items, key=None):
    if not items:
        return []

    reversed_items = []
    seen = set()
    for item in reversed(items):
        marker = key(item) if key else item
        if marker in seen:
            continue
        seen.add(marker)
        reversed_items.append(item)

    reversed_items.reverse()
    return reversed_items


def _normalize_line(line):
    return (
        line.replace("\u00e2\u20ac\u009d\u0153", "\u251c")
        .replace("\u00e2\u20ac\u009d\u201d", "\u2514")
        .replace("\u00e2\u20ac\u009d\u201a", "\u2502")
        .replace("\u00e2\u20ac\u009d\u201a\u00ac", "\u2500")
        .rstrip()
    )


def _looks_like_tree_line(line):
    clean = _normalize_line(line).strip()
    if not clean:
        return False
    if any(symbol in clean for symbol in TREE_SYMBOLS):
        return True
    if clean.endswith("/") and " " not in clean:
        return True
    return bool(re.match(r"^[A-Za-z0-9_.-]+/$", clean))


def extract_folder_trees(text):
    trees = []
    current_tree = []

    for line in text.splitlines():
        clean = _normalize_line(line).strip()
        if _looks_like_tree_line(clean):
            current_tree.append(clean)
            continue

        if len(current_tree) > 1:
            trees.append("\n".join(current_tree))
        current_tree = []

    if len(current_tree) > 1:
        trees.append("\n".join(current_tree))

    trees = _dedupe_preserve_order(trees)
    return trees[-1:] if trees else []


def extract_file_paths(text):
    prepared_text = _prepare_python_path_text(text)
    matches = re.findall(PYTHON_PATH_RE, prepared_text)
    paths = []

    for match in matches:
        path = _normalize_python_path(match)
        if path:
            paths.append(path)

    return _dedupe_preserve_order(paths)


def extract_module_imports(text):
    modules = []
    import_re = re.compile(r"^\s*import\s+([A-Za-z0-9_.,\s]+)", re.MULTILINE)
    from_re = re.compile(
        r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+([A-Za-z0-9_*.,\s]+)",
        re.MULTILINE,
    )

    for match in import_re.finditer(text):
        raw_names = match.group(1)
        for module in raw_names.split(","):
            module = module.strip().split(" as ")[0].strip()
            if module:
                modules.append(module)

    for match in from_re.finditer(text):
        parent = match.group(1).strip()
        targets = match.group(2)
        modules.append(parent)
        for target in targets.split(","):
            target = target.strip().split(" as ")[0].strip()
            if target and target != "*":
                modules.append(f"{parent}.{target}")

    return _dedupe_keep_last(modules)


def extract_commands(text):
    commands = []

    for line in text.splitlines():
        clean = line.strip()
        clean = re.sub(r"^[>$#`\s]+", "", clean)
        if clean.startswith(COMMAND_PREFIXES):
            commands.append(clean)

    return _dedupe_keep_last(commands)


def _infer_filename(context, code, index):
    file_matches = extract_file_paths(context)
    if file_matches:
        return file_matches[-1]

    first_line = code.splitlines()[0].strip() if code.splitlines() else ""
    if first_line.endswith(".py") and "/" in first_line:
        return first_line

    return f"code_snippet_{index}.txt"


def _prepare_python_path_text(text):
    prepared = text.replace("\\", "/")
    prepared = re.sub(r"(?<=\.py)(?=[A-Za-z0-9_./\\-])", " ", prepared)
    prepared = re.sub(
        r"([A-Z]{2,})([A-Za-z0-9_./\\-]+?\.py)",
        r"\1 \2",
        prepared,
    )
    return prepared


def _normalize_python_path(path):
    normalized = path.replace("\\", "/").strip().strip("`'\"()[]{}:;,")
    normalized = normalized.lstrip("./")
    normalized = re.sub(r"/{2,}", "/", normalized)

    if not normalized.endswith(".py"):
        return ""

    parts = [part for part in normalized.split("/") if part]
    if not parts:
        return ""

    parts[-1] = _clean_python_filename(parts[-1])
    if not parts[-1]:
        return ""

    return "/".join(parts)


def _clean_python_filename(filename):
    cleaned = filename.strip()
    if not cleaned.endswith(".py"):
        return ""

    stem = cleaned[:-3]
    lowered = stem.lower()

    changed = True
    while changed:
        changed = False
        for prefix in NOISE_PREFIXES:
            if lowered.startswith(prefix) and len(stem) > len(prefix):
                stem = stem[len(prefix) :].lstrip("_-")
                lowered = stem.lower()
                changed = True

    if not stem:
        return ""

    return f"{stem}.py"


def extract_code_blocks(text):
    blocks = []
    parts = text.split("```")

    for i in range(1, len(parts), 2):
        raw_block = parts[i].strip()
        if len(raw_block.splitlines()) < 2:
            continue

        lines = raw_block.split("\n", 1)
        language = ""
        code = raw_block
        if len(lines) > 1 and re.fullmatch(r"[A-Za-z0-9_#+.-]+", lines[0].strip()):
            language = lines[0].strip()
            code = lines[1].strip()

        if len(code.splitlines()) < 2:
            continue

        preceding = parts[i - 1][-300:]
        filename = _infer_filename(preceding, code, i)
        blocks.append(
            {
                "filename": filename,
                "language": language or "text",
                "code": code,
            }
        )

    return _dedupe_keep_last(blocks, key=lambda item: item["filename"])


def extract_entrypoints(text, file_paths=None, commands=None):
    file_paths = file_paths or []
    commands = commands or []
    entrypoints = []

    for command in commands:
        match = re.search(r"\bpython(?:3)?\s+([A-Za-z0-9_./\\-]+\.py)\b", command)
        if match:
            entrypoints.append(match.group(1).replace("\\", "/").lstrip("./"))

    candidate_names = ("main.py", "app.py", "server.py", "memory_sync.py")
    runnable_prefixes = ("run_", "generate_")

    lines = text.splitlines()
    for index, line in enumerate(lines):
        clean = line.strip()
        if not clean:
            continue

        if ENTRYPOINT_HINT_RE.search(clean):
            window = "\n".join(lines[index : index + 3])
            for path in PYTHON_PATH_RE.findall(window):
                entrypoints.append(path.replace("\\", "/").lstrip("./"))

    for path in file_paths:
        filename = path.split("/")[-1]
        if filename in candidate_names or filename.startswith(runnable_prefixes):
            entrypoints.append(path)

    return _dedupe_keep_last(entrypoints)


def describe_file_role(path):
    filename = path.split("/")[-1]
    stem = filename.rsplit(".", 1)[0]

    if filename == "__init__.py":
        return f"{path} - package initializer"
    if filename == "memory_sync.py":
        return f"{path} - end-to-end pipeline orchestrator"
    if stem.startswith("run_"):
        return f"{path} - runnable helper script"
    if stem.startswith("generate_"):
        return f"{path} - snapshot or report generator"
    if stem.startswith("test_"):
        return f"{path} - test or manual verification script"
    if "extract" in stem:
        return f"{path} - extraction logic"
    if "parser" in stem:
        return f"{path} - conversation parsing logic"
    if "prompt" in stem:
        return f"{path} - prompt construction logic"
    if "index" in stem:
        return f"{path} - vector index logic"
    if "search" in stem:
        return f"{path} - retrieval logic"
    if "model" in stem:
        return f"{path} - model wrapper or embedding logic"
    if "client" in stem:
        return f"{path} - external service client"
    if "config" in stem:
        return f"{path} - project configuration"
    if "schema" in stem:
        return f"{path} - packet or data schema"
    return f"{path} - python module referenced in the conversation"
