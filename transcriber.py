import os
import math
import subprocess
import logging
import openai
import time
import sys
from pathlib import Path
import tempfile
from typing import List

logger = logging.getLogger(__name__)

# Constants
CHUNK_SIZE_LIMIT = 24 * 1024 * 1024  # 24 MB
DEFAULT_OVERLAP_SECONDS = 2

def transcribe_file(audio_path: str, model: str = None, overlap_seconds: int = DEFAULT_OVERLAP_SECONDS) -> str:
    """Transcribe an audio file using OpenAI Whisper API with automatic chunking for large files.
    
    Args:
        audio_path: Path to the audio file to transcribe
        model: Whisper model name (defaults to whisper-1 or WHISPER_MODEL env var)
        overlap_seconds: Number of seconds to overlap between chunks (default 2)
        
    Returns:
        Complete transcribed text as a single string
        
    Raises:
        RuntimeError: If transcription fails completely
    """
    # Set default model
    model = model or os.getenv('WHISPER_MODEL', 'whisper-1')
    logger.info(f"Starting transcription of {audio_path} using model {model}")
    
    # Get file size
    file_size = os.path.getsize(audio_path)
    logger.info(f"Audio file size: {file_size} bytes")
    
    if file_size <= CHUNK_SIZE_LIMIT:
        logger.info("File is within size limit, processing directly")
        try:
            with open(audio_path, "rb") as audio_file:
                response = openai.audio.transcriptions.create(
                    model=model,
                    file=audio_file
                )
            logger.info("Transcription successful")
            return response.text
        except Exception as e:
            logger.error(f"Direct transcription failed: {str(e)}")
            raise RuntimeError(f"Direct transcription failed: {str(e)}")
    else:
        logger.info("File exceeds size limit, processing in chunks")
        return _transcribe_large_file(audio_path, model, overlap_seconds, file_size)

def _transcribe_large_file(audio_path: str, model: str, overlap_seconds: int, file_size: int) -> str:
    """Handle transcription of large audio files by splitting into chunks."""
    try:
        # Get total duration using ffprobe
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        total_duration = float(subprocess.check_output(duration_cmd).decode().strip())
        logger.info(f"Total audio duration: {total_duration} seconds")
    except Exception as e:
        logger.error(f"Failed to get audio duration: {str(e)}")
        raise RuntimeError(f"Failed to get audio duration: {str(e)}")
    
    # Calculate chunk parameters
    avg_bitrate = (file_size * 8) / total_duration
    max_chunk_duration = (CHUNK_SIZE_LIMIT * 8) / avg_bitrate * 0.95
    effective_chunk_duration = max(max_chunk_duration - overlap_seconds, 0.1)
    num_chunks = math.ceil(total_duration / effective_chunk_duration)
    
    logger.info(f"Processing {num_chunks} chunks with {overlap_seconds}s overlap")
    logger.debug(f"Max chunk duration: {max_chunk_duration}s, effective: {effective_chunk_duration}s")
    
    transcripts = []
    temp_files_to_delete = []
    
    try:
        for i in range(num_chunks):
            start_time = i * effective_chunk_duration
            if start_time >= total_duration:
                break
                
            end_time = min(total_duration, start_time + max_chunk_duration)
            chunk_path = _create_chunk_file(audio_path, start_time, end_time, i)
            temp_files_to_delete.append(chunk_path)
            
            # Verify chunk size
            chunk_size = os.path.getsize(chunk_path)
            logger.debug(f"Chunk {i+1}: {start_time:.2f}-{end_time:.2f}s, size: {chunk_size} bytes")
            if chunk_size > CHUNK_SIZE_LIMIT:
                logger.warning(f"Chunk {i+1} exceeds size limit: {chunk_size} bytes")
            
            # Transcribe chunk
            try:
                logger.info(f"Transcribing chunk {i+1}/{num_chunks}")
                with open(chunk_path, "rb") as chunk_file:
                    response = openai.audio.transcriptions.create(
                        model=model,
                        file=chunk_file
                    )
                transcripts.append(response.text)
                logger.debug(f"Chunk {i+1} transcription successful, length: {len(response.text)}")
            except Exception as e:
                logger.error(f"Failed to transcribe chunk {i+1}: {str(e)}")
                continue
                
    finally:
        _cleanup_temp_files(temp_files_to_delete)
    
    if not transcripts:
        raise RuntimeError("Transcription failed: no chunks could be transcribed successfully")
    
    logger.info(f"Transcription completed with {len(transcripts)}/{num_chunks} successful chunks")
    return " ".join(transcripts)

def _create_chunk_file(audio_path: str, start_time: float, end_time: float, index: int) -> Path:
    """Create a temporary chunk file using ffmpeg."""
    audio_path = Path(audio_path)
    chunk_path = Path(tempfile.gettempdir()) / f"{audio_path.stem}_part{index+1}{audio_path.suffix}"
    
    try:
        subprocess.run([
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-i', str(audio_path),
            '-to', str(end_time),
            '-c', 'copy',
            str(chunk_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create chunk {index+1}: {str(e)}")
        raise RuntimeError(f"Failed to create audio chunk: {str(e)}")
    
    return chunk_path

def _cleanup_temp_files(file_paths: List[Path]):
    """Clean up temporary files with retry mechanism."""
    if not file_paths:
        return
        
    logger.info(f"Starting cleanup of {len(file_paths)} temporary files")
    failed_deletions = 0
    
    for temp_path in file_paths:
        if not temp_path.exists():
            continue
            
        max_retries = 3
        deleted = False
        
        for attempt in range(max_retries):
            try:
                temp_path.unlink()
                logger.debug(f"Deleted temporary file: {temp_path}")
                deleted = True
                break
            except PermissionError as e:
                if sys.platform == "win32" and attempt < max_retries - 1:
                    wait_time = 0.5 * (attempt + 1)
                    logger.warning(
                        f"PermissionError deleting {temp_path}, retry {attempt+1}/{max_retries} in {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                logger.error(f"Failed to delete {temp_path}: {str(e)}")
                failed_deletions += 1
                break
            except FileNotFoundError:
                logger.debug(f"File already deleted: {temp_path}")
                deleted = True
                break
            except Exception as e:
                logger.error(f"Failed to delete {temp_path}: {str(e)}")
                failed_deletions += 1
                break
    
    if failed_deletions:
        logger.error(f"Failed to delete {failed_deletions} temporary files")
    else:
        logger.info("All temporary files cleaned up successfully")