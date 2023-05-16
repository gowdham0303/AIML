import pvleopard, logging
import pandas as pd
from ml_process.voice_classification import VoiceActivitySpeakerDiarization


logger = logging.getLogger()
access_key = 'Yg4R/1k/LfFWN80ZOQXPT9RNMz+zRwEXE6Uj/O7Qft4oRnplC7Y88w=='

class AudioMapper(object):
    def __init__(self, audio):
        self.audio = audio
        
    def sentence_mapper(self):
        leopard = pvleopard.create(access_key=access_key)
        _, words = leopard.process_file(self.audio)

        try:
            voice = VoiceActivitySpeakerDiarization(self.audio)
            df = voice.main()
            print(df)
            
            for idx, row in df.iterrows():
                start_time = round(row['StartTime'], 2)
                end_time = round(row['EndTime'], 2)
                word_list = []
                for word in words:
                    if start_time <= round(word.start_sec, 2) <= end_time:
                        word_list.append(''.join(word.word))

                sentence = ' '.join(word_list)
                df.at[idx, 'Sentence'] = sentence

            return df
        except:
            logger.exception("Failed to map the sentence")
            return