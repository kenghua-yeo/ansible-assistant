"""
Regenerate .claude/skills/_shared/catalog.md by scanning two separate
trees under the project root:

  collections/    READ-ONLY reference material. Never written to by /spec
                   or /build - only read, for conventions and for real
                   example roles to model new code on. Any folder with a
                   galaxy.yml (a source collection like cloud.aws_ops) or a
                   MANIFEST.json (an installed/built collection like
                   infra-support_assist-1.2.0) counts; its dotted name
                   (namespace.name) is read from that file, not guessed
                   from the directory name, since installed collections'
                   directory names don't always match it. Roles here are
                   "shipped" - the standard Ansible collection path,
                   addressable as <namespace>.<collection>.<role>.

  generated/       Everything /spec and /build actually produce, entirely
                   outside collections/. Layout:
                     generated/<dotted-collection-name>/<SPEC_ID>/
                       <SPEC_ID>.md
                       roles/<role_name>/...
                   The <dotted-collection-name> folder doesn't need to
                   already exist under collections/ - it may be a brand
                   new collection that hasn't been created there yet.
                   Roles here are "staged": real, complete code, but NOT
                   resolvable via the normal FQCN or usable as a
                   meta/main.yml dependency until a human *promotes* them
                   (copies into collections/<collection>/roles/) - staged
                   roles are flagged as such in the catalog so /spec and
                   /build never propose depending on one as if it were
                   already promoted.

For each role, pulls:
  - short_description + options from meta/argument_specs.yml
  - dependencies from meta/main.yml
  - a fallback one-line description from README.md if argument_specs.yml
    is missing entirely

Run this after adding/changing a role so /spec and /build see accurate
reuse candidates. Use whichever Python launcher exists on this platform -
`python3` on Linux/Mac/most containers, `python` on many Windows setups:

    python3 .claude/scripts/build_catalog.py
    python .claude/scripts/build_catalog.py

Requires PyYAML (`pip install pyyaml`) - nothing else outside the standard
library.
"""
import json
import re
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import yaml

ANSIBLE_ROOT = Path(__file__).resolve().parents[2]
COLLECTIONS_DIR = ANSIBLE_ROOT / "collections"
GENERATED_DIR = ANSIBLE_ROOT / "generated"
OUT_PATH = Path(__file__).resolve().parents[1] / "skills" / "_shared" / "catalog.md"

_UNDERLINE_RE = re.compile(r"^[=\-]{3,}$")


def _dotted_name_from_galaxy_yml(path: Path) -> Optional[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace")) or {}
    namespace, name = data.get("namespace"), data.get("name")
    return f"{namespace}.{name}" if namespace and name else None


def _dotted_name_from_manifest_json(path: Path) -> Optional[str]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    info = data.get("collection_info", {})
    namespace, name = info.get("namespace"), info.get("name")
    return f"{namespace}.{name}" if namespace and name else None


def discover_shipped_collections(collections_dir: Path) -> Dict[str, Path]:
    """Returns {dotted_name: collection_dir} for every real collection
    under (read-only) collections/."""
    if not collections_dir.exists():
        return {}
    found = {}
    for p in collections_dir.iterdir():
        if not p.is_dir():
            continue
        dotted = None
        if (p / "galaxy.yml").exists():
            dotted = _dotted_name_from_galaxy_yml(p / "galaxy.yml")
        elif (p / "MANIFEST.json").exists():
            dotted = _dotted_name_from_manifest_json(p / "MANIFEST.json")
        if dotted:
            found[dotted] = p
    return found


def discover_generated_collection_names(generated_dir: Path) -> List[str]:
    """Folder names directly under generated/ - each one IS a dotted
    collection name already (e.g. 'cloud.aws_ops'), chosen by /spec when it
    wrote the spec there; no galaxy.yml/MANIFEST.json involved since these
    are just organizational folders, not real collections (yet)."""
    if not generated_dir.exists():
        return []
    return sorted(p.name for p in generated_dir.iterdir() if p.is_dir())


def discover_shipped_roles(coll_dir: Path) -> Iterator[Path]:
    roles_dir = coll_dir / "roles"
    if roles_dir.exists():
        for role_dir in sorted(roles_dir.iterdir()):
            if role_dir.is_dir():
                yield role_dir


def discover_staged_roles(generated_coll_dir: Path) -> Iterator[Tuple[Path, str]]:
    """Yields (role_dir, spec_id) for every role staged under
    generated/<collection>/<SPEC_ID>/roles/*."""
    if not generated_coll_dir.exists():
        return
    for spec_dir in sorted(generated_coll_dir.iterdir()):
        staged_roles_dir = spec_dir / "roles"
        if spec_dir.is_dir() and staged_roles_dir.exists():
            for role_dir in sorted(staged_roles_dir.iterdir()):
                if role_dir.is_dir():
                    yield role_dir, spec_dir.name


def first_paragraph(readme_path: Path) -> str:
    if not readme_path.exists():
        return ""
    lines = readme_path.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        # setext-style header: "Title" followed by a line of ===== or -----
        if i + 1 < len(lines) and _UNDERLINE_RE.match(lines[i + 1].strip()):
            i += 2
            continue
        break
    para = []
    while i < len(lines) and lines[i].strip() and not _UNDERLINE_RE.match(lines[i].strip()):
        para.append(lines[i].strip())
        i += 1
    return " ".join(para)


def _table_cell(value) -> str:
    """Flatten a value to a single markdown-table-safe line: collapse
    whitespace/newlines and escape `|` so multi-line Jinja default
    expressions (which often contain both) don't break the table."""
    text = " ".join(str(value).split())
    text = text.replace("|", "\\|")
    if len(text) > 80:
        text = text[:77] + "..."
    return text


def load_yaml(path: Path):
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"__error__": str(exc)}


def scan_role(dotted_collection: str, role_dir: Path, staged_under: Optional[str] = None) -> dict:
    role_name = role_dir.name
    argspecs = load_yaml(role_dir / "meta" / "argument_specs.yml")
    meta_main = load_yaml(role_dir / "meta" / "main.yml")

    options = []
    short_desc = ""
    if argspecs and "argument_specs" in argspecs:
        main_spec = argspecs["argument_specs"].get("main", {})
        short_desc = main_spec.get("short_description", "")
        for opt_name, opt in (main_spec.get("options") or {}).items():
            desc = opt.get("description")
            if isinstance(desc, list):
                desc = " ".join(desc)
            options.append({
                "name": opt_name,
                "type": opt.get("type", "str"),
                "required": opt.get("required", False),
                "default": opt.get("default", None),
                "choices": opt.get("choices", None),
                "description": desc or "",
            })

    deps = []
    if meta_main and isinstance(meta_main.get("dependencies"), list):
        for d in meta_main["dependencies"]:
            deps.append(d.get("role", str(d)) if isinstance(d, dict) else str(d))

    return {
        "collection": dotted_collection,
        "role": role_name,
        "short_desc": short_desc or first_paragraph(role_dir / "README.md")[:200],
        "options": options,
        "deps": deps,
        "has_argspecs": argspecs is not None,
        "staged_under": staged_under,
    }


def main() -> None:
    shipped = discover_shipped_collections(COLLECTIONS_DIR)
    generated_names = discover_generated_collection_names(GENERATED_DIR)
    all_collection_names = sorted(set(shipped) | set(generated_names))

    rows = []
    for dotted in all_collection_names:
        if dotted in shipped:
            for role_dir in discover_shipped_roles(shipped[dotted]):
                rows.append(scan_role(dotted, role_dir))
        generated_coll_dir = GENERATED_DIR / dotted
        if generated_coll_dir.exists():
            for role_dir, spec_id in discover_staged_roles(generated_coll_dir):
                rows.append(scan_role(dotted, role_dir, staged_under=spec_id))

    out = [
        "# Role Catalog\n\n",
        "Auto-generated by `.claude/scripts/build_catalog.py` from `meta/argument_specs.yml`, "
        "`meta/main.yml`, and `README.md` across every collection under the read-only "
        "`collections/` tree, plus every role staged under `generated/`. "
        "**Do not hand-edit** - regenerate instead after adding/changing a role.\n\n",
        "`/spec` and `/build` read this file to find existing roles to reuse or "
        "extend before proposing anything new.\n\n",
    ]

    for coll in all_collection_names:
        coll_rows = [r for r in rows if r["collection"] == coll]
        if not coll_rows:
            continue
        out.append(f"## {coll}\n\n")
        if coll not in shipped:
            out.append(
                "_(no collection named this exists yet under `collections/` - "
                "every role below is staged under `generated/`)_\n\n"
            )
        for r in coll_rows:
            out.append(f"### `{coll}.{r['role']}`\n\n")
            if r["staged_under"]:
                out.append(
                    f"**STAGED** under spec `{r['staged_under']}` "
                    f"(`generated/{coll}/{r['staged_under']}/roles/{r['role']}/`) - "
                    "outside the read-only `collections/` tree, so it is "
                    "**not** yet resolvable as a normal "
                    f"`{coll}.{r['role']}` role reference or usable as a "
                    "`meta/main.yml` dependency until a human promotes it "
                    f"(copies it into `collections/{coll}/roles/{r['role']}/`).\n\n"
                )
            out.append(f"{r['short_desc']}\n\n")
            if r["deps"]:
                out.append(f"**Depends on:** {', '.join('`' + d + '`' for d in r['deps'])}\n\n")
            if r["options"]:
                out.append("| variable | type | required | default | choices |\n")
                out.append("|---|---|---|---|---|\n")
                for o in r["options"]:
                    choices = _table_cell(", ".join(str(c) for c in o["choices"])) if o["choices"] else ""
                    default = "" if o["default"] is None else _table_cell(o["default"])
                    out.append(f"| `{o['name']}` | {o['type']} | {o['required']} | {default} | {choices} |\n")
                out.append("\n")
            else:
                out.append("_(no meta/argument_specs.yml - variables undocumented in machine-readable form; "
                            "check README.md or treat as a candidate for backfilling one)_\n\n")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("".join(out), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(rows)} roles across {len(all_collection_names)} collections: {', '.join(all_collection_names)})")


if __name__ == "__main__":
    main()
