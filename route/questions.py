from fastapi import APIRouter, Request, File, UploadFile, status
from fastapi.responses import HTMLResponse
from PyPDF2 import PdfReader
from question_processor.model import pdf_analysis
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from question_processor.openaifile import openaiintegration
import os
import re
from typing import Optional
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix='/Question',
    tags=['Question'],
)
FileObj = None

class query(BaseModel):
    question: str

@router.post("/uploadDocument", response_class=HTMLResponse)
async def read_item(request: Request, file: UploadFile = File(...)):
    global FileObj
    obj = pdf_analysis(PdfReader(stream=file.file))
    FileObj = obj
    return "File Upload Sucessfully"

@router.post("/questions")
async def home(number_of_questions:str, model_name:Optional[str]=None):
    print("Question input is :", number_of_questions)
    if model_name:
        print("\nINFORMATION: Entered into Media mode for framing questions.")
        path_of_file = 'extracted_files/' + model_name + '.txt' 
        with open(path_of_file,'r+') as file:
            file_obj = file.read()
            # Define the regular expression pattern
            pattern = r'\d{2}:\d{2}:\d{2}-\d{2}:\d{2}:\d{2}\sSpeaker \d:'

            # Remove the matched pattern from the text
            clean_text = re.sub(pattern, '', file_obj)
        ai_obj = openaiintegration()
        ai_obj.split_into_chunks(clean_text, " ")
        output = ai_obj.formQuestion3(number_of_questions)
    else:
        print("\nINFORMATION: Entered into PDF mode for framing questions.")
        output = FileObj.generateQuestion(number_of_questions)
      
    return output
