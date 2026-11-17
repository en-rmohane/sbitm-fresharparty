/**
 * SANSKRITI 2026 - Mobile-First Faculty Approval Wizard
 * Orchestrates: Welcome -> Invitation -> Signature -> Selfie -> Blessing -> Confirmation -> Animated Stamp
 */

class FacultyApprovalWizard {
  constructor(config) {
    this.facultyId = config.facultyId;
    this.eventId = config.eventId;
    this.departmentId = config.departmentId;
    this.csrfToken = config.csrfToken;
    this.submitUrl = config.submitUrl;
    this.successRedirectUrl = config.successRedirectUrl;

    this.currentStep = 1;
    this.totalSteps = 5;

    this.signatureManager = null;
    this.cameraManager = null;

    this.init();
  }

  init() {
    // Initialize signature
    this.signatureManager = new SignaturePadManager('sigCanvas', 'clearSigBtn');

    // Initialize camera
    this.cameraManager = new SelfieCameraManager({
      videoId: 'selfieVideo',
      canvasId: 'selfieCanvas',
      previewImg: 'selfiePreviewImg',
      captureBtnId: 'btnCaptureSelfie',
      retakeBtnId: 'btnRetakeSelfie',
      cameraContainerId: 'cameraLiveContainer',
      fallbackContainerId: 'cameraFallbackContainer',
      fallbackInputId: 'manualSelfieInput',
    });

    this.attachNavigation();
    this.updateUI();
  }

  goToStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > this.totalSteps) return;

    // Validate current step before proceeding forward
    if (stepNumber > this.currentStep) {
      if (!this.validateStep(this.currentStep)) return;
    }

    // Camera handling
    if (stepNumber === 3) {
      // Starting camera on Step 3 (Selfie)
      setTimeout(() => this.cameraManager.startCamera(), 200);
    } else {
      // Stop tracks if moving away from camera step
      if (this.cameraManager) this.cameraManager.stopCameraTracks();
    }

    // Populate review summary when entering Step 5
    if (stepNumber === 5) {
      this.populateReviewSummary();
    }

    this.currentStep = stepNumber;
    this.updateUI();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  validateStep(step) {
    if (step === 1) {
      const consentCheck = document.getElementById('invitationConsentCheck');
      if (consentCheck && !consentCheck.checked) {
        Swal.fire({
          icon: 'info',
          title: 'Consent Required',
          text: 'Please confirm acknowledgement of the invitation to proceed.',
          background: '#3A1019',
          color: '#FFF8EB',
          confirmButtonColor: '#C6A15B',
        });
        return false;
      }
    } else if (step === 2) {
      if (this.signatureManager.isEmpty()) {
        Swal.fire({
          icon: 'warning',
          title: 'Signature Required',
          text: 'Please provide your digital signature on the pad above to proceed.',
          background: '#3A1019',
          color: '#FFF8EB',
          confirmButtonColor: '#C6A15B',
        });
        return false;
      }
    } else if (step === 3) {
      if (!this.cameraManager.getImageData()) {
        Swal.fire({
          icon: 'warning',
          title: 'Selfie Required',
          text: 'Please capture or upload a faculty selfie to proceed.',
          background: '#3A1019',
          color: '#FFF8EB',
          confirmButtonColor: '#C6A15B',
        });
        return false;
      }
    }
    return true;
  }

  updateUI() {
    // Hide all step sections, show current
    for (let i = 1; i <= this.totalSteps; i++) {
      const sec = document.getElementById(`stepSection${i}`);
      const dot = document.getElementById(`stepDot${i}`);
      if (sec) {
        sec.style.display = i === this.currentStep ? 'block' : 'none';
      }
      if (dot) {
        dot.classList.remove('active', 'completed');
        if (i < this.currentStep) dot.classList.add('completed');
        if (i === this.currentStep) dot.classList.add('active');
      }
    }
  }

  populateReviewSummary() {
    // Signature preview
    const sigImg = document.getElementById('reviewSignatureImg');
    if (sigImg) {
      sigImg.src = this.signatureManager.toDataURL();
    }

    // Selfie preview
    const selfieImg = document.getElementById('reviewSelfieImg');
    if (selfieImg) {
      selfieImg.src = this.cameraManager.getImageData();
    }

    // Blessing message
    const msgInput = document.getElementById('facultyBlessingInput');
    const reviewMsg = document.getElementById('reviewBlessingText');
    if (reviewMsg) {
      const msg = msgInput ? msgInput.value.trim() : '';
      reviewMsg.textContent = msg || '“With warmest blessings and best wishes for Sanskriti 2026!”';
    }

    // Public display consent
    const consentPublic = document.getElementById('publicConsentCheck');
    const reviewConsentBadge = document.getElementById('reviewConsentBadge');
    if (reviewConsentBadge) {
      if (consentPublic && consentPublic.checked) {
        reviewConsentBadge.textContent = 'Public Wall Display: Consented';
        reviewConsentBadge.className = 'badge-festive';
      } else {
        reviewConsentBadge.textContent = 'Public Wall Display: Private (Internal Only)';
        reviewConsentBadge.className = 'badge-pending';
      }
    }
  }

  attachNavigation() {
    // Next / Prev buttons
    document.querySelectorAll('[data-wizard-next]').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.goToStep(this.currentStep + 1);
      });
    });

    document.querySelectorAll('[data-wizard-prev]').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.goToStep(this.currentStep - 1);
      });
    });

    // Final Submit Button
    const submitBtn = document.getElementById('btnSubmitApproval');
    if (submitBtn) {
      submitBtn.addEventListener('click', () => this.submitApproval());
    }
  }

  async submitApproval() {
    const signatureData = this.signatureManager.toDataURL();
    const selfieData = this.cameraManager.getImageData();
    const captureMethod = this.cameraManager.getMethod();
    const messageInput = document.getElementById('facultyBlessingInput');
    const messageText = messageInput ? messageInput.value.trim() : '';
    const publicConsent = document.getElementById('publicConsentCheck') ? document.getElementById('publicConsentCheck').checked : true;

    if (!signatureData || this.signatureManager.isEmpty()) {
      Swal.fire({
        icon: 'error',
        title: 'Missing Signature',
        text: 'Please go back and provide your signature.',
        background: '#3A1019',
        color: '#FFF8EB',
        confirmButtonColor: '#C6A15B',
      });
      return;
    }

    if (!selfieData) {
      Swal.fire({
        icon: 'error',
        title: 'Missing Selfie',
        text: 'Please go back and capture your faculty selfie.',
        background: '#3A1019',
        color: '#FFF8EB',
        confirmButtonColor: '#C6A15B',
      });
      return;
    }

    // Show loading
    Swal.fire({
      title: 'Recording Blessings...',
      text: 'Saving digital signature, photo & blessing into college archives...',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
      background: '#3A1019',
      color: '#FFF8EB',
    });

    try {
      const response = await fetch(this.submitUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.csrfToken,
        },
        body: JSON.stringify({
          faculty_id: this.facultyId,
          event_id: this.eventId,
          department_id: this.departmentId,
          signature_base64: signatureData,
          selfie_base64: selfieData,
          capture_method: captureMethod,
          message_text: messageText,
          is_public: publicConsent,
        }),
      });

      const res = await response.json();
      if (res.success) {
        // Play festive audio fanfare
        if (typeof FestiveAudio !== 'undefined') {
          FestiveAudio.playApprovalFanfare();
        }

        // Redirect to animated approval celebration page
        window.location.href = res.redirect_url || this.successRedirectUrl;
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Submission Error',
          text: res.message || 'Unable to save approval. Please try again.',
          background: '#3A1019',
          color: '#FFF8EB',
          confirmButtonColor: '#C6A15B',
        });
      }
    } catch (err) {
      console.error(err);
      Swal.fire({
        icon: 'error',
        title: 'Connection Error',
        text: 'A network error occurred. Please check connectivity and try again.',
        background: '#3A1019',
        color: '#FFF8EB',
        confirmButtonColor: '#C6A15B',
      });
    }
  }
}

window.FacultyApprovalWizard = FacultyApprovalWizard;

