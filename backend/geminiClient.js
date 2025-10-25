class GeminiClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    // Initialize real Gemini connection here
  }

  async sendAudio(audioBuffer) {
    // For now, echo back input (simulate Gemini)
    return audioBuffer;
  }
}

module.exports = { GeminiClient };
