"""
FIXED TTS Module - Reliable Audio Playback
This version uses pygame which is much more reliable than PowerShell
"""
import asyncio
import edge_tts
import tempfile
import threading
import os
import time
import pygame

# Initialize pygame mixer once
pygame.mixer.init()

VOICE_MAP = {
    "hood": "en-US-GuyNeural",
    "calm": "en-US-AriaNeural",
    "default": "en-US-GuyNeural",
    "strict": "en-US-SteffanNeural",
    "motivational": "en-US-DavisNeural"
}


def _play_audio_pygame(audio_path):
    """
    Reliable audio playback using pygame
    This actually works on Windows unlike the PowerShell approach
    """
    try:
        print(f"[AUDIO] Loading: {audio_path}")
        pygame.mixer.music.load(audio_path)

        print(f"[AUDIO] Playing...")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        print(f"[AUDIO] Finished playing")
        return True
    except Exception as e:
        print(f"[AUDIO ERROR] {e}")
        return False


async def _generate_and_speak(text: str, personality: str):
    """
    Step 1: Generate speech with edge-tts
    Step 2: Save to temporary file
    Step 3: Play with pygame
    """
    voice = VOICE_MAP.get(personality, VOICE_MAP["default"])

    print(f"[TTS] Generating speech: '{text}' with voice: {voice}")

    communicate = edge_tts.Communicate(text, voice)

    # Create a unique temporary file
    temp_path = os.path.join(
        tempfile.gettempdir(),
        f"discipline_reminder_{int(time.time() * 1000)}.mp3"
    )

    try:
        # Generate the audio file
        print(f"[TTS] Saving to: {temp_path}")
        await communicate.save(temp_path)

        # Small delay to ensure file is fully written
        await asyncio.sleep(0.3)

        # Verify file exists and has content
        if not os.path.exists(temp_path):
            print(f"[TTS ERROR] File not created: {temp_path}")
            return

        file_size = os.path.getsize(temp_path)
        print(f"[TTS] File created successfully ({file_size} bytes)")

        # Play the audio (this is blocking, which is what we want)
        success = _play_audio_pygame(temp_path)

        if success:
            print(f"[TTS] ✅ Audio played successfully")
        else:
            print(f"[TTS] ❌ Audio playback failed")

    except Exception as e:
        print(f"[TTS ERROR] Exception during generation/playback: {e}")
    finally:
        # Clean up the temporary file
        await asyncio.sleep(0.5)
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"[TTS] Cleaned up temp file")
        except Exception as e:
            print(f"[TTS] Could not delete temp file: {e}")


def speak_background(text: str, personality: str = "default"):
    """
    Main function to call from your logic.py
    Runs TTS in a background thread so it doesn't block your main app
    """
    print(f"\n{'=' * 60}")
    print(f"[SPEAK_BACKGROUND] Called with text: '{text}'")
    print(f"[SPEAK_BACKGROUND] Personality: {personality}")
    print(f"{'=' * 60}\n")

    def thread_runner():
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async TTS function
            loop.run_until_complete(_generate_and_speak(text, personality))

            # Clean up
            loop.close()
        except Exception as e:
            print(f"[THREAD ERROR] {e}")

    # Start in a daemon thread (won't block app shutdown)
    thread = threading.Thread(target=thread_runner, daemon=True)
    thread.start()
    print(f"[SPEAK_BACKGROUND] Thread started: {thread.name}")


# Test function
def test_audio():
    """Run this to test if audio is working"""
    print("\n🎵 TESTING AUDIO SYSTEM 🎵\n")

    test_messages = [
        ("Yo! This is a test of the hood voice.", "hood"),
        ("This is a calm reminder test.", "calm"),
        ("This is a strict warning test.", "strict")
    ]

    for text, personality in test_messages:
        print(f"\nTesting: {personality}")
        speak_background(text, personality)
        time.sleep(6)  # Wait for each to finish

    print("\n✅ Audio test complete!")


if __name__ == "__main__":
    # Run test when file is executed directly
    test_audio()
