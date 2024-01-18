import os
import re
from utils import Utils
from model_classes import StructuredSummary,BuildSummary
from fastapi import HTTPException
import json
import platform_config
from config import log_entry_exit

class Summary:  

    @log_entry_exit
    def generate_summary(worknotes : list, summary_type: str) -> str :
        """
        Generates a summary of the input worknote using Llama summarization.
        """

        try:
            cleaned_worknotes = Utils.clean_text(worknotes)

            generated_prompt_list = platform_config.promptbuilders.generate_prompts(summary_type, cleaned_worknotes)
            params = platform_config.integration.fetch_default_params()
            llm_response = platform_config.integration.generate_text(
                generated_prompt_list,  params
                )
            
            summary = Utils.process_response(llm_response)

            if summary_type == "structured_summary" or summary_type == "build_summary_structured":
                return Summary.structured_summary(summary, summary_type)
            else:
                return summary

        except Exception as e:
            raise e
        
    @log_entry_exit
    def summarize_rootcause_from_telemetry(anomaly: str, metric: str, error: str, summary_type: str) -> str:
        """
        Generates a summary of the root cause from telemetry data
        """

        try:

            generated_prompt = platform_config.promptbuilders.generate_telemetry_prompt(summary_type=summary_type,anomaly=anomaly,metric=metric,error=error)

            params = platform_config.integration.fetch_params_telemetry_summary()

            bam_response = platform_config.integration.generate_text(
                generated_prompt, params
            )

            summary = bam_response[0]

            if summary_type == "structured_summary":
                return Summary.structured_summary(summary)

            else:
                return summary

        except Exception as e:
            raise e

    @log_entry_exit
    def remove_email_parts(email_text):
        subject_pattern = rf".*{re.escape('Subject:')}.*"
        greeting_pattern = rf".*{re.escape('Dear')}.*"
        signature_pattern_1 = rf".*{re.escape('Best regards')}.*"
        signature_pattern_2 = rf".*{re.escape('Your Name')}.*"

        # Split the input text into lines
        lines = email_text.split("\n")
        filtered_lines = [
            line for line in lines if not re.search(subject_pattern, line)]
        output_text = "\n".join(filtered_lines)

        lines = output_text.split("\n")
        filtered_lines = [
            line for line in lines if not re.search(greeting_pattern, line)]
        output_text = "\n".join(filtered_lines)

        lines = output_text.split("\n")
        filtered_lines = [
            line for line in lines if not re.search(signature_pattern_1, line)
        ]
        output_text = "\n".join(filtered_lines)

        lines = output_text.split("\n")
        filtered_lines = [
            line for line in lines if not re.search(signature_pattern_2, line)
        ]
        output_text = "\n".join(filtered_lines)

        # Print the modified text
        print(output_text)

        # Print the modified text
        # print(output_text)
        return output_text

    @log_entry_exit
    def major_incident_communication(worknote: str):
        """
        major incident communication of the input worknote using Llama.
        """

        try:
            generated_prompt = platform_config.promptbuilders.generate_prompt(
                "major_incident_communication", worknote
            )

            params = platform_config.integration.fetch_params_major_incident_communication()

            bam_response = platform_config.integration.generate_text(
                generated_prompt, params
            )

            email_body = bam_response[0]
            email_body = Summary.remove_email_parts(email_body)
            return email_body

        except Exception as e:
            raise e

    @log_entry_exit
    def structured_summary(summary: str, summary_type:str) :
        json_summary = Utils.convert_to_valid_json(summary)

        json_summary = json.loads(json_summary)

        if summary_type == 'structured_summary':
            structured_summary = StructuredSummary()
        elif summary_type == "build_summary_structured":
            structured_summary = BuildSummary()

        for key, value in json_summary.items():
            key_normalized = key.lower().replace(" ", "_")
            if isinstance(value, list):
                value = ", ".join(value)
            if hasattr(structured_summary, key_normalized):
                setattr(structured_summary, key_normalized, value)

        all_empty = all(
            value == "" for value in structured_summary.__dict__.values())

        if all_empty:
            msg = "The watsonx model failed to generate a valid response."
            error_response = {"detail": msg}
            print(msg, json_summary)
            return HTTPException(status_code=500, detail=error_response)
        # JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)

        return structured_summary
