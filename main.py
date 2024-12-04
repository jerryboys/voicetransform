import gradio as gr
from stt.client import STTClient
from datetime import datetime
import os
import wave
from storage.client import StorageClient

sst_client = STTClient()
def transcribe(audio):
    ss, audio = audio
    sst_client.streamRecognize(audio, ss)
    
    yield sst_client.transcript


def upload(file):
    new_file_name = "./offline_audio/{}.wav".format(datetime.now().strftime("%Y-%M-%d-%H-%m-%S"))
    os.rename(file, new_file_name)
    with wave.Wave_read(new_file_name) as audio_wav:
        chanel_number = audio_wav.getnchannels()
        sample_rate = audio_wav.getframerate()
        audio_bit = audio_wav.getsampwidth()*8
        play_time = audio_wav.getnframes()/sample_rate
    if play_time>=60:
        client = StorageClient("voicetransform-demo")
        client.uploadFile(new_file_name.strip("./"), new_file_name)
    return chanel_number, sample_rate, audio_bit, play_time, new_file_name

def offline_transcribe(lang, rate, nchannel, maxAlternatives, separate, play, file_name):
    
    sst_client.updateConfig_offline(lang, rate, nchannel, maxAlternatives, separate)
    if float(play)>=60:
        result = sst_client.longFileRecognize("gs://voicetransform-demo"+file_name.strip("."), separate)
    else:
        result = sst_client.shortFileRecognize(file_name,separate)
    return result

with gr.Blocks() as demo:
    with gr.Tab("STT(Offline)"):
        with gr.Row():
            with gr.Column(scale=1):
                lang_offline = gr.Dropdown(sst_client.models.keys(),label="语言")
                sample_rate_offline = gr.Text(interactive=False, label="采样率", placeholder="上传音频自动获取")
                chanel_number_offline = gr.Number(value=1, interactive=False,label="通道数")
                auto_bit_offline = gr.Number(16, interactive=False, label="音频位深")
                maxAlternatives_offline = gr.Number(value=1, minimum=1, maximum=30,label="识别假设最大数量")
                separateRecogn_offline = gr.Radio(choices=[("是", True), ("否", False)],value = False, label="是否区分音道")
                play_time = gr.Text(visible=False)
                file_name = gr.Text(visible=False)
            with gr.Column(scale=2):
                audio_input_offline = gr.Audio(sources=["upload"], type="filepath", format="wav")
                run_recogn = gr.Button("执行转录")
        offline_output = gr.Text("转录结果", show_copy_button=True)
        audio_input_offline.upload(upload, audio_input_offline, [chanel_number_offline, sample_rate_offline, auto_bit_offline, play_time, file_name])
        run_recogn.click(offline_transcribe, inputs = [
            lang_offline,
            sample_rate_offline, 
            chanel_number_offline, 
            maxAlternatives_offline,
            separateRecogn_offline,
            play_time,
            file_name
        ], outputs=offline_output)




    with gr.Tab("STT(OnLine)"):
        with gr.Row():
            with gr.Column(scale=1):
                lang = gr.Dropdown(sst_client.models.keys(),label="语言")
                chanel_number = gr.Label(1, label="通道数")
                maxAlternatives = gr.Label(1, label="识别假设最大数量")
                adaptation = gr.TextArea(label="自定义词汇", interactive=False)

                
            with gr.Column(scale=2):
                audio_input = gr.Audio(sources = ["microphone"],streaming=True)
                reset = gr.Button("Reset")
                
        streamResult = gr.Text(show_copy_button=True)
        save_result = gr.Button("保持结果")
        downfile = gr.File(file_count="multiple",label="识别结果文件")
        #reset.click(sst_client.resetClient)
        audio_input.stream(transcribe, [audio_input], [streamResult], queue=True)
        reset.click(sst_client.resetClient,inputs=lang, outputs=streamResult)
        save_result.click(sst_client.saveResult, outputs=downfile)


demo.launch(server_name="0.0.0.0",show_api=True,share = True,max_threads=1, auth=("Demo", "DemoPW"))



