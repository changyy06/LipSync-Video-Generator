#!/usr/bin/env python3
"""
Test Google Translate integration
"""

try:
    from googletrans import Translator
    
    def test_google_translate():
        print("🧪 Testing Google Translate...")
        
        translator = Translator()
        
        # Test basic translation
        text = "Hello, this is a test of Google Translate integration."
        
        languages_to_test = ['es', 'fr', 'de', 'zh', 'ja']
        
        for lang in languages_to_test:
            try:
                result = translator.translate(text, dest=lang)
                print(f"✅ {lang}: {result.text[:50]}...")
            except Exception as e:
                print(f"❌ {lang}: Error - {e}")
        
        print("✅ Google Translate test completed!")
        
    if __name__ == "__main__":
        test_google_translate()
        
except ImportError:
    print("❌ Google Translate not available. Install with: pip install googletrans==4.0.0rc1")