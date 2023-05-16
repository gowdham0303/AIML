from moviepy.editor import VideoFileClip
from pytube import YouTube
import os
from audio_mapper import AudioMapper


class VideoAudioExtractor(object):
    audio_output_dir = "input/audio"
    video_output_dir = "input/video"

    def extract_audio(self, video_path):
        # Load the video clip
        video_clip = VideoFileClip(video_path)

        # Extract the audio
        audio_clip = video_clip.audio

        # Get the original filename from the video path
        filename = os.path.splitext(os.path.basename(video_path))[0]

        # Specify the output filename
        output_filename = os.path.join(__class__.audio_output_dir, filename + ".wav")

        # Save the audio clip as an MP3 file
        audio_clip.write_audiofile(output_filename)

        # Close the clips
        video_clip.close()
        audio_clip.close()
        
        os.remove(video_path)

        audio_mapper = AudioMapper(output_filename)
        t = audio_mapper.sentence_mapper()
        print(t)

    def download_youtube_video(self, video_url):
        # Create a YouTube object
        yt = YouTube(video_url)

        # Get the highest resolution video stream
        stream = yt.streams.get_highest_resolution()

        # Get the original filename from the YouTube video
        filename = yt.title + ".mp4"

        # Download the video
        stream.download(__class__.video_output_dir, filename)

        self.extract_audio(__class__.video_output_dir +'/'+ filename)