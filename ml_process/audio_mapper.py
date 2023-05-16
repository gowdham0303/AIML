import pvleopard, logging
import datetime
from ml_process.voice_classification import VoiceActivitySpeakerDiarization
from ml_process.audio_model_training import Models

logger = logging.getLogger()
access_key = 'Yg4R/1k/LfFWN80ZOQXPT9RNMz+zRwEXE6Uj/O7Qft4oRnplC7Y88w=='

class AudioMapper(object):
    def __init__(self, audio):
        self.audio = audio
    
    def write_data_to_text_file(self, data_frame, file_path):
        with open(file_path, 'w') as file:
            for _, row in data_frame.iterrows():
                start_time = row['StartTime_HH_MM_SS']
                end_time = row['EndTime_HH_MM_SS']
                speaker = row['SpeakerLabel']
                sentence = row['Sentence']
                line = f"{start_time}-{end_time} {speaker}: {sentence}\n"
                file.write(line)
            
            file.close()

    def sentence_mapper(self):
        leopard = pvleopard.create(access_key=access_key)
        _, words = leopard.process_file(self.audio)

        try:
            voice = VoiceActivitySpeakerDiarization(self.audio)
            df = voice.main()

            def convert_to_hh_mm_ss(decimal_time):
                time_delta = datetime.timedelta(seconds=decimal_time)
                time_obj = datetime.datetime(1, 1, 1) + time_delta
                return datetime.datetime.strptime(time_obj.strftime("%H:%M:%S"), "%H:%M:%S").time()

            # Apply conversion to StartTime and EndTime columns
            df['StartTime_HH_MM_SS'] = df['StartTime'].apply(convert_to_hh_mm_ss)
            df['EndTime_HH_MM_SS'] = df['EndTime'].apply(convert_to_hh_mm_ss)

            for idx, row in df.iterrows():
                start_time = round(row['StartTime'], 2)
                end_time = round(row['EndTime'], 2)
                word_list = []
                for word in words:
                    if start_time <= round(word.start_sec, 2) <= end_time:
                        word_list.append(''.join(word.word))

                sentence = ' '.join(word_list)
                df.at[idx, 'Sentence'] = sentence
            
            output_filename = self.audio.split("/")[-1].split(".")[0]
            output_txt_file = f"extracted_files/{output_filename}.txt" 
            self.write_data_to_text_file(df, output_txt_file)

            #triggering model training
            audio_model = Models(output_filename)
            audio_model.model()


        except:
            logger.exception("Failed to map the sentence")