from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi import status
from pathlib import Path
from typing import Optional
from ml_process.audio_mapper import AudioMapper
from ml_process.media_conversion import VideoAudioExtractor
from ml_process.audio_model_training import get_answer
import os, re

router = APIRouter(
    prefix='/Audio',
    tags=['Audio'],
)

audio_output_dir = "input/audio/"
video_output_dir = "input/video/"

@router.post("/get-source")
async def upload_media_file(
    file: Optional[UploadFile] = File(None),
    link: Optional[str] = Form(None)
    ):
    if not file and not link:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {"message": "Either file or URl for the audio/video needed"},
        )
    # Ensure the uploaded file is an audio file
    if file and file.content_type.startswith("audio/"):
        # Save the audio file
        filename = file.filename.split('.')[0] + '.wav'
        with open(audio_output_dir + filename, "wb") as audio:
            audio.write(await file.read())

            audio_mapper = AudioMapper(audio_output_dir+filename)
            audio_mapper.sentence_mapper()
        return JSONResponse(
            status_code= status.HTTP_200_OK,
            content= {"message": "Audio file uploaded successfully"},
        )
    
    elif file and file.content_type.startswith("video/"):
        with open(video_output_dir+file.filename, "wb") as video:
            video.write(await file.read())

            va_extractor = VideoAudioExtractor()
            va_extractor.extract_audio(video_output_dir+file.filename)

        return JSONResponse(
            status_code= status.HTTP_200_OK,
            content= {"message": "Video file uploaded successfully"},
            )

    elif link:
        va_extractor = VideoAudioExtractor()
        va_extractor.download_youtube_video(link)
        return JSONResponse(
            status_code= status.HTTP_200_OK,
            content= {"message": f"Link processed successfully: {link}"},
        )

    else:
        return JSONResponse(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            content= {"message": "Invalid file format. Please upload an audio or video file."},
            )


@router.get("/get_models")
async def get_models():
    file_list = os.listdir(os.getcwd() + '/models') 
    file_list = [file.split('.')[0] for file in file_list]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= {"message": "Model list successfully fetched", "model_list": file_list}
    )

@router.get("/select_model")
async def select_model(model_name):
    file_path = os.path.join(os.getcwd(),'models',model_name+'.pkl')
    if os.path.exists(file_path):
        return JSONResponse(
            status_code= status.HTTP_200_OK,
            content= {"message": f"Selected Model: {model_name} was exists"},
        )
    else:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {"message": f"Selected Model: {model_name} was not found"},
        )
    

@router.get("/download")
async def download_file(model_name: str):
    try:
        filename = f"input/audio/{model_name}.wav"
        return FileResponse(filename, media_type="application/octet-stream", filename=filename.split('/')[-1])
    except FileNotFoundError:
        return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content= {"message": "File not found"},
            )

@router.get('/question')
async def get_question(question: str, model: str):
    try:
        question += ' and give me the timeframe in paranthesis'
        res = get_answer(question, model)
        print(res)
        pattern = r'\((.*?)\)'
        matches = re.findall(pattern, res)

        if matches:
            timeframe = matches[0]
            answer = re.sub(pattern, '', res).strip()
        else:
            timeframe = matches[0]
            answer = re.sub(pattern, '', res).strip()

        return JSONResponse(
                status_code= status.HTTP_200_OK,
                content= {
                    "answer": answer,
                    'timeframe': timeframe
                }
            )
    except Exception as e:
        return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content= {"exception": e.args[0]},
            )