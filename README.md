# Python Subtitle Translator

A Python application that uses Google Gemini AI to translate film subtitles.

## Features

- Translate subtitle files (.srt) to any language
- Powered by Google Gemini AI (gemini-2.5-flash model)
- Vietnamese translation appears in yellow below English text
- Automatic rate limiting (10 requests/min for free tier)
- Auto-save progress every 50 subtitles
- Retry logic for rate limit errors
- Environment-based configuration
- Simple command-line interface

## Prerequisites

- Python 3.7+
- Google Gemini API key

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd python-research
```

### 2. Create virtual environment

```bash
python3 -m venv venv
```

### 3. Activate virtual environment

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API key

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Open `.env` file and replace `your_api_key_here` with your actual API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## Usage

### Basic usage (translates to Vietnamese by default)

```bash
python translate_subtitle.py input.srt
```

This creates `input_translated.srt`

### Specify output file

```bash
python translate_subtitle.py input.srt output.srt
```

### Translate to different language

```bash
python translate_subtitle.py input.srt output.srt Spanish
```

### For large files (run in background)

For files with many subtitles (1000+ lines), use `nohup` to run in background:

```bash
nohup bash -c 'source venv/bin/activate && python translate_subtitle.py "input.srt" "output.srt"' > translation.log 2>&1 &
```

Monitor progress:
```bash
tail -f translation.log
```

Check if process is running:
```bash
ps aux | grep translate_subtitle
```

## Configuration Files

- `.env` - Environment variables and API keys
- `config.py` - Application configuration loader
- `requirements.txt` - Python dependencies

## Project Structure

```
python-research/
├── .env                    # Environment variables
├── config.py              # Configuration loader
├── translate_subtitle.py  # Main translation script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Dependencies

- `python-dotenv` - Environment variable management
- `google-generativeai` - Google Gemini AI SDK
- `pysrt` - Subtitle file parser

## Rate Limits (Free Tier)

- **10 requests per minute**
- **250,000 tokens per minute**
- **250 requests per day**

The script automatically handles rate limiting with 6-second delays between requests.

## Notes

- The script translates each subtitle entry individually
- Vietnamese translation appears in **yellow color** below English text
- Translation progress is shown in the terminal
- Progress auto-saves every 50 subtitles
- **Estimated time**: ~6 seconds per subtitle (e.g., 1200 subtitles ≈ 2 hours)
- Make sure your API key has sufficient quota
- Always activate the virtual environment before running the script
- The script will retry automatically if rate limits are hit

## Deactivate Virtual Environment

When done, deactivate the virtual environment:

```bash
deactivate
```
