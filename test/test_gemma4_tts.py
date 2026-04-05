import unittest
import os
import sys
import wave

# Import current module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from gemma4.tts import save_tts

class TestGemma4TTS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_output = "test_tts_vn.wav"
        cls.output_dir = os.path.join(project_root, "output")
        cls.full_path = os.path.join(cls.output_dir, cls.test_output)

    def test_vietnamese_tts(self):
        print("\n[*] Testing Vietnamese TTS...")
        text = "Xin chào, đây là bản thử nghiệm giọng nói tiếng Việt từ hệ thống Gemma 4."
        
        try:
            path = save_tts(text, self.test_output)
            print(f"[+] TTS saved to: {path}")
            
            # Verify file existence
            self.assertTrue(os.path.exists(path))
            
            # Verify it's a valid wave file
            with wave.open(path, 'rb') as f:
                params = f.getparams()
                print(f"[*] Wave params: {params}")
                self.assertGreater(params.nframes, 0)
                self.assertEqual(params.nchannels, 1) # Mono
                self.assertEqual(params.framerate, 24000) # Kokoro v1.0 default
                
        except Exception as e:
            self.fail(f"TTS generation failed: {e}")

if __name__ == "__main__":
    # Remove config_dunp from sys.argv for unittest
    if len(sys.argv) > 1 and sys.argv[1] == 'config_dunp':
        sys.argv.pop(1)
    unittest.main()
