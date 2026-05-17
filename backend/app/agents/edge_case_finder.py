from typing import Dict, List, Any, Set
import ast


class EdgeCaseFinderAgent:
    """
    Intelligent edge-case detection engine.
    """

    MAX_EDGE_CASES = 12

    def __init__(self):
        pass

    # ==========================================================
    # MAIN ENTRY
    # ==========================================================

    def find_edge_cases(
        self,
        function_info: Dict[str, Any],
        file_path: str
    ) -> List[Dict[str, Any]]:

        edge_cases = []

        edge_cases.extend(
            self._find_null_cases(function_info)
        )

        edge_cases.extend(
            self._find_empty_input_cases(function_info)
        )

        edge_cases.extend(
            self._find_boundary_cases(function_info)
        )

        edge_cases.extend(
            self._find_type_mismatch_cases(function_info)
        )

        edge_cases.extend(
            self._find_exception_cases(function_info)
        )

        edge_cases.extend(
            self._find_concurrency_cases(function_info)
        )

        edge_cases.extend(
            self._find_api_failure_cases(function_info)
        )

        # IMPORTANT:
        # Remove duplicates aggressively

        edge_cases = self._deduplicate_cases(
            edge_cases
        )

        return edge_cases[:self.MAX_EDGE_CASES]

    # ==========================================================
    # NULL CASES
    # ==========================================================

    def _find_null_cases(
        self,
        function_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        cases = []

        args = function_info.get(
            "args",
            []
        ) or []

        for arg in args:

            arg_name = arg.get(
                "name",
                "argument"
            )

            cases.append({
                "type": "null_input",
                "argument": arg_name,
                "description": (
                    f"Test None input for "
                    f"{arg_name}"
                ),
                "priority": 9
            })

        return cases

    # ==========================================================
    # EMPTY INPUTS
    # ==========================================================

    def _find_empty_input_cases(
        self,
        function_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        cases = []

        args = function_info.get(
            "args",
            []
        ) or []

        collection_keywords = [
            "list",
            "items",
            "array",
            "dict",
            "map",
            "data",
            "text",
            "string",
            "content",
            "values"
        ]

        for arg in args:

            arg_name = (
                arg.get("name", "")
                .lower()
            )

            if any(
                keyword in arg_name
                for keyword in collection_keywords
            ):

                cases.append({
                    "type": "empty_input",
                    "argument": arg_name,
                    "description": (
                        f"Test empty value "
                        f"for {arg_name}"
                    ),
                    "priority": 7
                })

        return cases

    # ==========================================================
    # BOUNDARY CASES
    # ==========================================================

    def _find_boundary_cases(
        self,
        function_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        cases = []

        args = function_info.get(
            "args",
            []
        ) or []

        numeric_keywords = [
            "count",
            "size",
            "index",
            "num",
            "limit",
            "price",
            "quantity",
            "amount",
            "age",
            "score",
            "rate"
        ]

        for arg in args:

            arg_name = (
                arg.get("name", "")
                .lower()
            )

            if any(
                keyword in arg_name
                for keyword in numeric_keywords
            ):

                cases.append({
                    "type": "boundary",
                    "argument": arg_name,
                    "description": (
                        f"Test zero, negative, "
                        f"and max values "
                        f"for {arg_name}"
                    ),
                    "priority": 8
                })

        return cases

    # ==========================================================
    # TYPE MISMATCH
    # ==========================================================

    def _find_type_mismatch_cases(
        self,
        function_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        cases = []

        args = function_info.get(
            "args",
            []
        ) or []

        for arg in args:

            arg_name = arg.get(
                "name",
                "argument"
            )

            cases.append({
                "type": "type_mismatch",
                "argument": arg_name,
                "description": (
                    f"Test invalid type "
                    f"for {arg_name}"
                ),
                "priority": 8
            })

        return cases

    # ==========================================================
    # EXCEPTION ANALYSIS
    # ==========================================================

    def _find_exception_cases(
        self,
        function_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        cases = []

        source_code = function_info.get(
            "source_code",
            ""
        )

        if not source_code:

            return cases

        try:

            tree = ast.parse(source_code)

            found_type_error = False
            found_value_error = False

            for node in ast.walk(tree):

                if isinstance(node, ast.Raise):

                    exception_text = ast.dump(node)

                    if (
                        "TypeError"
                        in exception_text
                        and not found_type_error
                    ):

                        found_type_error = True

                        cases.append({
                            "type": "type_error",
                            "description": (
                                "Function raises "
                                "TypeError"
                            ),
                            "priority": 10
                        })

                    if (
                        "ValueError"
                        in exception_text
                        and not found_value_error
                    ):

                        found_value_error = True

                        cases.append({
                            "type": "value_error",
                            "description": (
                                "Function raises "
                                "ValueError"
                            ),
                            "priority": 10
                        })

        except Exception:
            pass

        return cases

    # ==========================================================
    # CONCURRENCY
    # ==========================================================

    def _find_concurrency_cases(
        self,
        function_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        cases = []

        text = (
            function_info.get(
                "docstring",
                ""
            )
            + " "
            + function_info.get(
                "name",
                ""
            )
        ).lower()

        concurrency_keywords = [
            "thread",
            "async",
            "parallel",
            "concurrent",
            "await"
        ]

        if any(
            keyword in text
            for keyword in concurrency_keywords
        ):

            cases.append({
                "type": "concurrency",
                "description": (
                    "Test concurrent execution"
                ),
                "priority": 5
            })

        return cases

    # ==========================================================
    # API FAILURES
    # ==========================================================

    def _find_api_failure_cases(
        self,
        function_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        cases = []

        text = (
            function_info.get(
                "docstring",
                ""
            )
            + " "
            + function_info.get(
                "name",
                ""
            )
        ).lower()

        api_keywords = [
            "api",
            "request",
            "http",
            "fetch",
            "client",
            "endpoint"
        ]

        if any(
            keyword in text
            for keyword in api_keywords
        ):

            cases.append({
                "type": "api_failure",
                "description": (
                    "Test failed API request"
                ),
                "priority": 6
            })

        return cases

    # ==========================================================
    # DEDUPLICATION
    # ==========================================================

    def _deduplicate_cases(
        self,
        edge_cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        unique_cases = []

        seen: Set[str] = set()

        for case in edge_cases:

            signature = (
                f"{case.get('type')}::"
                f"{case.get('argument', '')}::"
                f"{case.get('description', '')}"
            )

            if signature in seen:
                continue

            seen.add(signature)

            unique_cases.append(case)

        unique_cases.sort(
            key=lambda x: x.get(
                "priority",
                0
            ),
            reverse=True
        )

        return unique_cases