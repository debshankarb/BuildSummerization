from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from model_classes import ExceptionMessageEnum,CustomException
from dataprocessing.bart_summary import bart_summarization
from http import HTTPStatus
from dataprocessing.summary import Summary
from urllib.parse import unquote
from dataprocessing.data_cleansing import process_conversation_notes
from model_classes import Note, CleanseDataStatusResponse, CleanseDataResponse, UnstructuredSummary, Job, StatusEnum, StructuredSummary, MajorIncidentCommunication, Telemetry, BuildSummary, BuildLogs
from fastapi.security.api_key import APIKey
import auth
from dotenv import load_dotenv
from dataprocessing.chunking import Chunk
from config import log_entry_exit
import platform_config
import logging

load_dotenv()

job_object = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@log_entry_exit
def cleanse_note(note: Note, job):
    '''
    Method takes uncleansed notes as input and returns cleansed note as output
    '''
    try:
        # Process and cleanse conversation notes
        url_encoded_string = process_conversation_notes(note.work_note)
        # Update job result and status
        job_object[job.job_uuid.__str__()].result = url_encoded_string
        job_object[job.job_uuid.__str__()].status = StatusEnum.SUCCESS
    except Exception as e:
        logging.error(ExceptionMessageEnum.DATA_CLEANSING_ERROR.value.format(e))
        job_object[job.job_uuid.__str__()].result = ExceptionMessageEnum.DATA_CLEANSING_ERROR.value.format(e)
        job_object[job.job_uuid.__str__()].status = StatusEnum.ERROR

@log_entry_exit
@app.post("/text-tools/cleanse-note", response_model=CleanseDataStatusResponse, status_code=HTTPStatus.ACCEPTED)
async def post_cleanse_note(note: Note, background_tasks: BackgroundTasks, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to initiate data cleansing process
    '''
    try:
        # Create a new job and add it to the job_object
        data_cleaning_job = Job()
        job_uuid = data_cleaning_job.job_uuid.__str__()
        job_object[job_uuid] = data_cleaning_job
        # Add a background task to run data cleansing asynchronously
        background_tasks.add_task(cleanse_note, note, data_cleaning_job)
        return CleanseDataStatusResponse(transaction_id=job_uuid, status=data_cleaning_job.status)
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit
@app.get("/text-tools/cleanse-note/status/{transaction_id}", response_model=CleanseDataStatusResponse)
def get_cleanse_note_status(transaction_id: str, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to retrieve data cleansing job status
    '''
    try:
        job = job_object.get(transaction_id)
        if job:
            return CleanseDataStatusResponse(transaction_id=transaction_id, status=job.status)
        else:
            return CleanseDataStatusResponse(transaction_id=transaction_id, status=StatusEnum.NOT_FOUND)
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit
@app.get("/text-tools/cleanse-note/{transaction_id}", response_model=CleanseDataResponse)
def get_cleansed_note(transaction_id: str, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to retrieve cleansed data
    '''
    try:
        job = job_object.get(transaction_id)
        if job:
            return CleanseDataResponse(transaction_id=transaction_id, status=job.status, result=job.result)
        else:
            return CleanseDataResponse(transaction_id=transaction_id, status=StatusEnum.NOT_FOUND, result="NA")
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit
@app.post("/text-tools/short-summary", response_model=UnstructuredSummary)
def post_short_summary(note: Note, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to generate a short summary using BART summarization
    '''
    try:
        url_encoded_string = bart_summarization(note.work_note)
        decoded_summary = unquote(url_encoded_string)
        return UnstructuredSummary(summary=decoded_summary)
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit
@app.post("/text-tools/long-summary", response_model=UnstructuredSummary)
def post_long_summary(note: Note, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to generate a long summary using Llama summarization
    '''
    try:
        chunks = Chunk()
        long_summary = chunks.summarize(note.work_note, summary_type='long_summary')
        return UnstructuredSummary(summary=long_summary)
    
    except CustomException as ce:
        logging.error(str(ce))
        raise HTTPException(status_code=ce.error_code, detail=str(ce))
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit
@app.post("/text-tools/structured-summary", response_model=StructuredSummary)
def post_structured_summary(note: Note, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to generate a structured summary using Llama summarization
    '''
    try:
        chunks = Chunk()
        structured_summary = chunks.summarize(note.work_note, summary_type='structured_summary')
        return structured_summary

    except ValidationError as ve:
        raise HTTPException(status_code=400, detail = ExceptionMessageEnum.VALIDATION_ERROR.value.format(ve))
    except CustomException as ce:
        logging.error(str(ce))
        raise HTTPException(status_code=ce.error_code, detail=str(ce))
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit   
@app.post("/text-tools/build-summary/", response_model=BuildSummary)
def post_build_summary(input: BuildLogs, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to generate a Build Log Summarization, essentially for build failures
    '''
    try:
        chunks = Chunk()
        build_summary = chunks.summarize(input.logs, summary_type='build_summary_structured')
        return build_summary

    except ValidationError as ve:
        raise HTTPException(status_code=400, detail = ExceptionMessageEnum.VALIDATION_ERROR.value.format(ve))
    except CustomException as ce:
        logging.error(str(ce))
        raise HTTPException(status_code=ce.error_code, detail=str(ce))
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit
@app.post("/text-tools/major-incident-communication", response_model=MajorIncidentCommunication)
def major_incident_communication(note: Note, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to generate a major incident communication
    '''
    try:
        major_incident_communication = Summary.major_incident_communication(
            note.work_note)
        return MajorIncidentCommunication(email_content=major_incident_communication)

    except ValidationError as ve:
        raise HTTPException(status_code=400, detail = ExceptionMessageEnum.VALIDATION_ERROR.value.format(ve))
    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

@log_entry_exit
@app.post("/text-tools/telemetry-summary", response_model=UnstructuredSummary)
def telemetry_summary(telemetry: Telemetry, api_key: APIKey = Depends(auth.get_api_key)):
    '''
    API to generate Telemetry text based rootcause summarization
    '''
    try:
        telemetry_summary = Summary.summarize_rootcause_from_telemetry(
            telemetry.anomaly,telemetry.metric,telemetry.error, summary_type='llama_telemetry_summary')
        
        return UnstructuredSummary(summary=telemetry_summary)

    except Exception as e:
        logging.error(ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))
        raise HTTPException(
            status_code=500, detail=ExceptionMessageEnum.ERROR_RESPONSE.value.format(e))

