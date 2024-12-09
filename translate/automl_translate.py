from google.cloud import translate
from typing import List, Union

class AutoMLTranslator:
    def __init__(self, project_id: str):
        self.client = translate.TranslationServiceClient()
        self.project_id = project_id
        self.location = "us-central1"
        self.parent = f"projects/{project_id}/locations/{self.location}"

    def translate(self, 
                 text: Union[str, List[str]], 
                 model_id: str,
                 target_lang: str = "zh",
                 source_lang: str = "en") -> Union[str, List[str]]:
        """
        执行AutoML翻译
        
        Args:
            text: 要翻译的文本，可以是字符串或字符串列表
            model_id: AutoML模型ID
            target_lang: 目标语言代码
            source_lang: 源语言代码
            
        Returns:
            翻译后的文本，如果输入是字符串则返回字符串，如果输入是列表则返回列表
        """
        try:
            # 准备输入文本
            contents = [text] if isinstance(text, str) else text
            
            # 构建请求
            request = {
                "contents": contents,
                "model": f"{self.parent}/models/{model_id}",
                "target_language_code": target_lang,
                "source_language_code": source_lang,
                "parent": self.parent,
                "mime_type": "text/plain"
            }
            
            # 执行翻译
            response = self.client.translate_text(request=request)
            
            # 处理结果
            translations = [t.translated_text for t in response.translations]
            return translations[0] if isinstance(text, str) else translations
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return "" if isinstance(text, str) else []


def main():
    # 使用示例
    translator = AutoMLTranslator(project_id="925998980422")
    
    # 单个文本翻译
    text = "There was a problem loading the traffic report"
    result = translator.translate(
        text=text,
        model_id="NM2af21d7d99679993"
    )
    print(f"单个翻译结果: {result}")
    
    # 批量翻译示例
    texts = ["Hello world", "Good morning"]
    results = translator.translate(
        text=texts,
        model_id="NM2af21d7d99679993"
    )
    print(f"批量翻译结果: {results}")


if __name__ == "__main__":
    main()