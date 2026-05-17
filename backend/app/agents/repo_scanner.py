import os
import re
import ast
import zipfile
import subprocess

from typing import Dict, List, Any
from collections import defaultdict


class RepoScannerAgent:
    """
    Repository scanner and analyzer.

    Features:
    - Repository tree scanning
    - Language detection
    - Python AST extraction
    - JavaScript regex extraction
    - Dependency-safe traversal
    """

    LANGUAGE_EXTENSIONS = {
        "python": [".py"],
        "javascript": [
            ".js",
            ".jsx",
            ".ts",
            ".tsx"
        ],
        "java": [".java"],
        "cpp": [
            ".cpp",
            ".cc",
            ".h"
        ],
        "go": [".go"],
        "rust": [".rs"],
    }

    IGNORE_DIRS = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        ".idea",
        ".pytest_cache",
        "generated_tests",
        "coverage",
        ".next",
        ".turbo",
        ".cache",
    }

    IGNORE_FILES = {
        ".DS_Store"
    }

    MAX_FILE_SIZE = 2 * 1024 * 1024

    def __init__(self, repo_path: str):

        self.repo_path = os.path.abspath(
            repo_path
        )

        self.file_tree = {}

        self.language_stats = defaultdict(int)

        self.files = []

    # ==========================================================
    # MAIN SCAN
    # ==========================================================

    def scan(self) -> Dict[str, Any]:
        """
        Scan repository safely.
        """

        self.files = []

        self.language_stats.clear()

        if not os.path.exists(
            self.repo_path
        ):

            return {
                "file_tree": {},
                "languages": {},
                "files": [],
                "total_files": 0,
                "error": (
                    "Repository path does not exist"
                )
            }

        self.file_tree = self._build_file_tree(
            self.repo_path
        )

        self._detect_languages()

        return {
            "file_tree": self.file_tree,
            "languages": dict(
                self.language_stats
            ),
            "files": sorted(
                list(set(self.files))
            ),
            "total_files": len(
                list(set(self.files))
            ),
        }

    # ==========================================================
    # BUILD FILE TREE
    # ==========================================================

    def _build_file_tree(
        self,
        path: str,
        relative_path: str = ""
    ) -> Dict[str, Any]:

        tree = {}

        try:

            items = sorted(
                os.listdir(path)
            )

        except Exception:

            return tree

        for item in items:

            try:

                # ----------------------------------------------
                # IGNORE RULES
                # ----------------------------------------------

                if (
                    item.startswith(".")
                    or item in self.IGNORE_DIRS
                    or item in self.IGNORE_FILES
                ):

                    continue

                item_path = os.path.join(
                    path,
                    item
                )

                if os.path.islink(
                    item_path
                ):

                    continue

                normalized_relative = (
                    os.path.join(
                        relative_path,
                        item
                    )
                    if relative_path
                    else item
                )

                normalized_relative = (
                    normalized_relative.replace(
                        "\\",
                        "/"
                    )
                )

                # ----------------------------------------------
                # DIRECTORY
                # ----------------------------------------------

                if os.path.isdir(item_path):

                    subtree = self._build_file_tree(
                        item_path,
                        normalized_relative
                    )

                    tree[item] = subtree

                # ----------------------------------------------
                # FILE
                # ----------------------------------------------

                else:

                    if not os.path.isfile(
                        item_path
                    ):

                        continue

                    try:

                        file_size = os.path.getsize(
                            item_path
                        )

                    except Exception:

                        continue

                    if (
                        file_size <= 0
                        or file_size >
                        self.MAX_FILE_SIZE
                    ):

                        continue

                    if self._is_binary_file(
                        item_path
                    ):

                        continue

                    tree[item] = {
                        "type": "file",
                        "path": normalized_relative,
                        "size": file_size
                    }

                    self.files.append(
                        normalized_relative
                    )

            except Exception:

                continue

        return tree

    # ==========================================================
    # BINARY FILE CHECK
    # ==========================================================

    def _is_binary_file(
        self,
        file_path: str
    ) -> bool:

        try:

            with open(
                file_path,
                "rb"
            ) as f:

                chunk = f.read(1024)

            return b"\0" in chunk

        except Exception:

            return True

    # ==========================================================
    # DETECT LANGUAGES
    # ==========================================================

    def _detect_languages(self):

        self.language_stats.clear()

        for file_path in self.files:

            _, ext = os.path.splitext(
                file_path
            )

            ext = ext.lower()

            for (
                language,
                extensions
            ) in self.LANGUAGE_EXTENSIONS.items():

                if ext in extensions:

                    self.language_stats[
                        language
                    ] += 1

                    break

    # ==========================================================
    # EXTRACT FUNCTIONS
    # ==========================================================

    def extract_functions(
        self
    ) -> List[Dict[str, Any]]:

        functions = []

        for file_path in self.files:

            full_path = os.path.join(
                self.repo_path,
                file_path
            )

            ext = os.path.splitext(
                file_path
            )[1].lower()

            try:

                if ext == ".py":

                    functions.extend(
                        self._extract_python_functions(
                            full_path,
                            file_path
                        )
                    )

                elif ext in [
                    ".js",
                    ".jsx",
                    ".ts",
                    ".tsx"
                ]:

                    functions.extend(
                        self._extract_js_functions(
                            full_path,
                            file_path
                        )
                    )

            except Exception as e:

                print(
                    f"[SCANNER ERROR] "
                    f"{file_path}: {e}"
                )

        return functions

    # ==========================================================
    # PYTHON FUNCTION EXTRACTION
    # ==========================================================

    def _extract_python_functions(
        self,
        file_path: str,
        relative_path: str
    ) -> List[Dict[str, Any]]:

        functions = []

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                content = f.read()

            tree = ast.parse(content)

            source_lines = content.splitlines()

            # ----------------------------------------------
            # TOP LEVEL ONLY
            # ----------------------------------------------

            for node in tree.body:

                # ------------------------------------------
                # FUNCTIONS
                # ------------------------------------------

                if isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef
                    )
                ):

                    functions.append(
                        self._build_python_function(
                            node,
                            relative_path,
                            source_lines
                        )
                    )

                # ------------------------------------------
                # CLASSES
                # ------------------------------------------

                elif isinstance(
                    node,
                    ast.ClassDef
                ):

                    functions.append({
                        "type": "class",
                        "name": node.name,
                        "file": relative_path,
                        "line": node.lineno,
                        "language": "python"
                    })

                    # --------------------------------------
                    # CLASS METHODS
                    # --------------------------------------

                    for class_node in node.body:

                        if isinstance(
                            class_node,
                            (
                                ast.FunctionDef,
                                ast.AsyncFunctionDef
                            )
                        ):

                            method = (
                                self._build_python_function(
                                    class_node,
                                    relative_path,
                                    source_lines
                                )
                            )

                            method["class_name"] = (
                                node.name
                            )

                            method["type"] = (
                                "method"
                            )

                            functions.append(
                                method
                            )

        except Exception as e:

            print(
                f"[PYTHON PARSE ERROR] "
                f"{file_path}: {e}"
            )

        return functions

    # ==========================================================
    # BUILD PYTHON FUNCTION
    # ==========================================================

    def _build_python_function(
        self,
        node,
        relative_path,
        source_lines
    ) -> Dict[str, Any]:

        start_line = node.lineno

        end_line = getattr(
            node,
            "end_lineno",
            start_line + 20
        )

        function_source = "\n".join(
            source_lines[
                start_line - 1:end_line
            ]
        )

        args = []

        for arg in node.args.args:

            if arg.arg == "self":
                continue

            args.append({
                "name": arg.arg
            })

        return {
            "type": "function",
            "name": node.name,
            "file": relative_path,
            "line": start_line,
            "language": "python",
            "args": args,
            "source": function_source,
            "context": function_source,
        }

    # ==========================================================
    # JAVASCRIPT EXTRACTION
    # ==========================================================

    def _extract_js_functions(
        self,
        file_path: str,
        relative_path: str
    ) -> List[Dict[str, Any]]:

        functions = []

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                content = f.read()

            patterns = [

                r'function\s+(\w+)\s*\((.*?)\)',

                r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>',

                r'let\s+(\w+)\s*=\s*\((.*?)\)\s*=>',

                r'var\s+(\w+)\s*=\s*\((.*?)\)\s*=>',

                r'export\s+function\s+(\w+)\s*\((.*?)\)',
            ]

            seen = set()

            for pattern in patterns:

                for match in re.finditer(
                    pattern,
                    content,
                    re.MULTILINE
                ):

                    func_name = match.group(1)

                    if func_name in seen:
                        continue

                    seen.add(func_name)

                    raw_args = match.group(2)

                    args = []

                    for arg in raw_args.split(","):

                        cleaned = arg.strip()

                        if cleaned:

                            args.append({
                                "name": cleaned
                            })

                    functions.append({
                        "type": "function",
                        "name": func_name,
                        "file": relative_path,
                        "language": "javascript",
                        "args": args,
                    })

            # ----------------------------------------------
            # CLASSES
            # ----------------------------------------------

            class_pattern = (
                r'class\s+(\w+)'
            )

            for match in re.finditer(
                class_pattern,
                content
            ):

                functions.append({
                    "type": "class",
                    "name": match.group(1),
                    "file": relative_path,
                    "language": "javascript"
                })

        except Exception as e:

            print(
                f"[JS PARSE ERROR] "
                f"{file_path}: {e}"
            )

        return functions

    # ==========================================================
    # ZIP EXTRACTION
    # ==========================================================

    @staticmethod
    def extract_from_zip(
        zip_path: str,
        extract_to: str
    ) -> str:

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_ref:

            for member in zip_ref.namelist():

                normalized = os.path.normpath(
                    member
                )

                if (
                    normalized.startswith("..")
                    or os.path.isabs(
                        normalized
                    )
                ):

                    continue

                zip_ref.extract(
                    member,
                    extract_to
                )

        return extract_to

    # ==========================================================
    # GITHUB CLONE
    # ==========================================================

    @staticmethod
    def clone_from_github(
        repo_url: str,
        clone_to: str
    ) -> str:

        result = subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                repo_url,
                clone_to
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"Git clone failed:\n"
                f"{result.stderr}"
            )

        return clone_to