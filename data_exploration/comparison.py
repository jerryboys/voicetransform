import pandas as pd
import textwrap
from IPython.display import Markdown
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel
)

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

prompt = """
<角色>你是语音识别（Automatic Speech Recognition, ASR）领域的专家和评判员</角色>

<任务>
你将根据 <正确文字> 作为标准正确答案，评估提供的多段 <转录文字> 语音识别的正确率。
你将使用 ASR 领域衡量识别准确性的两个主要指标：错误率（Word Error Rate, WER）和字正确率（Word Correct, W.Corr），来进行多段 <转录文字> 和 <正确文字> 的正确率评估。

输出下面的结果：
1、在一个表格内输出每段<转录文字> 的 WER 结果 和 W.Corr 结果
2、综合考虑转录内容是否合乎逻辑和人类可读性，对于多端 <转录文字>，你推荐使用哪一个 <转录文字> 作为最终的优胜者？
3、提供详细的分析过程和推荐的原因
</任务>

"""

manual_results=""

correct_asr = "<正确文字>" + manual_results + "</正确文字> \n"
prompt = prompt + correct_asr

# print(prompt)
    
output_csv_file = "output_csv_file"
file_path = output_csv_file

# 使用 pandas 读取 CSV 文件，指定列名
df = pd.read_csv(file_path, names=['api_version', 'model_name', 'transcript'])

# 循环遍历每一行
for index, row in df.iterrows():
    # 打印行号
    # print(f"Row {index + 1}:")
    if index > 0 :
        # 打印列名和值
        model_info = "_" + str(index) + "_" + df.loc[index, 'api_version'] + "_" + df.loc[index, 'model_name']
        # print(f" {column}: {model_info}")

        # 读取所有 ASR 识别结果
        gcp_asr = "<转录文字" + model_info + ">" + df.loc[index, 'transcript'] + "</转录文字" + model_info + "> \n"
        prompt = prompt + gcp_asr

print("############################## Gemini 提示词 ######################################")
print(prompt)
print("############################################################################")

# Use a more deterministic configuration with a low temperature
generation_config = GenerationConfig(
    temperature=0,
    top_p=1,
    # top_k=1,
    candidate_count=1,
    max_output_tokens=8192,
)


contents = [
    prompt,
]

multimodal_model = GenerativeModel("gemini-1.5-pro-001")

responses = multimodal_model.generate_content(
    contents, generation_config=generation_config, stream=False)

print("############################ Gemini 评分结果 #################################")
gemini_assessment_result = responses.text
print(gemini_assessment_result)
print("############################################################################")


to_markdown(gemini_assessment_result)