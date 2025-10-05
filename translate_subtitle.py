import google.generativeai as genai
import pysrt
import time
from config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def translate_subtitle(input_file, output_file, target_language='Vietnamese'):
    """
    Translate subtitle file using Google Gemini

    Args:
        input_file: Path to input .srt file
        output_file: Path to output .srt file
        target_language: Target language for translation (default: Vietnamese)
    """

    # Load subtitle file
    subs = pysrt.open(input_file)

    # Initialize Gemini model
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    print(f"Translating {len(subs)} subtitle entries to {target_language}...")
    print(f"Estimated time: ~{len(subs) * 6 / 60:.1f} minutes")

    # Translate each subtitle
    for i, sub in enumerate(subs, 1):
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Store original text
                original_text = sub.text

                prompt = f"Translate this subtitle to {target_language}. Only return the translated text, no explanations:\n\n{original_text}"

                response = model.generate_content(prompt)
                translated_text = response.text.strip()

                # Combine original and translated with yellow color for translation
                sub.text = f"{original_text}\n<font color=\"yellow\">{translated_text}</font>"

                print(f"Translated {i}/{len(subs)}", end='\r')

                # Save progress every 50 subtitles
                if i % 50 == 0:
                    subs.save(output_file, encoding='utf-8')
                    print(f"\nProgress saved at {i}/{len(subs)}")

                # Rate limiting: 10 requests/min = 6 seconds between requests
                time.sleep(6)
                break

            except Exception as e:
                retry_count += 1
                if "429" in str(e) or "quota" in str(e).lower():
                    wait_time = 60 * retry_count
                    print(f"\nRate limit hit at {i}/{len(subs)}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif retry_count >= max_retries:
                    print(f"\nError translating subtitle {i} after {max_retries} retries: {e}")
                    break
                else:
                    print(f"\nRetrying subtitle {i} (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(5)

    # Save final translated subtitles
    subs.save(output_file, encoding='utf-8')
    print(f"\nTranslation complete! Saved to: {output_file}")

if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python translate_subtitle.py <input.srt> [output.srt] [language]")
        print("Example: python translate_subtitle.py movie.srt movie_vi.srt Vietnamese")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.srt', '_translated.srt')
    language = sys.argv[3] if len(sys.argv) > 3 else 'Vietnamese'

    translate_subtitle(input_file, output_file, language)
