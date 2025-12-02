#!/usr/bin/env python3
"""
YouTube Content Generator
Uses multiple LLM APIs to generate YouTube video content from a transcript.
"""

import os
import asyncio
from litellm import completion
from typing import Dict, Any


class YouTubeContentGenerator:
    """Generate YouTube content using multiple LLM providers."""

    def __init__(self):
        """Initialize with API keys from environment variables."""
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

        # Validate all required API keys are present
        if not all([self.deepseek_api_key, self.openai_api_key,
                   self.gemini_api_key, self.anthropic_api_key]):
            missing = []
            if not self.deepseek_api_key:
                missing.append('DEEPSEEK_API_KEY')
            if not self.openai_api_key:
                missing.append('OPENAI_API_KEY')
            if not self.gemini_api_key:
                missing.append('GEMINI_API_KEY')
            if not self.anthropic_api_key:
                missing.append('ANTHROPIC_API_KEY')
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}")

    def read_file(self, filepath: str) -> str:
        """Read content from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error reading {filepath}: {str(e)}")

    def generate_timestamps(self, transcript: str) -> str:
        """
        Step 1: Use DeepSeek to generate YouTube timestamps.

        Args:
            transcript: The full video transcript

        Returns:
            Formatted timestamps ready for YouTube description
        """
        print("\n" + "="*80)
        print("STEP 1: Generating YouTube Timestamps with OpenAI")
        print("="*80)

        prompt = """You are a YouTube video editor. Analyze the following transcript and generate timestamps in a copy-pastable format for the YouTube video description.

Format each timestamp as:
HH:MM:SS - Brief description of the topic

Make sure the timestamps are:
- Accurate and helpful for viewers
- Cover all major topics and transitions
- Use proper time format (HH:MM:SS or MM:SS)
- Include clear, concise descriptions

Transcript:
{transcript}

Generate the timestamps now:"""

        response = completion(
            # model="deepseek/deepseek-chat",
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt.format(transcript=transcript)}],
            # api_key=self.deepseek_api_key
            api_key=self.openai_api_key
        )

        result = response.choices[0].message.content
        print(result)
        return result

    def generate_marketing_summary(self, transcript: str) -> str:
        """
        Step 2: Use Gemini to create a marketing summary.

        Args:
            transcript: The full video transcript

        Returns:
            Marketing-focused summary
        """
        print("\n" + "="*80)
        print("STEP 2: Generating Marketing Summary with Gemini 2.5 Lite")
        print("="*80)

        prompt = """You are a marketing expert. Analyze the following video transcript and create a compelling summary that would be useful for marketing activities.

The summary should:
- Highlight key value propositions and takeaways
- Emphasize benefits and outcomes for the audience
- Be engaging and persuasive
- Focus on what makes this content valuable and shareable
- Be suitable for social media posts, email campaigns, and promotional materials

Transcript:
{transcript}

Generate the marketing summary now:"""

        response = completion(
            model="gemini/gemini-2.0-flash-lite",
            messages=[
                {"role": "user", "content": prompt.format(transcript=transcript)}],
            api_key=self.gemini_api_key
        )

        result = response.choices[0].message.content
        print(result)
        return result

    def generate_seo_titles(self, summary: str, knowledge_base: str) -> str:
        """
        Step 3: Use Claude to generate SEO-optimized YouTube titles.

        Args:
            summary: The marketing summary from Gemini
            knowledge_base: Target audience and tone of voice instructions

        Returns:
            Five SEO-optimized YouTube titles
        """
        print("\n" + "="*80)
        print("STEP 3: Generating SEO-Optimized Titles with Claude")
        print("="*80)

        prompt = """You are a YouTube SEO expert. Based on the following marketing summary and target audience guidelines, generate 5 SEO-optimized YouTube video titles.

Target Audience & Tone Guidelines:
{knowledge_base}

Marketing Summary:
{summary}

Requirements for titles:
- Must be SEO-optimized with relevant keywords
- Should be compelling and click-worthy
- Follow YouTube best practices (typically 60-70 characters)
- Match the specified tone of voice and target audience
- Each title should offer a unique angle or hook

Generate 5 YouTube titles now:"""

        response = completion(
            model="anthropic/claude-sonnet-4-5-20250929",
            messages=[{"role": "user", "content": prompt.format(
                knowledge_base=knowledge_base,
                summary=summary
            )}],
            api_key=self.anthropic_api_key
        )

        result = response.choices[0].message.content
        print(result)
        return result

    def generate_thumbnail_concepts(self, summary: str) -> str:
        """
        Step 4: Use Gemini to generate thumbnail concepts (runs in parallel with step 3).

        Args:
            summary: The marketing summary from Gemini

        Returns:
            Five YouTube thumbnail concepts
        """
        print("\n" + "="*80)
        print("STEP 4: Generating Thumbnail Concepts with Gemini 2.5 Lite")
        print("="*80)

        prompt = """You are a YouTube thumbnail designer. Based on the following marketing summary, generate 5 creative thumbnail concepts that would attract clicks and views.

Marketing Summary:
{summary}

For each thumbnail concept, describe:
- Main visual element or focal point
- Text overlay (if any) - keep it short and impactful
- Color scheme and mood
- Composition and layout
- Why this concept would perform well

Generate 5 thumbnail concepts now:"""

        response = completion(
            model="gemini/gemini-2.0-flash-lite",
            messages=[
                {"role": "user", "content": prompt.format(summary=summary)}],
            api_key=self.gemini_api_key
        )

        result = response.choices[0].message.content
        print(result)
        return result

    def generate_show_notes(self, transcript: str, knowledge_base: str) -> str:
        """
        Step 5: Use Gemini to generate SEO-optimized show notes.

        Args:
            transcript: The full video transcript
            knowledge_base: Target audience guidelines

        Returns:
            SEO-optimized show notes
        """
        print("\n" + "="*80)
        print("STEP 5: Generating Show Notes with Gemini 2.5 Lite")
        print("="*80)

        prompt = """You are a content strategist specializing in YouTube SEO. Based on the following transcript and target audience guidelines, create comprehensive show notes that will resonate with the target audience and rank well in search.

Target Audience Guidelines:
{knowledge_base}

Transcript:
{transcript}

The show notes should include:
- A compelling overview/introduction
- Key topics covered with timestamps references
- Important links, resources, or references mentioned
- Relevant keywords naturally integrated
- Call-to-action for engagement
- Be well-formatted and easy to read
- Optimized for YouTube's description field and search algorithms

Generate the show notes now:"""

        response = completion(
            model="gemini/gemini-2.0-flash-lite",
            messages=[{"role": "user", "content": prompt.format(
                knowledge_base=knowledge_base,
                transcript=transcript
            )}],
            api_key=self.gemini_api_key
        )

        result = response.choices[0].message.content
        print(result)
        return result

    async def generate_parallel_content(self, summary: str, knowledge_base: str) -> Dict[str, str]:
        """
        Run steps 3 and 4 in parallel (titles and thumbnails).

        Args:
            summary: The marketing summary
            knowledge_base: Target audience and tone guidelines

        Returns:
            Dictionary with 'titles' and 'thumbnails' keys
        """
        # Create tasks for parallel execution
        titles_task = asyncio.to_thread(
            self.generate_seo_titles, summary, knowledge_base)
        thumbnails_task = asyncio.to_thread(
            self.generate_thumbnail_concepts, summary)

        # Run in parallel
        titles, thumbnails = await asyncio.gather(titles_task, thumbnails_task)

        return {
            'titles': titles,
            'thumbnails': thumbnails
        }

    def save_output(self, content: str, filename: str):
        """Save content to a file."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nSaved to: {filename}")

    async def generate_all_content(self, transcript_file: str, knowledge_base_file: str):
        """
        Main workflow to generate all YouTube content.

        Args:
            transcript_file: Path to transcript.txt
            knowledge_base_file: Path to knowledge_base.txt
        """
        print("\n" + "="*80)
        print("YOUTUBE CONTENT GENERATOR")
        print("="*80)

        # Read input files
        print("\nReading input files...")
        transcript = self.read_file(transcript_file)
        knowledge_base = self.read_file(knowledge_base_file)
        print(f"✓ Loaded transcript ({len(transcript)} characters)")
        print(f"✓ Loaded knowledge base ({len(knowledge_base)} characters)")

        # Step 1: Generate timestamps with DeepSeek
        timestamps = self.generate_timestamps(transcript)
        self.save_output(timestamps, 'output_timestamps.txt')

        # Step 2: Generate marketing summary with Gemini
        marketing_summary = self.generate_marketing_summary(transcript)
        self.save_output(marketing_summary, 'output_marketing_summary.txt')

        # Steps 3 & 4: Generate titles and thumbnails in parallel
        print("\n" + "="*80)
        print("Running Steps 3 & 4 in Parallel...")
        print("="*80)
        parallel_results = await self.generate_parallel_content(marketing_summary, knowledge_base)

        self.save_output(parallel_results['titles'], 'output_seo_titles.txt')
        self.save_output(
            parallel_results['thumbnails'], 'output_thumbnail_concepts.txt')

        # Step 5: Generate show notes with Gemini
        show_notes = self.generate_show_notes(transcript, knowledge_base)
        self.save_output(show_notes, 'output_show_notes.txt')

        print("\n" + "="*80)
        print("ALL CONTENT GENERATED SUCCESSFULLY!")
        print("="*80)
        print("\nOutput files created:")
        print("  1. output_timestamps.txt")
        print("  2. output_marketing_summary.txt")
        print("  3. output_seo_titles.txt")
        print("  4. output_thumbnail_concepts.txt")
        print("  5. output_show_notes.txt")


async def main():
    """Main entry point."""
    generator = YouTubeContentGenerator()

    # File paths
    transcript_file = 'transcript.txt'
    knowledge_base_file = 'knowledge_base.txt'

    try:
        await generator.generate_all_content(transcript_file, knowledge_base_file)
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease ensure both files exist:")
        print(f"  - {transcript_file}")
        print(f"  - {knowledge_base_file}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
