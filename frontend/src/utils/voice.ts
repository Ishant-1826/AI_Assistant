// Voice Input & Output Utilities using Web Speech API

// Speech Recognition (Voice Input)
export class VoiceInputManager {
  private recognition: any = null;
  public isSupported: boolean = false;
  private isListening: boolean = false;

  constructor() {
    const SpeechRecognition = 
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.isSupported = true;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';
    }
  }

  public start(
    onResult: (text: string, isFinal: boolean) => void,
    onError: (err: string) => void,
    onEnd: () => void
  ) {
    if (!this.isSupported || !this.recognition) {
      onError('Speech Recognition is not supported in this browser. Please try Chrome, Edge, or Safari.');
      return;
    }

    if (this.isListening) {
      this.stop();
      return;
    }

    this.isListening = true;

    this.recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const text = finalTranscript || interimTranscript;
      onResult(text, Boolean(finalTranscript));
    };

    this.recognition.onerror = (event: any) => {
      this.isListening = false;
      let msg = 'Microphone error: ' + event.error;
      if (event.error === 'not-allowed') {
        msg = 'Microphone permission denied. Please allow microphone access in your browser.';
      } else if (event.error === 'no-speech') {
        msg = 'No speech detected. Please speak into your microphone.';
      }
      onError(msg);
    };

    this.recognition.onend = () => {
      this.isListening = false;
      onEnd();
    };

    try {
      this.recognition.start();
    } catch (e: any) {
      this.isListening = false;
      onError('Could not start microphone: ' + e.message);
    }
  }

  public stop() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  public getStatus(): boolean {
    return this.isListening;
  }
}

// Speech Synthesis (Voice Output)
export class VoiceOutputManager {
  private synth: SpeechSynthesis | null = null;
  public isSupported: boolean = false;
  private currentUtterance: SpeechSynthesisUtterance | null = null;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
      this.isSupported = true;
    }
  }

  public getVoices(): SpeechSynthesisVoice[] {
    if (!this.synth) return [];
    return this.synth.getVoices();
  }

  public speak(
    text: string, 
    rate: number = 1.0, 
    preferredVoiceName?: string,
    onStart?: () => void,
    onEnd?: () => void
  ) {
    if (!this.synth) return;
    this.stop();

    // Clean markdown symbols for cleaner speech
    const cleanText = text
      .replace(/```[\s\S]*?```/g, 'Code block omitted.')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/#+\s/g, '')
      .replace(/[*_~]/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = Math.max(0.5, Math.min(2.0, rate));

    const voices = this.getVoices();
    if (preferredVoiceName && voices.length > 0) {
      const match = voices.find(v => v.name === preferredVoiceName);
      if (match) utterance.voice = match;
    } else if (voices.length > 0) {
      // Pick default English voice
      const eng = voices.find(v => v.lang.startsWith('en'));
      if (eng) utterance.voice = eng;
    }

    utterance.onstart = () => {
      if (onStart) onStart();
    };

    utterance.onend = () => {
      this.currentUtterance = null;
      if (onEnd) onEnd();
    };

    utterance.onerror = () => {
      this.currentUtterance = null;
      if (onEnd) onEnd();
    };

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
  }

  public stop() {
    if (this.synth) {
      this.synth.cancel();
      this.currentUtterance = null;
    }
  }

  public pause() {
    if (this.synth && this.synth.speaking) {
      this.synth.pause();
    }
  }

  public resume() {
    if (this.synth && this.synth.paused) {
      this.synth.resume();
    }
  }

  public isSpeaking(): boolean {
    return Boolean(this.synth && this.synth.speaking);
  }
}

export const voiceInput = new VoiceInputManager();
export const voiceOutput = new VoiceOutputManager();
