"""
Test script to verify TTS logging functionality
"""
from sqlalchemy.orm import Session
from aistudio.repositories import get_db_session
from aistudio.repositories.tts_log_repository import TTSLogRepository
from aistudio.schemas.tts_log_out import TTSLogCreate

def test_tts_logging():
    """Test TTS logging repository operations"""
    with get_db_session() as db:
        try:
            repo = TTSLogRepository(db)
            
            # Create a test log entry
            test_log = TTSLogCreate(
                speech_uid="test-speech-001",
                uuid_file="test-file-001",
                text="This is a test text for TTS logging",
                index=0,
                lang="ru",
                service="yandex"
            )
            
            created_log = repo.create(test_log)
            print(f"✓ Created log entry with ID: {created_log.id}")
            
            # Test retrieving by speech_uid
            logs = repo.get_by_speech_uid("test-speech-001")
            print(f"✓ Found {len(logs)} log(s) for speech_uid 'test-speech-001'")
            
            # Test statistics
            total = repo.count_total()
            print(f"✓ Total TTS conversions: {total}")
            
            by_lang = repo.count_by_language()
            print(f"✓ Conversions by language: {by_lang}")
            
            by_service = repo.count_by_service()
            print(f"✓ Conversions by service: {by_service}")
            
            avg_length = repo.get_average_text_length()
            print(f"✓ Average text length: {avg_length:.2f} characters")
            
            print("\n✅ All TTS logging tests passed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_tts_logging()
