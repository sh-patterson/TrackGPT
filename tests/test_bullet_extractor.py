import unittest
from unittest.mock import patch
from bullet_extractor import extract_bullets

import openai

class TestBulletExtractor(unittest.TestCase):
    def setUp(self):
        # Ensure api_key is set so extract_bullets skips the key-check raise
        openai.api_key = "testkey"
        # Patch the OpenAI chat completions method to return a predictable response
        patcher = patch('openai.chat.completions.create')
        self.mock_create = patcher.start()
        self.addCleanup(patcher.stop)
        class FakeChoice:
            def __init__(self, content):
                self.message = type('Msg', (object,), {'content': content})
        class FakeResponse:
            def __init__(self, content):
                self.choices = [FakeChoice(content)]
        def fake_create(model, messages, temperature):
            # Return a JSON list with a single bullet including a speaker
            content = '[{"headline": "Test Headline", "body": "Test body text.", "speaker": "John Doe"}]'
            return FakeResponse(content)
        self.mock_create.side_effect = fake_create

    def test_extract_bullets_with_metadata(self):
        metadata = {
            "extractor_key": "Youtube",
            "title": "Sample Title",
            "upload_date": "20210101",
            "webpage_url": "http://example.com"
        }
        bullets = extract_bullets("dummy transcript", "TargetEntity", max_bullets=1, video_metadata=metadata)
        self.assertEqual(len(bullets), 1)
        bullet = bullets[0]
        self.assertEqual(bullet.headline, "Test Headline")
        self.assertEqual(bullet.body, "Test body text.")
        self.assertEqual(bullet.speaker, "John Doe")
        # Citation fields should be populated and normalized
        self.assertEqual(bullet.citation.platform, "YouTube")
        self.assertEqual(bullet.citation.title, "Sample Title")
        self.assertEqual(bullet.citation.date, "20210101")
        self.assertEqual(bullet.citation.url, "http://example.com")

    def test_extract_bullets_without_metadata(self):
        # Adjust the fake response to omit speaker for simplicity
        def fake_create_no_speaker(model, messages, temperature):
            content = '[{"headline": "Head only", "body": "Body only"}]'
            return type('R', (object,), {'choices': [type('C', (object,), {'message': type('M', (object,), {'content': content})})]})
        self.mock_create.side_effect = fake_create_no_speaker
        bullets = extract_bullets("text", "Target", max_bullets=1, video_metadata=None)
        self.assertEqual(len(bullets), 1)
        bullet = bullets[0]
        self.assertEqual(bullet.headline, "Head only")
        self.assertEqual(bullet.body, "Body only")
        # Default citation should be 'Unknown'
        self.assertEqual(bullet.citation.platform, "Unknown")
        self.assertEqual(bullet.citation.title, "Unknown")
        self.assertIsNone(bullet.citation.date)
        self.assertIsNone(bullet.citation.url)

if __name__ == "__main__":
    unittest.main()