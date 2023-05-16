from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi import status

from typing import Optional
# from schemas.audio import LinkProcess
from ml_process.audio_mapper import AudioMapper
from ml_process.media_conversion import VideoAudioExtractor
import os

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
        with open(audio_output_dir + file.filename, "wb") as audio:
            audio.write(await file.read())

            audio_mapper = AudioMapper(audio_output_dir+file.filename)
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
    print(file_list)