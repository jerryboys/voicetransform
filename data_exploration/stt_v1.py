from google.cloud import speech,storage
import csv

def transcribe_gcs_with_all_models_v1(gcs_uri, output_csv_file, project_id, language):
   
    # 设置 Google Cloud 项目 ID
    # client = speech.SpeechClient.from_service_account_json('/path/to/your/service_account_key.json')
    client = speech.SpeechClient()
    client.project = project_id # 设置项目 ID

    storage_client = storage.Client(project=project_id)

    # 获取 GCS 存储桶中的音频文件
    bucket_name = gcs_uri.replace("gs://", "").split("/")[0]
    object_name = "/".join(gcs_uri.replace("gs://", "").split("/")[1:])
    # blob = storage_client.bucket(bucket_name).blob(object_name)
    # audio_content = blob.download_as_string()

    # 指定语言所支持的所有可用的模型，参考：
    # https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
    if language == "zh":
        model_names = [
            "default", 
            # "latest_short",
            "latest_long"
        ]
        language_code = "cmn-Hans-CN"

    if language == "en":
        model_names = [
            "default", 
            "telephony", 
            # "latest_short",, 
            "latest_long"
        ]
        language_code = "en-US"

    MAX_AUDIO_LENGTH_SECS = 8 * 60 * 60
    
    with open(output_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        for model_name in model_names:
            print(model_name)
            
            # 配置识别请求
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                sample_rate_hertz=8000,  # 根据你的音频文件调整采样率
                language_code=language_code,  # 根据你的音频文件调整语言代码
                model=model_name,
                use_enhanced=True,  # 可选，启用增强模型
                enable_automatic_punctuation=True,
            )
            # audio = speech.RecognitionAudio(content=audio_content)
            audio = speech.RecognitionAudio(uri=gcs_uri)

            output_end = ""
            
            # 进行语音识别
            try:
                operation = client.long_running_recognize(config=config, audio=audio)
                print("Waiting for operation to complete...")
                response = operation.result(timeout=MAX_AUDIO_LENGTH_SECS)

                # response = client.recognize(config=config, audio=audio)
                transcript_builder = []
                # Each result is for a consecutive portion of the audio. Iterate through
                # them to get the transcripts for the entire audio file.
                for result in response.results:
                    # The first alternative is the most likely one for this portion.
                    # transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
                    # transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")
                    
                    transcript = result.alternatives[0].transcript
                    output_end = output_end + transcript
                    
                writer = csv.writer(csvfile)
                writer.writerow(["v1", model_name, output_end])
                print(f"Model: {model_name}, Transcript: {output_end}")
                
            except Exception as e:
                print(f"Error processing model {model_name}: {e}")

transcribe_gcs_with_all_models_v1(gcs_uri, output_csv_file, project_id, language_code)