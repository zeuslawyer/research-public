# YouTube Content Generator

Automated YouTube content generation using multiple LLM APIs (DeepSeek, Gemini, Claude) via LiteLLM.

## Features

This script processes a video transcript and generates:

1. **YouTube Timestamps** (DeepSeek) - Copy-pastable timestamps for video descriptions
2. **Marketing Summary** (Gemini 2.5 Lite) - Compelling summary for marketing activities
3. **SEO-Optimized Titles** (Claude) - 5 titles optimized for search and clicks
4. **Thumbnail Concepts** (Gemini 2.5 Lite) - 5 creative thumbnail ideas
5. **Show Notes** (Gemini 2.5 Lite) - SEO-optimized video description

Steps 3 and 4 (titles and thumbnails) run in parallel for efficiency.

## Prerequisites

### Required Files

1. **transcript.txt** - Your video transcript
2. **knowledge_base.txt** - Instructions for target audience and tone of voice

### Required Environment Variables

Set the following API keys as environment variables:

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export OPENAI_API_KEY="your_openai_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Place your transcript in `transcript.txt`
2. Place your target audience/tone guidelines in `knowledge_base.txt`
3. Set your environment variables (see above)
4. Run the script:

```bash
python youtube_content_generator.py
```

## Output Files

The script generates 5 output files:

- `output_timestamps.txt` - YouTube chapter timestamps
- `output_marketing_summary.txt` - Marketing-focused summary
- `output_seo_titles.txt` - 5 SEO-optimized video titles
- `output_thumbnail_concepts.txt` - 5 thumbnail design concepts
- `output_show_notes.txt` - Complete show notes for video description

## Workflow

```
transcript.txt ──┬──> [DeepSeek] ──> Timestamps
                 │
                 ├──> [Gemini] ──> Marketing Summary ──┬──> [Claude] ──> SEO Titles
                 │                                      │
                 │                                      └──> [Gemini] ──> Thumbnails
                 │
knowledge_base.txt ──> [Used by Claude & Gemini for context]
                 │
transcript.txt ──┴──> [Gemini] ──> Show Notes
```

## Models Used

- **DeepSeek Chat** - Timestamp generation
- **Gemini 2.0 Flash Lite** - Marketing summary, thumbnails, show notes
- **Claude Sonnet 4.5** - SEO-optimized titles

## Error Handling

The script will:
- Validate all API keys are present before running
- Display helpful error messages if files are missing
- Print progress for each step
- Save each output to a separate file for easy review
