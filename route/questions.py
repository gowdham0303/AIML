from fastapi import APIRouter, Request, File, UploadFile, status
from fastapi.responses import HTMLResponse
from PyPDF2 import PdfReader
from question_processor.model import pdf_analysis
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from question_processor.openaifile import openaiintegration
import os
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
async def home(number_of_questions:str):
    print("Question input is :", number_of_questions)
    if FileObj:
        print(111111111111111111111)
        output = FileObj.generateQuestion(number_of_questions)
    elif os.path.isfile('output.txt'):
        print(22222222222222)
        with open('output.txt','r+') as file:
            file_obj = file.read()
        ai_obj = openaiintegration()
        ai_obj.split_into_chunks(file_obj, " ")
        output = ai_obj.formQuestion3(number_of_questions)
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content= {"message": "Input File Not Found"},
        )
    return output
