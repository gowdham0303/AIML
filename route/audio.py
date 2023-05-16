from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import JSONResponse

from typing import Optional
from schemas.audio import LinkProcess
from audio_mapper import AudioMapper
from media_conversion import VideoAudioExtractor

router = APIRouter(
    prefix='/NewPayments',
    tags=['New Payments'],
)


@router.post("/get-source")
async def upload_media_file(
    file: UploadFile = Optional[File(...)],
    url: str = Optional[None]
    ):
    if not file and not url:
        return JSONResponse(
            content= "Either file or URl for the audio/video needed",
            status_code= 400
        )
    # Ensure the uploaded file is an audio file
    print(file, file.content_type)
    if file.content_type.startswith("audio/"):
        # Save the audio file
        with open(file.filename, "wb") as audio:
            audio.write(await file.read())

            audio_mapper = AudioMapper(file.filename)
            p = audio_mapper.sentence_mapper()
            print(p)            
        return JSONResponse(
            content= {"message": "Audio file uploaded successfully"},
            status_code= 400
        )
    
    elif file.content_type.startswith("video/"):
        with open(file.filename, "wb") as video:
            video.write(await file.read())

            va_extractor = VideoAudioExtractor()
            va_extractor.extract_audio(file.filename)

        return {"message": "Video file uploaded successfully"}

    else:
        return {"error": "Invalid file format. Please upload an audio or video file."}


@router.post("/process_link")
async def process_link(link_request: LinkProcess):
    link = link_request.link
    print(link)
    va_extractor = VideoAudioExtractor()
    va_extractor.download_youtube_video(link)
    return JSONResponse(
        content= {"message": f"Link processed successfully: {link}"},
        status_code= 400
    )