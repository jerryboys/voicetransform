from google.cloud import speech
import wave
import datetime

class STTClient:
    models = {
        "英语(美国)":{
            "language_code":"en-US",
            "model":"latest_long",
            "useEnhanced":False
        },
        "英语(英国)":{
            "language_code":"en-GB",
            "model":"latest_long",
            "useEnhanced":False
        },
        "英语(印度)":{
            "language_code":"en-IN",
            "model":"latest_long",
            "useEnhanced":False
        },
        "英语(澳大利亚)":{
            "language_code":"en-AU",
            "model":"latest_long",
            "useEnhanced":False
        },
        "俄语":{
            "language_code":"ru-RU",
            "model":"latest_long",
            "useEnhanced":False
        },
        "西班牙语(西班牙)":{
            "language_code":"es-ES",
            "model":"latest_long",
            "useEnhanced":False
        },
        "西班牙语(美国)":{
            "language_code":"es-US",
            "model":"latest_long",
            "useEnhanced":False
        },
        "西班牙语(美国)":{
            "language_code":"es-US",
            "model":"latest_long",
            "useEnhanced":False
        },
        "法语(法国)":{
            "language_code":"fr-FR",
            "model":"latest_long",
            "useEnhanced":False
        },
        "法语(加拿大)":{
            "language_code":"fr-CA",
            "model":"latest_long",
            "useEnhanced":False
        },
        "葡萄牙语(葡萄牙)":{
            "language_code":"pt-PT",
            "model":"latest_long",
            "useEnhanced":False
        },
        "葡萄牙语(巴西)":{
            "language_code":"pt-BR",
            "model":"latest_long",
            "useEnhanced":False
        },
        "中文普通话":{
            "language_code": "zh",
            "model":"default",
            "useEnhanced": False
        },
        "粤语":{
            "language_code": "yue-Hant-HK",
            "model":"default",
            "useEnhanced": False
        }
    }
    client = None
    def __init__(self):
        self.resetConfig()
        self.transcript = ""
        self.audio = b""
        self.getClient()

    def resetConfig(self):
        self.config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=48000,
                language_code="zh",
                max_alternatives=1,
                enable_automatic_punctuation=True,
                use_enhanced = False,
            )
        self.streaming_config = speech.StreamingRecognitionConfig(
                config=self.config,
                
            )
        
    def getClient(self):
        self.client = speech.SpeechClient()
        return self.client
    
    def resetClient(self, lang):
        self.updateConfig(lang)
        self.client = None
        self.audio = b""
        self.transcript = ""
        self.getClient()
        return ""

    def updateConfig(self, lang):
        self.resetConfig()
        config =self.models[lang]
        self.streaming_config.config.model = config["model"]
        self.streaming_config.config.language_code = config["language_code"]
        self.streaming_config.config.use_enhanced = config["useEnhanced"]

    def updateConfig_offline(self, lang, rate, nchannel, maxAlternatives, separate):
        self.resetClient(lang)
        self.resetConfig()
        
        self.config.sample_rate_hertz=int(rate)
        self.config.audio_channel_count=int(nchannel)
        self.config.max_alternatives = int(maxAlternatives)
        #self.config.enable_word_time_offsets = True
        config =self.models[lang]
        self.config.model = config["model"]
        self.config.language_code = config["language_code"]
        self.config.use_enhanced = config["useEnhanced"]
        # self.config.features=cloud_speech.RecognitionFeatures(
        #     multi_channel_mode=cloud_speech.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL,
        # ),
        self.config.enable_separate_recognition_per_channel=True
        # if separate:
        #     self.config.diarization_config.enable_speaker_diarization = True
        #     self.config.diarization_config.min_speaker_count = 1
        print(self.config)
            
        
    
    def saveResult(self):
        filename = "pcm/"+datetime.datetime.now().strftime("%Y-%M-%d-%H-%m-%S")
        with wave.open(filename+".wav", "wb") as waf_output :
            waf_output.setnchannels(1)
            waf_output.setsampwidth(2)
            waf_output.setframerate(44100)
            waf_output.writeframes(self.audio)
        with open(filename+".txt", "w") as f:
            f.write(self.transcript)
        return [filename+".wav", filename+".txt"]
        
    def streamRecognize(self, audio, sample_rate=16000):
        if self.streaming_config.config.sample_rate_hertz != sample_rate:
            self.streaming_config.config.sample_rate_hertz = sample_rate
        chunck = int(sample_rate/10)
        requests = []
        audio = [item.tobytes() for item in audio]
        self.audio+=b"".join(audio)
        while audio:
            request = audio[:chunck]
            audio = audio[chunck:]
            requests.append(b"".join( request))
        
        requests = [speech.StreamingRecognizeRequest(audio_content=item) for item in requests]
        
        responses = self.client.streaming_recognize(self.streaming_config, requests)
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue
            self.transcript += result.alternatives[0].transcript
            
            if  result.is_final:
                self.transcript+="\n"

    def shortFileRecognize(self, file_name, separate = False):
        with open(file_name, "rb") as audo_file:
            content = audo_file.read()
        audio = speech.RecognitionAudio(content=content)
        response = self.client.recognize(config=self.config, audio=audio)
        transcripts = []
        if separate:
            for item in response.results:
                print(item.channel_tag)
                transcripts.append("channel"+str(item.channel_tag)+": "+item.alternatives[0].transcript)
        else:
            for item in response.results:
                
                transcripts.append(item.alternatives[0].transcript)
        
        return "\n".join(transcripts)

    def longFileRecognize(self, file_name, separate = False):
        
        audio = speech.RecognitionAudio(uri = file_name)
        operation = self.client.long_running_recognize(config=self.config, audio=audio)
        response = operation.result(timeout=90)
        transcripts = []
        if separate:
            for item in response.results:
                
                transcripts.append("channel"+str(item.channel_tag)+": "+item.alternatives[0].transcript)
        else:
            for item in response.results:
                print(item.alternatives[0])
                transcripts.append(item.alternatives[0].transcript)
        
        return "\n".join(transcripts)