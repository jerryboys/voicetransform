from google.api_core.client_options import ClientOptions
from google.cloud import speech_v2
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
import csv

def transcribe_gcs_with_all_models_v2(gcs_uri, output_csv_file, project_id, language):
   
    MAX_AUDIO_LENGTH_SECS = 8 * 60 * 60
    
    # 获取所有可用的模型，这里我们直接指定一些常用的模型 ID
    # 你可以根据需要添加或删除模型，或者通过 Recognizer.list 方法获取可用模型列表
    # 参考：https://cloud.google.com/speech-to-text/v2/docs/speech-to-text-supported-languages

    if language == "zh":
        model_names = [
            "long",
            "chirp",
            "chirp_2"
        ]
        
        language_code = ["cmn-Hans-CN"]

    if language == "en":
        model_names = [
            "long",
            "telephony", 
            "chirp_telephony"
        ]
        
        language_code = ["en-US"]
    

    with open(output_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        for model_name in model_names:
            print(model_name)
            # print(language_code)

            config = speech_v2.RecognitionConfig(
              auto_decoding_config={},
              features=speech_v2.RecognitionFeatures(
                  # enable_word_confidence=True,
                  enable_word_time_offsets=True,
                  enable_automatic_punctuation=True,
                  multi_channel_mode=cloud_speech.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL,
                ),
              model=model_name,
              language_codes=language_code,
            )
            
            files = [speech_v2.BatchRecognizeFileMetadata(uri=gcs_uri)]
            
            output_config=cloud_speech.RecognitionOutputConfig(
                inline_response_config=cloud_speech.InlineOutputConfig(),
            )
            
            # 创建 Recognizer
            if model_name == "long" :
                # 设置模型的 Global 或 Region
                client = speech_v2.SpeechClient()

                recognizer_name = f"projects/{project_id}/locations/global/recognizers/_"
                print(recognizer_name)
            else:
                # 设置模型的 Global 或 Region
                client = speech_v2.SpeechClient(
                    client_options=ClientOptions(
                        api_endpoint="us-central1-speech.googleapis.com",
                    )
                )
                
                recognizer_name = f"projects/{project_id}/locations/us-central1/recognizers/_" # 使用默认 Recognizer

            # recognizer = speech_v2.Recognizer.from_service_account_json('/path/to/your/service_account_key.json')
            # recognizer = speech_v2.Recognizer()
            # recognizer.name = recognizer_name
            
            request = cloud_speech.BatchRecognizeRequest(
              recognizer=recognizer_name,
              config=config,
              files=files,
              recognition_output_config=output_config,
            )
                
            # 进行语音识别
            try:
                operation = client.batch_recognize(request=request)
                # operation = client.recognize(request=request)
                print("Waiting for operation to complete...")
                response = operation.result(timeout=3 * MAX_AUDIO_LENGTH_SECS)
                # print(response)
                
                output_end = ""
                for result in response.results[gcs_uri].transcript.results:
                    if "alternatives" in result:
                        transcript = result.alternatives[0].transcript
                        output_end = output_end + transcript
                
                writer = csv.writer(csvfile)
                writer.writerow(["v2", model_name, output_end])
                print(f"Model ID: {model_name}, Transcript: {output_end}")
                
            except Exception as e:
                print(f"Error processing model ID {model_name}: {e}")

transcribe_gcs_with_all_models_v2(gcs_uri, output_csv_file, project_id, language_code)