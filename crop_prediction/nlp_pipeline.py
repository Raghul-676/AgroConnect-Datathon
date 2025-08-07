from langdetect import detect
from deep_translator import GoogleTranslator
import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# ISO 639-1 → full name (for deep_translator)
LANG_CODE_MAP = {
    "en": "english",
    "ta": "tamil",
    "te": "telugu",
    "hi": "hindi",
    "ml": "malayalam",
    "kn": "kannada"
}

def detect_language(text):
    """Detect the input text's language using langdetect."""
    try:
        return detect(text)
    except:
        return "en"

def translate_to_english(text):
    """Translate given text to English from detected language."""
    src_lang_code = detect_language(text)
    src_lang = LANG_CODE_MAP.get(src_lang_code, "english")

    try:
        return GoogleTranslator(source=src_lang, target="english").translate(text)
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
        return text
    
def translate_from_english(text, target_lang):
    return GoogleTranslator(source='en', target=target_lang).translate(text)

def translate_to_original(text, target_lang_code):
    """Translate English text back to user's original language."""
    tgt_lang = LANG_CODE_MAP.get(target_lang_code, "english")

    try:
        return GoogleTranslator(source="english", target=tgt_lang).translate(text)
    except Exception as e:
        print(f"⚠️ Reverse translation error: {e}")
        return text

def extract_entities(text):
    """Extract crop, date/month, area, location, investment using spaCy."""
    doc = nlp(text)

    crop = None
    month = None
    area = 1.0  # Default to 1.0 acre if not found
    location = "Unknown"
    investment = 0.0  # Optional field

    for ent in doc.ents:
        if ent.label_ == "GPE":
            location = ent.text
        elif ent.label_ == "DATE":
            month = ent.text
        elif ent.label_ == "QUANTITY":
            try:
                area = float(ent.text.split()[0])
            except:
                pass
        elif ent.label_ in ["ORG", "PRODUCT"]:
            crop = ent.text
        elif ent.label_ == "MONEY":
            try:
                investment = float(ent.text.replace("₹", "").replace(",", "").split()[0])
            except:
                pass

    return crop, month, area, location, investment
