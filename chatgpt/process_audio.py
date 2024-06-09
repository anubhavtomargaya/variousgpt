import subprocess

def preprocess_audio_for_transcription(input_file, output_file,
                                       format='ogg'):
  """
  Re-encodes audio to Opus codec optimized for transcription.

  Args:
      input_file (str): Path to the input audio file.
      output_file (str): Path to save the re-encoded audio file.

  Returns:
      bool: True if successful, False otherwise.
  """
  command = [
      "ffmpeg",
      "-i", input_file,
      "-vn",  # Disable video processing
      "-map_metadata", "-1",  # Prevent copying metadata
      "-ac", "1",  # Mono audio
      "-c:a", "libopus",  # Opus codec
      "-b:a", "12k",  # 12kbps bitrate (adjust as needed)
      "-application", "voip",  # Optimize for voice
      output_file,
  ]

  try:
    subprocess.run(command, check=True)
    return True
  except subprocess.CalledProcessError:
    print("Error: ffmpeg failed to process audio.")
    return False

# Example usage
if __name__ == "__main__":
  from pathlib import Path

  wav_file = 'chatgpt/data/EarningsCall.wav'
  path_ = f'chatgpt/data/'
  file_name = 'earning_call_morepen.mp3'
  mp3_file = f'{path_}{file_name}'
  output_file = f"{path_}processed_{file_name.split('.')[0]}.ogg"
  success = preprocess_audio_for_transcription(mp3_file, output_file)
  if success:
    print(f"Audio re-encoded successfully to {output_file}")
  else:
    print("Re-encoding failed.")
