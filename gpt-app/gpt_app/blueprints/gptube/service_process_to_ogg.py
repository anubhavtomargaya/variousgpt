
from pathlib import Path
from gpt_app.common.dirs import PROCESSED_DIR, YOUTUBE_DIR
from gpt_app.common.utils_dir import _make_file_path, client as gcs_client, BUCKET_NAME
from gpt_app.common.utils_audio import preprocess_audio_for_transcription


def download_video_file_gcs(file_name,dir=YOUTUBE_DIR)->Path:
    tmp_file_path = _make_file_path(dir,file_name,local=True)
    if tmp_file_path.exists():
        print("tmp exists")
        return tmp_file_path
    src_blob_name = _make_file_path(dir,file_name,local=False)
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(src_blob_name)
    print(blob)
    blob.download_to_filename(tmp_file_path)
    return tmp_file_path

def convert_local_path_to_ogg_with_ffmpeg(file_path:Path, output_dir=PROCESSED_DIR):
    output_file = Path(output_dir,f"{file_path.stem}.ogg" )
    print(output_file)
    success = preprocess_audio_for_transcription(file_path, output_file)
    # return Path(output_file) if success else False
    if success:
        bucket = gcs_client.bucket(BUCKET_NAME)
        destination_blob_name = _make_file_path(PROCESSED_DIR,output_file,local=False)
        blob = bucket.blob(destination_blob_name)
        upload = blob.upload_from_filename(output_file)
        print("upload:",upload)
        print("gcs name,",destination_blob_name)
        print("gcs up,",upload)
        exists = blob.exists()
        print(f"Upload successful: {exists}")
        return Path(output_file)
    else:
        False

    

if __name__ == '__main__':
    # f = 'Cochin_Shipyard_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4'
    # f = 'Hindustan_Aeronautics_Ltd_Q4_FY2023-24_Earnings_Conference_Call.webm'
    # f = 'Granules_India_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4'
    f = 'Budget_पर_Kharge_ने_Rajya_Sabha_में__सुनाया_गुस्से_में_Nirmala_Sitharaman_ने_क्या_गिना_दिया.webm'
    # f = 'Deepak_Nitrite_Earnings_Call_for_Q4FY24.mp4'
    def test_download_input_file():
        return download_video_file_gcs(file_name=f)

    def test_conversion_to_ogg():
        fpath = download_video_file_gcs(f)
        # fpath = _make_file_path(direcotry=YOUTUBE_DIR,file_name=f)
        return convert_local_path_to_ogg_with_ffmpeg(file_path=fpath)
    

    # print(test_download_input_file())
    print(test_conversion_to_ogg())