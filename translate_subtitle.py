import google.generativeai as genai
import pysrt
import time
from config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def translate_subtitle(input_file, output_file, target_language='Vietnamese', batch_size=50, start_from=1, end_at=None):
    """
    Translate subtitle file using Google Gemini in batches

    Args:
        input_file: Path to input .srt file
        output_file: Path to output .srt file
        target_language: Target language for translation (default: Vietnamese)
        batch_size: Number of subtitles to translate per batch (default: 50)
        start_from: Subtitle number to start from (default: 1)
        end_at: Subtitle number to end at (default: None = translate all)
    """

    # Load subtitle file
    subs = pysrt.open(input_file)

    # Initialize Gemini model
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    # Calculate starting batch
    start_index = start_from - 1
    end_index = end_at if end_at else len(subs)
    total_batches = (len(subs) + batch_size - 1) // batch_size
    remaining = end_index - start_index

    print(f"Translating {len(subs)} subtitle entries to {target_language}...")
    if start_from > 1 or end_at:
        range_text = f"#{start_from}" + (f" to #{end_at}" if end_at else " to end")
        print(f"Processing range: {range_text} ({remaining} subtitles)")
    print(f"Using batch mode: {batch_size} subtitles per batch ({total_batches} batches)")
    print(f"Estimated time: ~{(remaining // batch_size + 1) * 10 / 60:.1f} minutes")

    # Process in batches, starting from start_index
    for batch_num in range(start_index, end_index, batch_size):
        batch_end = min(batch_num + batch_size, end_index)
        batch_subs = subs[batch_num:batch_end]

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Build batch prompt
                batch_text = []
                for i, sub in enumerate(batch_subs):
                    batch_text.append(f"[{i+1}] {sub.text}")

                batch_content = "\n\n".join(batch_text)

                prompt = f"""Translate these subtitles to {target_language}.
Return ONLY the translations in the same numbered format [1], [2], etc.
Each translation should be on the SAME LINE as its number, even if it's long.
Keep the same number of entries. Do not add explanations.

{batch_content}"""

                response = model.generate_content(prompt)
                translations = response.text.strip()

                # Parse translations - handle multi-line by using regex
                import re
                trans_lines = []
                # Match [N] followed by any text up to the next [N] or end
                pattern = r'\[(\d+)\]\s*(.+?)(?=\[\d+\]|$)'
                matches = re.findall(pattern, translations, re.DOTALL)
                for num, text in matches:
                    trans_lines.append(text.strip())

                # Apply translations to subtitles
                for i, sub in enumerate(batch_subs):
                    if i < len(trans_lines):
                        original_text = sub.text
                        translated_text = trans_lines[i]
                        sub.text = f"{original_text}\n<font color=\"yellow\">{translated_text}</font>"

                # Save progress after each batch
                subs.save(output_file, encoding='utf-8')
                print(f"Batch {(batch_num // batch_size) + 1}/{total_batches} complete ({batch_end}/{len(subs)} subtitles)")

                # Rate limiting: 10 requests/min = 6 seconds between requests
                time.sleep(6)
                break

            except Exception as e:
                retry_count += 1
                if "429" in str(e) or "quota" in str(e).lower():
                    print(f"\nQuota exceeded at batch {(batch_num // batch_size) + 1}. Error: {str(e)[:200]}")
                    print(f"Please wait for quota reset (typically resets daily)")
                    break
                elif retry_count >= max_retries:
                    print(f"\nError translating batch {(batch_num // batch_size) + 1} after {max_retries} retries: {e}")
                    break
                else:
                    print(f"\nRetrying batch {(batch_num // batch_size) + 1} (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(5)

    # Save final translated subtitles
    subs.save(output_file, encoding='utf-8')
    print(f"\nTranslation complete! Saved to: {output_file}")

if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python translate_subtitle.py <input.srt> [output.srt] [language] [start_from] [end_at]")
        print("Example: python translate_subtitle.py movie.srt movie_vi.srt Vietnamese 1 150")
        print("Example: python translate_subtitle.py movie.srt movie_vi.srt Vietnamese 151")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.srt', '_translated.srt')
    language = sys.argv[3] if len(sys.argv) > 3 else 'Vietnamese'
    start_from = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    end_at = int(sys.argv[5]) if len(sys.argv) > 5 else None

    translate_subtitle(input_file, output_file, language, batch_size=50, start_from=start_from, end_at=end_at)
