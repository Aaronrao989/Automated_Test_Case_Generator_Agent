import ast
import re

from typing import (
    Dict,
    List,
    Any,
    Optional
)


class CodeUnderstandingAgent:
    """
    Deep code understanding agent.

    Extracts:
    - Functions
    - Classes
    - Imports
    - Type hints
    - Return annotations
    - Exceptions
    - Complexity
    - External dependencies
    - Intent inference
    - Async behavior
    """

    def __init__(
        self,
        repo_path: str
    ):

        self.repo_path = repo_path

    # ==========================================================
    # MAIN ENTRY
    # ==========================================================

    def analyze_function(
        self,
        file_path: str,
        language: str = "python"
    ) -> Dict[str, Any]:

        if language == "python":

            return self._analyze_python_file(
                file_path
            )

        if language == "javascript":

            return self._analyze_js_file(
                file_path
            )

        return {}

    # ==========================================================
    # PYTHON ANALYSIS
    # ==========================================================

    def _analyze_python_file(
        self,
        file_path: str
    ) -> Dict[str, Any]:

        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "docstrings": {},
        }

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

            for node in ast.walk(tree):

                # --------------------------------------------------
                # FUNCTIONS
                # --------------------------------------------------

                if isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef
                    )
                ):

                    func_info = (
                        self._extract_python_function_info(
                            node,
                            source_lines
                        )
                    )

                    analysis["functions"].append(
                        func_info
                    )

                # --------------------------------------------------
                # CLASSES
                # --------------------------------------------------

                elif isinstance(
                    node,
                    ast.ClassDef
                ):

                    class_info = {
                        "name": node.name,
                        "lineno": node.lineno,
                        "docstring": (
                            ast.get_docstring(node)
                        ),
                        "methods": [],
                        "decorators": [
                            self._safe_unparse(d)
                            for d in node.decorator_list
                        ]
                    }

                    for item in node.body:

                        if isinstance(
                            item,
                            (
                                ast.FunctionDef,
                                ast.AsyncFunctionDef
                            )
                        ):

                            class_info["methods"].append(
                                item.name
                            )

                    analysis["classes"].append(
                        class_info
                    )

                # --------------------------------------------------
                # IMPORTS
                # --------------------------------------------------

                elif isinstance(node, ast.Import):

                    for alias in node.names:

                        analysis["imports"].append(
                            alias.name
                        )

                elif isinstance(
                    node,
                    ast.ImportFrom
                ):

                    module = (
                        node.module
                        if node.module
                        else ""
                    )

                    analysis["imports"].append(
                        f"from {module} import ..."
                    )

        except Exception as e:

            print(
                f"[CodeUnderstanding] "
                f"Python analysis failed: {e}"
            )

        return analysis

    # ==========================================================
    # FUNCTION EXTRACTION
    # ==========================================================

    def _extract_python_function_info(
        self,
        node,
        source_lines: List[str]
    ) -> Dict[str, Any]:

        args = []

        for arg in node.args.args:

            args.append({
                "name": arg.arg,
                "type": self._extract_annotation(
                    arg.annotation
                )
            })

        defaults = []

        for default in node.args.defaults:

            defaults.append(
                self._safe_unparse(default)
            )

        return_annotation = (
            self._extract_annotation(
                node.returns
            )
        )

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

        raised_exceptions = (
            self._extract_raised_exceptions(
                node
            )
        )

        external_calls = (
            self._extract_external_calls(
                node
            )
        )

        return {

            "name": node.name,

            "lineno": start_line,

            "end_lineno": end_line,

            "is_async": isinstance(
                node,
                ast.AsyncFunctionDef
            ),

            "args": args,

            "defaults": defaults,

            "docstring": (
                ast.get_docstring(node)
            ),

            "complexity": (
                self._estimate_complexity(node)
            ),

            "returns_type": (
                return_annotation
            ),

            "decorators": [
                self._safe_unparse(d)
                for d in node.decorator_list
            ],

            "raises": raised_exceptions,

            "external_calls": external_calls,

            "intent": self.infer_intent({
                "name": node.name,
                "docstring": (
                    ast.get_docstring(node)
                )
            }),

            "source_code": function_source
        }

    # ==========================================================
    # JS ANALYSIS
    # ==========================================================

    def _analyze_js_file(
        self,
        file_path: str
    ) -> Dict[str, Any]:

        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
        }

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                content = f.read()

            # --------------------------------------------------
            # FUNCTIONS
            # --------------------------------------------------

            patterns = [

                r'function\s+(\w+)\s*\((.*?)\)',

                r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>',

                r'export\s+function\s+(\w+)\s*\((.*?)\)'
            ]

            for pattern in patterns:

                for match in re.finditer(
                    pattern,
                    content
                ):

                    args_raw = (
                        match.group(2)
                        if len(match.groups()) > 1
                        else ""
                    )

                    args = []

                    for arg in args_raw.split(","):

                        arg = arg.strip()

                        if arg:

                            args.append({
                                "name": arg
                            })

                    analysis["functions"].append({

                        "name": match.group(1),

                        "args": args,

                        "intent": self.infer_intent({
                            "name": match.group(1)
                        }),

                        "complexity": 1
                    })

            # --------------------------------------------------
            # CLASSES
            # --------------------------------------------------

            for match in re.finditer(
                r'class\s+(\w+)',
                content
            ):

                analysis["classes"].append({
                    "name": match.group(1)
                })

            # --------------------------------------------------
            # IMPORTS
            # --------------------------------------------------

            for match in re.finditer(
                r'import\s+.*?from\s+["\']([^"\']+)["\']',
                content
            ):

                analysis["imports"].append(
                    match.group(1)
                )

        except Exception as e:

            print(
                f"[CodeUnderstanding] "
                f"JS analysis failed: {e}"
            )

        return analysis

    # ==========================================================
    # COMPLEXITY
    # ==========================================================

    def _estimate_complexity(
        self,
        node
    ) -> int:

        complexity = 1

        for child in ast.walk(node):

            if isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.ExceptHandler,
                    ast.BoolOp,
                    ast.With,
                    ast.Try
                )
            ):

                complexity += 1

        return complexity

    # ==========================================================
    # EXCEPTIONS
    # ==========================================================

    def _extract_raised_exceptions(
        self,
        node
    ) -> List[str]:

        exceptions = []

        for child in ast.walk(node):

            if isinstance(child, ast.Raise):

                if child.exc:

                    exceptions.append(
                        self._safe_unparse(
                            child.exc
                        )
                    )

        return exceptions

    # ==========================================================
    # EXTERNAL CALLS
    # ==========================================================

    def _extract_external_calls(
        self,
        node
    ) -> List[str]:

        calls = []

        for child in ast.walk(node):

            if isinstance(child, ast.Call):

                func = child.func

                if isinstance(func, ast.Name):

                    calls.append(func.id)

                elif isinstance(
                    func,
                    ast.Attribute
                ):

                    calls.append(
                        func.attr
                    )

        return list(set(calls))

    # ==========================================================
    # TYPE ANNOTATIONS
    # ==========================================================

    def _extract_annotation(
        self,
        annotation
    ) -> Optional[str]:

        if annotation is None:

            return None

        return self._safe_unparse(
            annotation
        )

    # ==========================================================
    # SAFE AST UNPARSE
    # ==========================================================

    def _safe_unparse(
        self,
        node
    ) -> str:

        try:

            return ast.unparse(node)

        except Exception:

            return str(node)

    # ==========================================================
    # INTENT INFERENCE
    # ==========================================================

    def infer_intent(
        self,
        function_info: Dict[str, Any]
    ) -> str:

        docstring = (
            function_info.get(
                "docstring"
            ) or ""
        )

        name = (
            function_info.get(
                "name"
            ) or ""
        )

        if docstring:

            return (
                docstring
                .strip()
                .split("\n")[0]
            )

        lowered = name.lower()

        mappings = {

            "get_": "Retrieves data",

            "set_": "Updates state",

            "is_": "Validates condition",

            "has_": "Checks existence",

            "calculate_": "Performs calculation",

            "process_": "Processes input data",

            "create_": "Creates resource",

            "delete_": "Deletes resource",

            "fetch_": "Fetches external data",

            "validate_": "Validates input",

            "convert_": "Converts data",

            "parse_": "Parses structured input"
        }

        for prefix, meaning in mappings.items():

            if lowered.startswith(prefix):

                return meaning

        return "General purpose function"