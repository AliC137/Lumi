"""
Test script to verify transcription logging is working
"""
from aistudio.core.database import SessionLocal
from aistudio.repositories.transcription_log_repository import TranscriptionLogRepository
from aistudio.schemas.transcription_log_out import TranscriptionLogCreate
import uuid

def test_transcription_logging():
    """Test creating transcription logs directly"""
    db = SessionLocal()
    
    try:
        # Create repository
        repo = TranscriptionLogRepository(db)
        
        # Test 1: Create a transcription log
        print("Test 1: Creating transcription log...")
        log = repo.create(
            file_uuid=str(uuid.uuid4()),
            text="This is a test transcription from audio file",
            lang="ru",
            service="vosk",
            stage=0,
            stage_name="original"
        )
        print(f"✓ Created transcription log with ID: {log.id}")
        
        # Test 2: Get total count
        print("\nTest 2: Getting total count...")
        total = repo.count_total()
        print(f"✓ Total transcription logs: {total}")
        
        # Test 3: Get by language stats
        print("\nTest 3: Getting language statistics...")
        lang_stats = repo.get_languages_stats()
        print(f"✓ Transcriptions by language: {lang_stats}")
        
        # Test 4: Get by service stats
        print("\nTest 4: Getting service statistics...")
        service_stats = repo.get_services_stats()
        print(f"✓ Transcriptions by service: {service_stats}")
        
        # Test 5: Get average text length
        print("\nTest 5: Getting average text length...")
        avg_length = repo.get_average_text_length()
        print(f"✓ Average text length: {avg_length:.2f} characters")
        
        # Test 6: Get uncorrected count
        print("\nTest 6: Getting uncorrected count...")
        uncorrected = repo.count_total() - repo.get_corrected_count()
        print(f"✓ Uncorrected transcriptions: {uncorrected}")
        
        # Test 7: Update correction
        print("\nTest 7: Testing correction update...")
        updated = repo.update_correction(log.id, "This is the corrected transcription text")
        print(f"✓ Updated transcription log {updated.id} with correction")
        
        # Test 8: Get corrected count
        print("\nTest 8: Getting corrected count after update...")
        corrected = repo.get_corrected_count()
        print(f"✓ Corrected transcriptions: {corrected}")
        
        print("\n✅ All transcription logging tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_transcription_logging()
