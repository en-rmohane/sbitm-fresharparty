/**
 * SANSKRITI 2026 - Cinematic Envelope Opening & GSAP Animations
 */

function setupEnvelopeAnimation() {
  const envelope = document.getElementById('invitationEnvelope');
  const openBtn = document.getElementById('openInvitationBtn');
  const waxSeal = document.getElementById('envelopeWaxSeal');
  const letter = document.getElementById('envelopeLetter');
  const revealedDetails = document.getElementById('revealedDetails');

  if (!envelope || !openBtn) return;

  let isOpen = false;

  function openEnvelope() {
    if (isOpen) return;
    isOpen = true;

    // Sacred chime sound
    if (typeof FestiveAudio !== 'undefined') {
      FestiveAudio.playBell();
    }

    // GSAP Sequence
    if (typeof gsap !== 'undefined') {
      const tl = gsap.timeline();

      // Step 1: Wax seal lifts & shines
      tl.to(waxSeal, {
        scale: 1.25,
        rotation: 15,
        opacity: 0.9,
        duration: 0.4,
        ease: 'power2.out',
      })
      .to(waxSeal, {
        scale: 0,
        opacity: 0,
        duration: 0.35,
        ease: 'power2.in',
      });

      // Step 2: Flap opens
      tl.to('.envelope-flap', {
        rotateX: 180,
        duration: 0.8,
        ease: 'power3.inOut',
        onStart: () => envelope.classList.add('open')
      }, '-=0.1');

      // Step 3: Letter card rises
      tl.to(letter, {
        y: -120,
        zIndex: 15,
        duration: 0.9,
        ease: 'back.out(1.2)'
      }, '-=0.3');

      // Step 4: Flower petals & golden confetti burst
      tl.add(() => {
        triggerFestiveConfetti();
      });

      // Step 5: Smooth reveal of the full invitation details section below
      if (revealedDetails) {
        tl.to(revealedDetails, {
          display: 'block',
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: 'power2.out',
          onComplete: () => {
            revealedDetails.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, '-=0.2');
      }

      // Hide the initial Open button smoothly
      gsap.to(openBtn, {
        opacity: 0,
        y: 10,
        duration: 0.3,
        pointerEvents: 'none'
      });

    } else {
      // Fallback if GSAP is still loading
      envelope.classList.add('open');
      if (revealedDetails) {
        revealedDetails.style.display = 'block';
        revealedDetails.style.opacity = '1';
        revealedDetails.scrollIntoView({ behavior: 'smooth' });
      }
      openBtn.style.display = 'none';
      triggerFestiveConfetti();
    }
  }

  openBtn.addEventListener('click', openEnvelope);
  if (waxSeal) waxSeal.addEventListener('click', openEnvelope);
  envelope.addEventListener('click', (e) => {
    if (!isOpen && !e.target.closest('#revealedDetails')) {
      openEnvelope();
    }
  });
}

function triggerFestiveConfetti() {
  if (typeof confetti === 'function') {
    // Golden & Maroon Indian festive petals
    const colors = ['#C6A15B', '#FFEBB8', '#641E28', '#D97732', '#FFF8EB'];
    
    // Left burst
    confetti({
      particleCount: 45,
      angle: 60,
      spread: 55,
      origin: { x: 0.2, y: 0.65 },
      colors: colors,
    });

    // Right burst
    confetti({
      particleCount: 45,
      angle: 120,
      spread: 55,
      origin: { x: 0.8, y: 0.65 },
      colors: colors,
    });

    // Center lotus shower
    setTimeout(() => {
      confetti({
        particleCount: 50,
        spread: 90,
        origin: { y: 0.4 },
        colors: colors,
        shapes: ['circle']
      });
    }, 250);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  setupEnvelopeAnimation();
});

