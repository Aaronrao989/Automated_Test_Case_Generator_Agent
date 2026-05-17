from datetime import datetime

from typing import (
    Optional,
    List,
    Dict,
    Any,
    Literal
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


# ==========================================================
# BASE MODEL
# ==========================================================

class APIBaseModel(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


# ==========================================================
# START ANALYSIS REQUEST
# ==========================================================

class AnalysisStartRequest(
    APIBaseModel
):

    source_type: Literal[
        "github_url",
        "zip_file",
        "user_story",
        "code_snippet",
        "raw_code"
    ]

    source_data: str = Field(
        min_length=1
    )


# ==========================================================
# JOB RESPONSE
# ==========================================================

class AnalysisJobResponse(
    APIBaseModel
):

    job_id: str

    status: str

    created_at: datetime


# ==========================================================
# FUNCTION RESPONSE
# ==========================================================

class FunctionResponse(
    APIBaseModel
):

    name: str

    file: Optional[str] = None

    type: Optional[str] = None

    language: Optional[str] = None

    line: Optional[int] = None


# ==========================================================
# REPOSITORY STRUCTURE
# ==========================================================

class RepoStructureResponse(
    APIBaseModel
):

    languages: Dict[
        str,
        int
    ] = Field(default_factory=dict)

    files: List[str] = Field(
        default_factory=list
    )

    functions: List[
        FunctionResponse
    ] = Field(default_factory=list)

    dependencies: Dict[
        str,
        Any
    ] = Field(default_factory=dict)


# ==========================================================
# EDGE CASE RESPONSE
# ==========================================================

class EdgeCaseResponse(
    APIBaseModel
):

    type: Optional[str] = None

    edge_case: Optional[str] = None

    description: Optional[str] = None

    test_code: Optional[str] = None

    function_name: Optional[str] = None

    edge_case_type: Optional[str] = None

    suggested_test: Optional[str] = None


# ==========================================================
# GENERATED TEST RESPONSE
# ==========================================================

class GeneratedTestResponse(
    APIBaseModel
):

    id: Optional[str] = None

    test_type: Optional[str] = None

    target_function: Optional[str] = None

    file_path: Optional[str] = None

    content: Optional[str] = None

    language: Optional[str] = None

    generated_by: Optional[str] = None


# ==========================================================
# TEST EXECUTION RESPONSE
# ==========================================================

class TestExecutionResultResponse(
    APIBaseModel
):

    file: Optional[str] = None

    status: str

    duration: float = 0.0

    output: Optional[str] = None

    errors: Optional[str] = None

    error: Optional[str] = None

    test_type: Optional[str] = None


# ==========================================================
# UNCOVERED CODE RESPONSE
# ==========================================================

class UncoveredCodeResponse(
    APIBaseModel
):

    file: Optional[str] = None

    line: Optional[int] = None

    code: Optional[str] = None

    importance: Optional[int] = None


# ==========================================================
# COVERAGE RESPONSE
# ==========================================================

class CoverageReportResponse(
    APIBaseModel
):

    total_coverage: float = 0.0

    covered_lines: int = 0

    total_lines: int = 0

    file_coverage: Dict[
        str,
        float
    ] = Field(default_factory=dict)

    uncovered_code: List[
        UncoveredCodeResponse
    ] = Field(default_factory=list)

    raw_output: Optional[str] = None

    raw_errors: Optional[str] = None

    error: Optional[str] = None


# ==========================================================
# FINAL ANALYSIS RESPONSE
# ==========================================================

class AnalysisResultResponse(
    APIBaseModel
):

    job_id: str

    status: str

    structure: Optional[
        RepoStructureResponse
    ] = None

    edge_cases: List[
        EdgeCaseResponse
    ] = Field(default_factory=list)

    tests: List[
        GeneratedTestResponse
    ] = Field(default_factory=list)

    saved_test_files: List[
        str
    ] = Field(default_factory=list)

    test_results: List[
        TestExecutionResultResponse
    ] = Field(default_factory=list)

    coverage: Optional[
        CoverageReportResponse
    ] = None

    suggestions: List[
        str
    ] = Field(default_factory=list)

    llm_provider: Optional[str] = None

    api_calls_made: Optional[int] = 0

    source_type: Optional[str] = None

    created_at: Optional[
        datetime
    ] = None

    updated_at: Optional[
        datetime
    ] = None

    error: Optional[str] = None