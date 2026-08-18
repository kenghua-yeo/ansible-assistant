"""
Trim collections/ down to what /spec, /build, /review, and /explain
actually reference, removing CI/VCS/packaging cruft that's pure noise for
an agent exploring the tree - and, worse, something it could mistake for
relevant reference material.

DESTRUCTIVE. Defaults to a dry run - nothing is deleted unless --apply is
passed. Always prints exactly what would be removed and how much space it
reclaims before doing anything.

Kept (this is what the skills actually read - see conventions.md,
catalog.md, spec-template.md, explain/SKILL.md):
  galaxy.yml / MANIFEST.json   - collection identity (build_catalog.py)
  meta/                         - collection metadata
  roles/                        - THE reference material (/build)
  extensions/patterns/          - AAP pattern packaging example, referenced
                                   by name in spec-template.md and explain/SKILL.md
  README.md, LICENSE*, COPYING* - left alone regardless of size; small,
                                   and licensing files aren't this script's
                                   business even under an aggressive trim

Removed (present in some or all of the reference collections here; none
of it is read by any skill):
  .git/, .github/                - VCS internals & CI workflows
  .gitignore, .gitattributes
  .config/                       - local tool config (lint configs etc.)
  changelogs/                    - changelog fragment automation
  docs/                          - docsite/RST source, redundant with README.md
  tests/                         - integration test targets (not referenced
                                    by any skill's documented workflow)
  plugins/                       - custom modules/filters/module_utils; not
                                    scanned by catalog.md or read by /build,
                                    which models role STRUCTURE, not module
                                    internals
  extensions/eda/                - Event-Driven Ansible rulebooks, out of
                                    scope for this workflow (extensions/patterns/
                                    is a sibling and is explicitly kept)
  tmt/                           - Testing Farm metadata
  CHANGELOG.rst, FILES.json, bindep.txt, collection_release.yml,
  execution-environment.yml, mypy-*.ini, pyproject-*.toml,
  packit-ci-*.fmf, lsr_role2coll_extra_script-*
                                  - assorted CI/build/packaging tooling

Run:
    python3 .claude/scripts/trim_collections.py            # dry run (default, safe)
    python3 .claude/scripts/trim_collections.py --apply     # actually delete
"""
import argparse
import os
import shutil
import stat
import sys
from pathlib import Path

ANSIBLE_ROOT = Path(__file__).resolve().parents[2]
COLLECTIONS_DIR = ANSIBLE_ROOT / "collections"

REMOVE_DIRS = [
    ".git", ".github", ".config", "changelogs", "docs", "tests", "plugins", "tmt",
]
REMOVE_EXTENSIONS_SUBDIRS = ["eda"]  # under extensions/ - patterns/ is explicitly kept

REMOVE_FILE_NAMES = {
    ".gitignore", ".gitattributes", "CHANGELOG.rst", "FILES.json",
    "bindep.txt", "collection_release.yml", "execution-environment.yml",
}
REMOVE_FILE_GLOBS = [
    "mypy-*.ini", "pyproject-*.toml", "packit-ci-*.fmf",
    "lsr_role2coll_extra_script-*",
]


def _force_remove_readonly(func, path, exc_info_or_exc):
    """git marks pack/index files read-only, which trips up shutil.rmtree
    on Windows (PermissionError). Clear the read-only bit and retry."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rmtree(path: Path) -> None:
    # Python 3.12 renamed the rmtree error-callback kwarg from onerror to
    # onexc; support both so this runs on whatever's installed.
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_force_remove_readonly)
    else:
        shutil.rmtree(path, onerror=_force_remove_readonly)


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def discover_collection_dirs(collections_dir: Path):
    if not collections_dir.exists():
        return []
    return sorted(p for p in collections_dir.iterdir() if p.is_dir())


def find_targets(coll_dir: Path):
    """Yields (path, kind) for everything in this collection slated for
    removal. kind is 'dir' or 'file', for reporting only."""
    for name in REMOVE_DIRS:
        p = coll_dir / name
        if p.is_dir():
            yield p, "dir"

    ext_dir = coll_dir / "extensions"
    if ext_dir.is_dir():
        for name in REMOVE_EXTENSIONS_SUBDIRS:
            p = ext_dir / name
            if p.is_dir():
                yield p, "dir"

    for item in coll_dir.iterdir():
        if not item.is_file():
            continue
        if item.name in REMOVE_FILE_NAMES or any(item.match(g) for g in REMOVE_FILE_GLOBS):
            yield item, "file"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="Actually delete. Without this flag, only reports what would be removed.")
    args = parser.parse_args()

    collections = discover_collection_dirs(COLLECTIONS_DIR)
    if not collections:
        print(f"No collections found under {COLLECTIONS_DIR}")
        return

    grand_total = 0
    git_removed = []

    for coll_dir in collections:
        targets = sorted(find_targets(coll_dir), key=lambda t: t[0].name)
        if not targets:
            continue
        coll_total = 0
        print(f"\n{coll_dir.name}/")
        for path, kind in targets:
            size = dir_size(path) if kind == "dir" else path.stat().st_size
            coll_total += size
            tag = "[dir] " if kind == "dir" else "[file]"
            print(f"  {tag} {path.relative_to(coll_dir)}  ({human_size(size)})")
            if kind == "dir" and path.name == ".git":
                git_removed.append(coll_dir.name)
            if args.apply:
                rmtree(path) if kind == "dir" else path.unlink()
        grand_total += coll_total
        print(f"  -> {human_size(coll_total)} {'removed' if args.apply else 'would be removed'}")

    verb = "Removed" if args.apply else "Would remove"
    print(f"\n{verb} {human_size(grand_total)} total across {len(collections)} collections.")

    if not args.apply:
        print("\nDry run only - nothing was deleted. Re-run with --apply to actually remove these.")
    elif git_removed:
        print(
            "\nNote: .git/ was removed from: " + ", ".join(git_removed) + ". "
            "Those collections can no longer be updated with `git pull` - "
            "re-clone from their origin if you need to sync with upstream again."
        )

    print(
        "\nAfter applying, regenerate the catalog (it doesn't scan anything "
        "removed here, so this is just hygiene, not required for correctness):"
        "\n    python3 .claude/scripts/build_catalog.py"
    )


if __name__ == "__main__":
    main()
