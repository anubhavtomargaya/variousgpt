
   

from  gpt_app.common.enums import RecordingFormats, RecordingTypes, tsFormats


class AudioFileMeta:
    def __init__(self, 
                 file_name:str,  #pk
                 input_file_format:RecordingFormats,
                 recording_type:RecordingTypes,
                 audio_length:float=None,
                 ) -> None:
        
        self.file_name = file_name
        self.input_file_format = input_file_format
        self.recording_type = recording_type
        self.audio_length = audio_length
        

class TranscriptMetadata:
    def __init__(self, 
                 audio_file_name:str,  #pk
                 transcript_format:tsFormats,
                 num_chunks:int=None,
                 org_name:str=None, 
                 audio_base_prompt:str=None,
                 speakers:dict=None
                 ) -> None:
        
        self.audio_file_name = audio_file_name
        self.transcript_format = transcript_format
        self.num_chunks = num_chunks
        self.org_name = org_name
        self.audio_base_prompt = audio_base_prompt
        self.speakers = speakers
        
class TranscriptChunk:
    def __init__(self,
                 id,
                 file_name,
                 text,
                 embedding=None) -> None:
        pass

class AudioTranscript:
    def __init__(self,
                 text,
                 meta:dict) -> None:
        self.text = text 
        self.meta = meta 
