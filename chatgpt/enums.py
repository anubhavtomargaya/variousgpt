from enum import Enum
class tsFormats(Enum):
    JSON = 'json'
    SRT  = 'srt'
    TXT = 'txt'

class RecordingFormats(Enum):
    MP3 = 'mp3'
    WAV = 'wav'
    M4A = 'm4a'

class RecordingTypes(Enum):
   CONCALL = 'concall'
   INTERVIEW = 'interview'
