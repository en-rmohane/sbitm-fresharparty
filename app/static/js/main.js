/**
 * SANSKRITI 2026 - Main JavaScript
 * Particle Canvas, Audio Chime, Countdown, Utility Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // Initialize Golden Particle Background
  initGoldenParticles();

  // Initialize Countdown Timer if element present
  initCountdownTimer();

  // Universal Modal Dismiss Helper (Handles all modal close & cross buttons reliably)
  document.addEventListener('click', (e) => {
    const dismissBtn = e.target.closest('[data-bs-dismiss="modal"]');
    if (dismissBtn) {
      const modalEl = dismissBtn.closest('.modal');
      if (modalEl && typeof bootstrap !== 'undefined') {
        const modalInstance = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
        if (modalInstance) {
          modalInstance.hide();
        }
      }
    }
  });
});

/* ==========================================================================
   Festive Golden Particles & Floating Sparkles Canvas
   ========================================================================== */
function initGoldenParticles() {
  const canvas = document.getElementById('particlesCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = [];
  const particleCount = Math.min(window.innerWidth < 768 ? 35 : 70, 80);
  const colors = ['#FFEBB8', '#DFBA73', '#C6A15B', '#D97732', '#FFF8EB'];

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      radius: Math.random() * 2.5 + 0.8,
      color: colors[Math.floor(Math.random() * colors.length)],
      vx: (Math.random() - 0.5) * 0.4,
      vy: -Math.random() * 0.6 - 0.2, // gently drifting upwards like sacred embers
      alpha: Math.random() * 0.7 + 0.2,
      pulse: Math.random() * 0.02 + 0.01,
      angle: Math.random() * Math.PI * 2,
    });
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    for (let p of particles) {
      p.x += p.vx + Math.sin(p.angle) * 0.2;
      p.y += p.vy;
      p.angle += 0.02;

      // Glow & opacity pulse
      p.alpha += Math.sin(p.angle * 2) * 0.005;
      if (p.alpha < 0.1) p.alpha = 0.1;
      if (p.alpha > 0.9) p.alpha = 0.9;

      // Wrap around screen
      if (p.y < -10) {
        p.y = height + 10;
        p.x = Math.random() * width;
      }
      if (p.x < -10) p.x = width + 10;
      if (p.x > width + 10) p.x = -10;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.shadowBlur = p.radius * 4;
      ctx.shadowColor = '#C6A15B';
      ctx.fill();
    }

    ctx.globalAlpha = 1.0;
    requestAnimationFrame(render);
  }

  render();
}

/* ==========================================================================
   Countdown Timer
   ========================================================================== */
function initCountdownTimer() {
  const container = document.getElementById('eventCountdown');
  if (!container) return;

  const targetDateStr = container.getAttribute('data-event-date') || 'November 19, 2026 10:00:00';
  const targetTime = new Date(targetDateStr).getTime();

  function update() {
    const now = new Date().getTime();
    const distance = targetTime - now;

    if (distance < 0) {
      document.getElementById('cdDays') && (document.getElementById('cdDays').textContent = '00');
      document.getElementById('cdHours') && (document.getElementById('cdHours').textContent = '00');
      document.getElementById('cdMinutes') && (document.getElementById('cdMinutes').textContent = '00');
      document.getElementById('cdSeconds') && (document.getElementById('cdSeconds').textContent = '00');
      return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    const pad = (n) => (n < 10 ? '0' + n : n);

    if (document.getElementById('cdDays')) document.getElementById('cdDays').textContent = pad(days);
    if (document.getElementById('cdHours')) document.getElementById('cdHours').textContent = pad(hours);
    if (document.getElementById('cdMinutes')) document.getElementById('cdMinutes').textContent = pad(minutes);
    if (document.getElementById('cdSeconds')) document.getElementById('cdSeconds').textContent = pad(seconds);
  }

  update();
  setInterval(update, 1000);
}

/* ==========================================================================
   Sacred Temple Chime Synthesizer (Web Audio API)
   ========================================================================== */
const FestiveAudio = {
  playBell() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();

      const freqs = [528, 1056, 1584]; // Harmonious sacred tuning
      freqs.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, ctx.currentTime);

        gain.gain.setValueAtTime(0.2 / (idx + 1), ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 3.2);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 3.3);
      });
    } catch (e) {
      console.warn('Audio synthesis not permitted without user gesture.');
    }
  },

  playApprovalFanfare() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();

      const notes = [440, 554.37, 659.25, 880]; // A Major festive chord
      notes.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.12);

        gain.gain.setValueAtTime(0.18, ctx.currentTime + i * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 2.5);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(ctx.currentTime + i * 0.12);
        osc.stop(ctx.currentTime + i * 0.12 + 2.6);
      });
    } catch (e) {
      // safe fallback
    }
  },

  // Freshers Party Celebration Dhol Beats Rhythmic Synthesizer
  partyAudioCtx: null,
  partyLoopTimer: null,
  isPartyPlaying: false,

  togglePartyBeats(btnElement) {
    if (this.isPartyPlaying) {
      this.stopPartyBeats(btnElement);
    } else {
      this.startPartyBeats(btnElement);
    }
  },

  startPartyBeats(btnElement) {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      this.partyAudioCtx = new AudioContext();
      this.isPartyPlaying = true;

      if (btnElement) {
        btnElement.innerHTML = '<i data-lucide="volume-2" style="width: 16px;"></i> Party Beats ON 🎵';
        btnElement.classList.add('party-btn-pulse');
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }

      // 8-beat energetic rhythmic loop (Bhangra / Bollywood party groove)
      let beatStep = 0;
      const playStep = () => {
        if (!this.isPartyPlaying || !this.partyAudioCtx) return;
        const now = this.partyAudioCtx.currentTime;

        // Bass drum thump (Dhama) on beats 0, 2, 4, 6
        if (beatStep % 2 === 0) {
          const osc = this.partyAudioCtx.createOscillator();
          const gain = this.partyAudioCtx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(110, now);
          osc.frequency.exponentialRampToValueAtTime(45, now + 0.15);
          gain.gain.setValueAtTime(0.35, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
          osc.connect(gain);
          gain.connect(this.partyAudioCtx.destination);
          osc.start(now);
          osc.stop(now + 0.22);
        }

        // Treble slap (Tilli sharp roll)
        if (beatStep % 2 === 1 || beatStep === 7) {
          const oscT = this.partyAudioCtx.createOscillator();
          const gainT = this.partyAudioCtx.createGain();
          oscT.type = 'triangle';
          oscT.frequency.setValueAtTime(320, now);
          oscT.frequency.exponentialRampToValueAtTime(180, now + 0.08);
          gainT.gain.setValueAtTime(0.2, now);
          gainT.gain.exponentialRampToValueAtTime(0.001, now + 0.09);
          oscT.connect(gainT);
          gainT.connect(this.partyAudioCtx.destination);
          oscT.start(now);
          oscT.stop(now + 0.1);
        }

        beatStep = (beatStep + 1) % 8;
      };

      this.partyLoopTimer = setInterval(playStep, 175); // ~170 BPM high energy tempo!

      // Trigger party confetti burst
      triggerPartyCelebration();

    } catch (e) {
      console.warn('Audio synthesis issue:', e);
    }
  },

  stopPartyBeats(btnElement) {
    this.isPartyPlaying = false;
    if (this.partyLoopTimer) {
      clearInterval(this.partyLoopTimer);
      this.partyLoopTimer = null;
    }
    if (this.partyAudioCtx) {
      try { this.partyAudioCtx.close(); } catch(e){}
      this.partyAudioCtx = null;
    }
    if (btnElement) {
      btnElement.innerHTML = '<i data-lucide="music" style="width: 16px;"></i> Play Party Beats';
      btnElement.classList.remove('party-btn-pulse');
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  }
};

/* ==========================================================================
   Full Screen Multi-Color Freshers Party Confetti Cannon
   ========================================================================== */
function triggerPartyCelebration() {
  if (typeof confetti === 'function') {
    const partyColors = ['#FFD700', '#FF4081', '#FF6D00', '#00E676', '#00B0FF', '#FFF8EB', '#9C27B0'];

    // Big central burst
    confetti({
      particleCount: 80,
      spread: 120,
      origin: { y: 0.6 },
      colors: partyColors,
      shapes: ['circle', 'square']
    });

    // Left party cannon
    setTimeout(() => {
      confetti({
        particleCount: 50,
        angle: 60,
        spread: 80,
        origin: { x: 0, y: 0.7 },
        colors: partyColors
      });
    }, 180);

    // Right party cannon
    setTimeout(() => {
      confetti({
        particleCount: 50,
        angle: 120,
        spread: 80,
        origin: { x: 1, y: 0.7 },
        colors: partyColors
      });
    }, 360);
  }
}

/* ==========================================================================
   Share Invitation Helper
   ========================================================================== */
function shareInvitation(title, text, url) {
  if (navigator.share) {
    navigator.share({
      title: title || 'SANSKRITI 2026 - Freshers Invitation',
      text: text || 'You are cordially invited to Sanskriti 2026 Freshers Party!',
      url: url || window.location.href,
    }).catch((err) => console.log('Share canceled', err));
  } else {
    // Copy link to clipboard
    navigator.clipboard.writeText(url || window.location.href).then(() => {
      Swal.fire({
        title: 'Invitation Link Copied!',
        text: 'The invitation link has been copied to your clipboard.',
        icon: 'success',
        background: '#3A1019',
        color: '#FFF8EB',
        confirmButtonColor: '#C6A15B'
      });
    });
  }
}

