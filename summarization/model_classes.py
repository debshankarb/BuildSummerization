from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Note(BaseModel):
    work_note: str

class BuildLogs(BaseModel):
    logs: str

class Telemetry(BaseModel):
    anomaly: str
    metric: str
    error: str



class UnstructuredSummary(BaseModel):
    summary: str


class MajorIncidentCommunication(BaseModel):
    email_content: str


class StructuredSummary(BaseModel):
    issue_title: str = ""
    issue_description: str = ""
    issue_category: str = ""
    root_cause: str = ""
    resolution_taken: str = ""
    affected_applications: str = ""
    participating_people: str = ""
    resolver_group: str = ""

class BuildSummary(BaseModel):
    version: str = ""
    account: str = ""
    application: str = ""
    description: str = ""
    error_location: str = ""
    resolution_note: str = ""
    affected_applications: str = ""
    triggered_by: str = ""
    issue_category: str = ""
    resolver_group: str = ""
    date: str = ""
    time: str = ""
    note: str = ""


class StatusEnum(Enum):
    IN_PROGRESS = "In progress"
    SUCCESS = "Success"
    FAILURE = "Failure"
    NOT_FOUND = "Not found"
    ERROR = "Error"


class CleanseDataResponse(BaseModel):
    transaction_id: str
    status: StatusEnum
    result: str


class CleanseDataStatusResponse(BaseModel):
    transaction_id: str
    status: StatusEnum


class Job(BaseModel):
    job_uuid: UUID = Field(default_factory=uuid4)
    status: StatusEnum = StatusEnum.IN_PROGRESS
    result: str = "No Data"


class ExceptionMessageEnum(Enum):
    INPUT_LIMIT_REACHED="Cannot process more than 35000 thousand tokens at one go! Tokens:{token}"
    LLM_CONNECTION_EXCEPTION = "Exception occured while connecting to LLM Platform{}"
    LLM_GENERATE_TEXT_EXCEPTION = "Exception occured while generating text from LLM Platform{}"
    ERROR_RESPONSE = "Exception Occured while generating API Response:{}"
    VALIDATION_ERROR = "Validation Error Occured:{}"
    DATA_CLEANSING_ERROR = "Error Ocuured While Invoking Cleansing Data API:{}"


class CustomException(Exception):
    def __init__(self, error_code, message="Default custom exception message"):
        self.error_code = error_code
        self.message = message
        super().__init__(self.message)
    