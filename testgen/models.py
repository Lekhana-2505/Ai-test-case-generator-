from typing import List, Literal

from pydantic import BaseModel, Field

Category = Literal["positive", "negative", "edge", "boundary", "security", "performance", "usability"]
Priority = Literal["high", "medium", "low"]


class TestCase(BaseModel):
    id: str = Field(description="Short unique ID such as TC-001")
    title: str
    category: Category
    priority: Priority
    preconditions: List[str]
    steps: List[str]
    test_data: str = Field(description="Concrete input values used by the test, or empty string")
    expected_result: str


class TestSuite(BaseModel):
    summary: str = Field(description="One or two sentences on what was tested and the coverage approach")
    assumptions: List[str] = Field(description="Assumptions made where the input was ambiguous")
    test_cases: List[TestCase]
    test_code: str = Field(description="Runnable automated test code, or empty string if none was requested")
