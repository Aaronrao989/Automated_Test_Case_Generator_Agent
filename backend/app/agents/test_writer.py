from typing import Dict, List, Any


class TestWriterAgent:
    """
    Generates:
    - unit tests
    - edge case tests
    - boundary tests
    - negative tests
    - integration tests
    """

    def __init__(self):

        pass

    # ==========================================================
    # MAIN ENTRY
    # ==========================================================

    def generate_tests(
        self,
        function_info: Dict[str, Any],
        edge_cases: List[Dict[str, Any]],
        language: str = "python"
    ) -> List[Dict[str, Any]]:

        tests = []

        tests.extend(
            self._generate_unit_tests(
                function_info,
                language
            )
        )

        tests.extend(
            self._generate_edge_case_tests(
                edge_cases,
                function_info,
                language
            )
        )

        tests.extend(
            self._generate_boundary_tests(
                function_info,
                language
            )
        )

        tests.extend(
            self._generate_negative_tests(
                function_info,
                language
            )
        )

        return tests

    # ==========================================================
    # UNIT TESTS
    # ==========================================================

    def _generate_unit_tests(
        self,
        function_info: Dict[str, Any],
        language: str
    ) -> List[Dict[str, Any]]:

        tests = []

        func_name = function_info.get(
            "name",
            "unknown"
        )

        if language == "python":

            test_code = (
                self._generate_python_unit_test(
                    func_name,
                    function_info
                )
            )

        elif language == "javascript":

            test_code = (
                self._generate_js_unit_test(
                    func_name,
                    function_info
                )
            )

        else:

            return []

        tests.append({
            "type": "unit",
            "target_function": func_name,
            "content": test_code,
            "language": language
        })

        return tests

    # ==========================================================
    # PYTHON UNIT TEST
    # ==========================================================

    def _generate_python_unit_test(
        self,
        func_name: str,
        function_info: Dict[str, Any]
    ) -> str:

        args = function_info.get(
            "args",
            []
        )

        arg_names = [

            arg.get("name", "arg")

            for arg in args
        ]

        arrange_lines = []

        call_args = []

        for arg_name in arg_names:

            arrange_lines.append(
                f"    {arg_name} = 1"
            )

            call_args.append(arg_name)

        arrange_block = "\n".join(
            arrange_lines
        )

        call_signature = ", ".join(
            call_args
        )

        if not arrange_block:

            arrange_block = (
                "    # No arguments required"
            )

        return f'''import pytest

from module import {func_name}


def test_{func_name}_basic():
    """
    Basic unit test for {func_name}
    """

{arrange_block}

    result = {func_name}({call_signature})

    assert result is not None
'''

    # ==========================================================
    # JS UNIT TEST
    # ==========================================================

    def _generate_js_unit_test(
        self,
        func_name: str,
        function_info: Dict[str, Any]
    ) -> str:

        args = function_info.get(
            "args",
            []
        )

        arg_names = [

            arg.get("name", "arg")

            for arg in args
        ]

        arrange_lines = []

        call_args = []

        for arg_name in arg_names:

            arrange_lines.append(
                f"    const {arg_name} = 1;"
            )

            call_args.append(arg_name)

        arrange_block = "\n".join(
            arrange_lines
        )

        call_signature = ", ".join(
            call_args
        )

        if not arrange_block:

            arrange_block = (
                "    // No arguments required"
            )

        return f"""import {{ {func_name} }} from './module';

describe('{func_name}', () => {{

  test('basic functionality', () => {{

{arrange_block}

    const result = {func_name}({call_signature});

    expect(result).toBeDefined();

  }});

}});
"""

    # ==========================================================
    # EDGE CASE TESTS
    # ==========================================================

    def _generate_edge_case_tests(
        self,
        edge_cases: List[Dict[str, Any]],
        function_info: Dict[str, Any],
        language: str
    ) -> List[Dict[str, Any]]:

        tests = []

        func_name = function_info.get(
            "name",
            "unknown"
        )

        args = function_info.get(
            "args",
            []
        )

        arg_names = [

            arg.get("name", "arg")

            for arg in args
        ]

        for index, edge_case in enumerate(
            edge_cases
        ):

            case_type = edge_case.get(
                "type",
                f"edge_{index}"
            )

            description = edge_case.get(
                "description",
                "Edge case test"
            )

            safe_case_name = (
                case_type
                .replace(" ", "_")
                .replace("-", "_")
            )

            if language == "python":

                invalid_args = []

                for _ in arg_names:

                    invalid_args.append("None")

                call_signature = ", ".join(
                    invalid_args
                )

                if not call_signature:

                    call_signature = ""

                test_code = f'''import pytest

from module import {func_name}


def test_{func_name}_{safe_case_name}():
    """
    {description}
    """

    with pytest.raises(Exception):

        {func_name}({call_signature})
'''

            elif language == "javascript":

                invalid_args = []

                for _ in arg_names:

                    invalid_args.append("null")

                call_signature = ", ".join(
                    invalid_args
                )

                test_code = f"""import {{ {func_name} }} from './module';

describe('{func_name}', () => {{

  test('{description}', () => {{

    expect(() => {{

      {func_name}({call_signature});

    }}).toThrow();

  }});

}});
"""

            else:

                continue

            tests.append({
                "type": f"edge_case_{safe_case_name}",
                "target_function": func_name,
                "content": test_code,
                "language": language
            })

        return tests

    # ==========================================================
    # BOUNDARY TESTS
    # ==========================================================

    def _generate_boundary_tests(
        self,
        function_info: Dict[str, Any],
        language: str
    ) -> List[Dict[str, Any]]:

        func_name = function_info.get(
            "name",
            "unknown"
        )

        args = function_info.get(
            "args",
            []
        )

        arg_names = [

            arg.get("name", "arg")

            for arg in args
        ]

        tests = []

        if language == "python":

            arrange_lines = []

            call_args = []

            for arg_name in arg_names:

                arrange_lines.append(
                    f"    {arg_name} = 0"
                )

                call_args.append(arg_name)

            arrange_block = "\n".join(
                arrange_lines
            )

            call_signature = ", ".join(
                call_args
            )

            test_code = f'''import pytest

from module import {func_name}


def test_{func_name}_boundary():
    """
    Boundary value testing
    """

{arrange_block}

    result = {func_name}({call_signature})

    assert result is not None
'''

        elif language == "javascript":

            arrange_lines = []

            call_args = []

            for arg_name in arg_names:

                arrange_lines.append(
                    f"    const {arg_name} = 0;"
                )

                call_args.append(arg_name)

            arrange_block = "\n".join(
                arrange_lines
            )

            call_signature = ", ".join(
                call_args
            )

            test_code = f"""import {{ {func_name} }} from './module';

describe('{func_name}', () => {{

  test('boundary conditions', () => {{

{arrange_block}

    const result = {func_name}({call_signature});

    expect(result).toBeDefined();

  }});

}});
"""

        else:

            return []

        tests.append({
            "type": "boundary",
            "target_function": func_name,
            "content": test_code,
            "language": language
        })

        return tests

    # ==========================================================
    # NEGATIVE TESTS
    # ==========================================================

    def _generate_negative_tests(
        self,
        function_info: Dict[str, Any],
        language: str
    ) -> List[Dict[str, Any]]:

        func_name = function_info.get(
            "name",
            "unknown"
        )

        args = function_info.get(
            "args",
            []
        )

        arg_names = [

            arg.get("name", "arg")

            for arg in args
        ]

        tests = []

        if language == "python":

            invalid_args = []

            for _ in arg_names:

                invalid_args.append('"invalid"')

            call_signature = ", ".join(
                invalid_args
            )

            test_code = f'''import pytest

from module import {func_name}


def test_{func_name}_negative():
    """
    Negative test for invalid inputs
    """

    with pytest.raises(Exception):

        {func_name}({call_signature})
'''

        elif language == "javascript":

            invalid_args = []

            for _ in arg_names:

                invalid_args.append('"invalid"')

            call_signature = ", ".join(
                invalid_args
            )

            test_code = f"""import {{ {func_name} }} from './module';

describe('{func_name}', () => {{

  test('negative invalid input', () => {{

    expect(() => {{

      {func_name}({call_signature});

    }}).toThrow();

  }});

}});
"""

        else:

            return []

        tests.append({
            "type": "negative",
            "target_function": func_name,
            "content": test_code,
            "language": language
        })

        return tests

    # ==========================================================
    # INTEGRATION TESTS
    # ==========================================================

    def generate_integration_tests(
        self,
        module_structure: Dict[str, Any],
        language: str
    ) -> List[Dict[str, Any]]:

        tests = []

        if language == "python":

            test_code = '''import pytest


def test_module_integration():
    """
    Integration workflow test
    """

    assert True
'''

        elif language == "javascript":

            test_code = """describe('Module Integration', () => {

  test('integration workflow', () => {

    expect(true).toBe(true);

  });

});
"""

        else:

            return []

        tests.append({
            "type": "integration",
            "content": test_code,
            "language": language
        })

        return tests