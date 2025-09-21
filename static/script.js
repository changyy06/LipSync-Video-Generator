// Clean, working JavaScript for LipSync Video Generator
document.addEventListener('DOMContentLoaded', function() {
    console.log('LipSync App initialized');

    // ===== AWS CONTENT GENERATION =====
    const generateContentBtn = document.getElementById('generateContentBtn');
    const contentPrompt = document.getElementById('contentPrompt');
    const contentResult = document.getElementById('contentResult');

    generateContentBtn.addEventListener('click', async function() {
        const prompt = contentPrompt.value.trim();
        if (!prompt) {
            alert('Please enter a content prompt');
            return;
        }

        generateContentBtn.disabled = true;
        generateContentBtn.textContent = 'Generating...';
        contentResult.innerHTML = '';

        try {
            const response = await fetch('/generate-content', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    content_type: 'general',
                    language: 'en'
                })
            });

            const data = await response.json();

            if (response.ok && data.success !== false) {
                // Handle both 'content' and 'generated_text' field names
                const content = data.content || data.generated_text || 'No content generated';
                contentResult.innerHTML = `
                    <div class="success">
                        <h3>Generated Content:</h3>
                        <div class="content">${content.replace(/\n/g, '<br>')}</div>
                        <button onclick="copyToTextPrompt('${content.replace(/'/g, "\\'")}')">📋 Use This Text</button>
                        <small>Model: ${data.model || 'AWS Bedrock'}</small>
                    </div>
                `;
            } else {
                throw new Error(data.error || 'Failed to generate content');
            }
        } catch (error) {
            contentResult.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        } finally {
            generateContentBtn.disabled = false;
            generateContentBtn.textContent = '✨ Generate Content';
        }
    });

    // ===== TRANSLATION =====
    const translateBtn = document.getElementById('translateBtn');
    const translateText = document.getElementById('translateText');
    const targetLanguage = document.getElementById('targetLanguage');
    const translateResult = document.getElementById('translateResult');

    translateBtn.addEventListener('click', async function() {
        const text = translateText.value.trim();
        if (!text) {
            alert('Please enter text to translate');
            return;
        }

        translateBtn.disabled = true;
        translateBtn.textContent = 'Translating...';
        translateResult.innerHTML = '';

        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    source_language: 'en',
                    target_language: targetLanguage.value
                })
            });

            const data = await response.json();

            if (response.ok && data.success !== false) {
                translateResult.innerHTML = `
                    <div class="success">
                        <h3>Translation:</h3>
                        <div><strong>Original:</strong> ${text}</div>
                        <div><strong>Translated:</strong> ${data.translated_text}</div>
                        <button onclick="copyToTextPrompt('${data.translated_text.replace(/'/g, "\\'")}')">📋 Use This Text</button>
                        <small>Service: ${data.service}</small>
                    </div>
                `;
            } else {
                throw new Error(data.error || 'Failed to translate');
            }
        } catch (error) {
            translateResult.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        } finally {
            translateBtn.disabled = false;
            translateBtn.textContent = '🌍 Translate';
        }
    });

    // ===== TRANSCRIPTION =====
    const audioFile = document.getElementById('audioFile');
    const transcribeBtn = document.getElementById('transcribeBtn');
    const transcribeResult = document.getElementById('transcribeResult');

    audioFile.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            transcribeBtn.style.display = 'inline-block';
        } else {
            transcribeBtn.style.display = 'none';
        }
    });

    transcribeBtn.addEventListener('click', async function() {
        const file = audioFile.files[0];
        if (!file) {
            alert('Please select an audio file');
            return;
        }

        transcribeBtn.disabled = true;
        transcribeBtn.textContent = 'Transcribing...';
        transcribeResult.innerHTML = '';

        try {
            const formData = new FormData();
            formData.append('audio_file', file);
            formData.append('language', 'en');

            const response = await fetch('/transcribe', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success !== false) {
                // Handle both 'transcript' and 'text' field names
                const transcript = data.transcript || data.text || 'No transcription available';
                transcribeResult.innerHTML = `
                    <div class="success">
                        <h3>Transcription:</h3>
                        <div class="content">${transcript}</div>
                        <button onclick="copyToTextPrompt('${transcript.replace(/'/g, "\\'")}')">📋 Use This Text</button>
                        <small>File: ${file.name}</small>
                    </div>
                `;
            } else {
                throw new Error(data.error || 'Failed to transcribe');
            }
        } catch (error) {
            transcribeResult.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        } finally {
            transcribeBtn.disabled = false;
            transcribeBtn.textContent = '📝 Transcribe';
        }
    });

    // ===== LIPSYNC FORM HANDLING =====
    const lipsyncForm = document.getElementById('lipsyncForm');
    const audioInputRadios = document.querySelectorAll('input[name="audio_input_type"]');
    const faceInputRadios = document.querySelectorAll('input[name="input_face_type"]');
    const audioUploadSection = document.getElementById('audioUploadSection');
    const faceUploadSection = document.getElementById('faceUploadSection');
    const faceUrlSection = document.getElementById('faceUrlSection');
    const loadingSection = document.getElementById('loadingSection');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');

    // Handle audio input type changes
    audioInputRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'audio') {
                audioUploadSection.style.display = 'block';
            } else {
                audioUploadSection.style.display = 'none';
            }
        });
    });

    // Handle face input type changes
    faceInputRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'url') {
                faceUploadSection.style.display = 'none';
                faceUrlSection.style.display = 'block';
            } else {
                faceUploadSection.style.display = 'block';
                faceUrlSection.style.display = 'none';
            }
        });
    });

    // Handle form submission
    lipsyncForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Clear previous results
        resultSection.innerHTML = '';
        errorSection.innerHTML = '';
        loadingSection.style.display = 'block';

        const generateVideoBtn = document.getElementById('generateVideoBtn');
        generateVideoBtn.disabled = true;
        generateVideoBtn.textContent = '⏳ Processing...';

        try {
            const formData = new FormData(lipsyncForm);
            
            console.log('Submitting LipSync form with data:', Array.from(formData.keys()));

            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                resultSection.innerHTML = `
                    <div class="success">
                        <h4>✅ ${data.message}</h4>
                        ${data.video_url ? `
                            <div style="margin: 15px 0;">
                                <a href="${data.video_url}" target="_blank" class="btn">🎬 View Video</a>
                                <a href="${data.video_url}" download class="btn">📥 Download Video</a>
                            </div>
                        ` : ''}
                        ${data.downloaded_path ? `
                            <p><strong>📁 Saved to:</strong> ${data.downloaded_path}</p>
                        ` : ''}
                        ${data.warning ? `<p class="warning">⚠️ ${data.warning}</p>` : ''}
                    </div>
                `;
            } else {
                throw new Error(data.error || 'Failed to generate video');
            }
        } catch (error) {
            errorSection.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
        } finally {
            loadingSection.style.display = 'none';
            generateVideoBtn.disabled = false;
            generateVideoBtn.textContent = '🎬 Generate LipSync Video';
        }
    });
});

// ===== UTILITY FUNCTIONS =====
function copyToTextPrompt(text) {
    const textPrompt = document.getElementById('textPrompt');
    if (textPrompt) {
        textPrompt.value = text;
        textPrompt.focus();
        
        // Visual feedback
        textPrompt.style.backgroundColor = '#e8f5e8';
        setTimeout(() => {
            textPrompt.style.backgroundColor = '';
        }, 1000);
    }
}