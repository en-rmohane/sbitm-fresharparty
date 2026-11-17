/**
 * SANSKRITI 2026 - Live Front Camera Selfie Capture
 * MediaDevices API, facingMode: "user", Track Release, and Safe Fallback
 */

class SelfieCameraManager {
  constructor(options) {
    this.videoEl = document.getElementById(options.videoId);
    this.canvasEl = document.getElementById(options.canvasId);
    this.previewImg = document.getElementById(options.previewImgId);
    this.captureBtn = document.getElementById(options.captureBtnId);
    this.retakeBtn = document.getElementById(options.retakeBtnId);
    this.fallbackContainer = document.getElementById(options.fallbackContainerId);
    this.fallbackInput = document.getElementById(options.fallbackInputId);
    this.cameraContainer = document.getElementById(options.cameraContainerId);

    this.stream = null;
    this.capturedImageData = null;
    this.captureMethod = 'live_camera';

    this.init();
  }

  async init() {
    this.attachEvents();
  }

  async startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this.showFallback('Camera is not supported on this browser/environment. You can upload a photo instead.');
      return;
    }

    try {
      const constraints = {
        video: {
          facingMode: 'user', // Prefer mobile front-facing camera
          width: { ideal: 1280 },
          height: { ideal: 960 },
        },
        audio: false,
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (this.videoEl) {
        this.videoEl.srcObject = this.stream;
        this.videoEl.style.display = 'block';
        if (this.previewImg) this.previewImg.style.display = 'none';
        if (this.captureBtn) this.captureBtn.style.display = 'inline-flex';
        if (this.retakeBtn) this.retakeBtn.style.display = 'none';
      }
    } catch (err) {
      console.warn('Camera access denied or failed:', err);
      let msg = 'Could not access the front camera. ';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg += 'Camera permission was denied. You may grant camera permission or use the manual photo upload below.';
      } else {
        msg += 'Please use the manual photo upload option below.';
      }
      this.showFallback(msg);
    }
  }

  capture() {
    if (!this.stream || !this.videoEl) return null;

    const width = this.videoEl.videoWidth || 640;
    const height = this.videoEl.videoHeight || 480;

    this.canvasEl.width = width;
    this.canvasEl.height = height;

    const ctx = this.canvasEl.getContext('2d');

    // Flip horizontally for natural mirror feel of front selfie
    ctx.translate(width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(this.videoEl, 0, 0, width, height);

    this.capturedImageData = this.canvasEl.toDataURL('image/jpeg', 0.88);
    this.captureMethod = 'live_camera';

    // Show preview & stop video tracks
    if (this.previewImg) {
      this.previewImg.src = this.capturedImageData;
      this.previewImg.style.display = 'block';
    }
    if (this.videoEl) this.videoEl.style.display = 'none';
    if (this.captureBtn) this.captureBtn.style.display = 'none';
    if (this.retakeBtn) this.retakeBtn.style.display = 'inline-flex';

    this.stopCameraTracks();
    return this.capturedImageData;
  }

  retake() {
    this.capturedImageData = null;
    this.startCamera();
  }

  stopCameraTracks() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
  }

  showFallback(message) {
    this.stopCameraTracks();
    if (this.cameraContainer) this.cameraContainer.style.display = 'none';
    if (this.fallbackContainer) {
      this.fallbackContainer.style.display = 'block';
      const hint = document.getElementById('cameraErrorHint');
      if (hint) hint.textContent = message;
    }
  }

  attachEvents() {
    if (this.captureBtn) {
      this.captureBtn.addEventListener('click', () => this.capture());
    }

    if (this.retakeBtn) {
      this.retakeBtn.addEventListener('click', () => this.retake());
    }

    // Manual upload fallback handler
    if (this.fallbackInput) {
      this.fallbackInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file.');
            return;
          }
          const reader = new FileReader();
          reader.onload = (event) => {
            this.capturedImageData = event.target.result;
            this.captureMethod = 'manual_upload';
            if (this.previewImg) {
              this.previewImg.src = this.capturedImageData;
              this.previewImg.style.display = 'block';
            }
          };
          reader.readAsDataURL(file);
        }
      });
    }

    // Clean up tracks when navigating away or unmounting
    window.addEventListener('beforeunload', () => this.stopCameraTracks());
  }

  getImageData() {
    return this.capturedImageData;
  }

  getMethod() {
    return this.captureMethod;
  }
}

window.SelfieCameraManager = SelfieCameraManager;

