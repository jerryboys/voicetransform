import pandas as pd
import time
from google.cloud import storage
from io import StringIO
from google.cloud import translate
from comet import download_model, load_from_checkpoint

def read_csv_from_gcs(bucket_name, blob_name):
    """Read CSV file from Google Cloud Storage"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    content = blob.download_as_text()
    return pd.read_csv(StringIO(content))


def translate_text_v2(source: str,target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target,source_language=source)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))

    return result["translatedText"]


# Initialize Translation client
def translate_text_v3(
    source: str,target: str,text: str = "YOUR_TEXT_TO_TRANSLATE", project_id: str = "YOUR_PROJECT_ID"
) -> translate.TranslationServiceClient:
    """Translating Text."""

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Translate text from English to French
    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        request={
            "parent": parent,
            "contents":[text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": source,
            "target_language_code": target,
        }
    )

    return response.translations[0].translated_text

def compare_translations(project_id="test"):
    # Read CSV from GCS
    df = read_csv_from_gcs("demo", "translate/input.csv")
    
    results_v2 = []
    results_v3 = []
    time_v2 = []
    time_v3 = []
    
    # Process each row
    for _, row in df.iterrows():
        # Translate using V2
        start_time = time.time()
        mt_v2 = translate_text_v2(row['source_language'], row['target_language'], row['src'])
        time_v2.append(time.time() - start_time)
        
        # Translate using V3
        start_time = time.time()
        mt_v3 = translate_text_v3(row['source_language'], row['target_language'], row['src'], project_id)
        time_v3.append(time.time() - start_time)
        
        # Prepare data for COMET evaluation
        results_v2.append({
            "src": row['src'],
            "mt": mt_v2,
            "ref": row['ref']
        })
        
        results_v3.append({
            "src": row['src'],
            "mt": mt_v3,
            "ref": row['ref']
        })
    
    # Load COMET model
    model_path = download_model("Unbabel/wmt22-comet-da")
    model = load_from_checkpoint(model_path)
    
    # Evaluate translations
    print("=== Translation Quality Comparison ===")
    print("\nV2 Translation Quality:")
    quality_v2 = model.predict(results_v2, batch_size=8, gpus=1)
    print(quality_v2)
    
    print("\nV3 Translation Quality:")
    quality_v3 = model.predict(results_v3, batch_size=8, gpus=1)
    print(quality_v3)
    
    # Print timing statistics
    print("\n=== Translation Speed Comparison ===")
    print(f"V2 Average Time: {sum(time_v2)/len(time_v2):.3f} seconds")
    print(f"V3 Average Time: {sum(time_v3)/len(time_v3):.3f} seconds")

if __name__ == "__main__":
    compare_translations()