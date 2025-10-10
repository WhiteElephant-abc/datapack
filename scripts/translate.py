import os
import json
import glob
from openai import OpenAI

# --- Configuration ---
SOURCE_LANG = "zh_cn"
TARGET_LANGS = ["en_us", "ru_ru", "ja_jp", "ko_kr", "pt_br", "es_es", "fr_fr"]
ASSETS_ROOT = "Localization-Resource-Pack/assets"
TRANSLATE_DIR = "translate"

# DeepSeek API settings
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-reasoner"
TEMPERATURE = 1.3

# --- Helper Functions ---
def find_source_files(assets_root, source_lang):
    """Find all source language files (e.g., zh_cn.json) under the assets root."""
    return glob.glob(f"{assets_root}/**/lang/{source_lang}.json", recursive=True)

def translate_namespace(client, source_file_path):
    """Translates a single namespace found via its source file path."""
    print(f"--- Processing namespace for: {source_file_path} ---")
    namespace_dir = os.path.dirname(os.path.dirname(source_file_path))

    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading source file {source_file_path}: {e}")
        return

    for lang in TARGET_LANGS:
        # Determine paths
        relative_lang_path = os.path.join(os.path.basename(namespace_dir), "lang", f"{lang}.json")
        target_file_path = os.path.join(TRANSLATE_DIR, relative_lang_path)
        existing_translation_path = os.path.join(namespace_dir, "lang", f"{lang}.json")

        # Create target directory
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

        # Load existing translations from the original assets directory
        existing_translations = {}
        if os.path.exists(existing_translation_path):
            try:
                with open(existing_translation_path, 'r', encoding='utf-8') as f:
                    existing_translations = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load existing translation for {lang} in {namespace_dir}: {e}")

        # Determine what needs to be translated
        to_translate = {k: v for k, v in source_data.items() if k not in existing_translations}
        final_translations = existing_translations.copy()

        if not to_translate:
            print(f"Skipping {lang}: No new keys to translate.")
            if not os.path.exists(target_file_path):
                with open(target_file_path, 'w', encoding='utf-8') as f:
                    json.dump(final_translations, f, ensure_ascii=False, indent=4)
            continue

        print(f"Translating {len(to_translate)} new keys to {lang}...")

        try:
            prompt_json = json.dumps(to_translate, ensure_ascii=False, indent=2)
            prompt = f"""Translate the values in the following JSON object from Chinese to {lang}.
Maintain the original JSON structure and keys. Only return the translated JSON object as a valid JSON, without any other text or explanations.

Input JSON:
{prompt_json}
"""

            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional translator that translates JSON files. You will receive a JSON object and you must return ONLY the translated JSON object, with the same keys, as a valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                stream=False,
                response_format={"type": "json_object"}
            )

            response_text = response.choices[0].message.content.strip()
            newly_translated_data = json.loads(response_text)
            final_translations.update(newly_translated_data)

        except Exception as e:
            print(f"An error occurred during batch translation for {lang}: {e}")
            # Fallback: copy source text for keys that failed to translate
            final_translations.update(to_translate)

        # Write the combined translations to the target file
        with open(target_file_path, 'w', encoding='utf-8') as f:
            json.dump(final_translations, f, ensure_ascii=False, indent=4)

        print(f"Finished translating to {lang}. Output at {target_file_path}")

# --- Main Script ---
def main():
    if not API_KEY:
        print("Error: DEEPSEEK_API_KEY environment variable not set.")
        return

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    source_files = find_source_files(ASSETS_ROOT, SOURCE_LANG)
    if not source_files:
        print(f"No source language files ({SOURCE_LANG}.json) found in {ASSETS_ROOT}.")
        return

    for source_file in source_files:
        translate_namespace(client, source_file)

if __name__ == "__main__":
    main()