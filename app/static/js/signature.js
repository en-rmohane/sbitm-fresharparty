/**
 * SANSKRITI 2026 - Digital E-Signature Canvas Pad
 * Mobile Touch, Stylus, and Mouse Support with Non-Blank Validation
 */

class SignaturePadManager {
  constructor(canvasId, clearBtnId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.clearBtn = document.getElementById(clearBtnId);
    this.isDrawing = false;
    this.points = [];
    this.strokeCount = 0;

    this.initCanvas();
    this.attachEvents();
  }

  initCanvas() {
    // Handle High DPI displays
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);

    // Default stroke style: Royal Deep Maroon / Ink Black with smooth caps
    this.ctx.strokeStyle = '#3A1019';
    this.ctx.lineWidth = 2.6;
    this.ctx.lineCap = 'round';
    this.ctx.lineJoin = 'round';

    this.clear();
  }

  attachEvents() {
    // Pointer / Mouse / Touch events
    const getPos = (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      return {
        x: clientX - rect.left,
        y: clientY - rect.top,
      };
    };

    const startDraw = (e) => {
      e.preventDefault();
      this.isDrawing = true;
      const pos = getPos(e);
      this.points = [pos];
      this.ctx.beginPath();
      this.ctx.moveTo(pos.x, pos.y);
      this.strokeCount++;
    };

    const draw = (e) => {
      if (!this.isDrawing) return;
      e.preventDefault();
      const pos = getPos(e);
      this.points.push(pos);

      if (this.points.length > 2) {
        const lastTwo = this.points.slice(-2);
        const xc = (lastTwo[0].x + lastTwo[1].x) / 2;
        const yc = (lastTwo[0].y + lastTwo[1].y) / 2;
        this.ctx.quadraticCurveTo(lastTwo[0].x, lastTwo[0].y, xc, yc);
        this.ctx.stroke();
      } else {
        this.ctx.lineTo(pos.x, pos.y);
        this.ctx.stroke();
      }
    };

    const endDraw = (e) => {
      if (!this.isDrawing) return;
      this.isDrawing = false;
      this.ctx.closePath();
    };

    // Mouse listeners
    this.canvas.addEventListener('mousedown', startDraw);
    this.canvas.addEventListener('mousemove', draw);
    window.addEventListener('mouseup', endDraw);

    // Touch listeners
    this.canvas.addEventListener('touchstart', startDraw, { passive: false });
    this.canvas.addEventListener('touchmove', draw, { passive: false });
    window.addEventListener('touchend', endDraw);
    window.addEventListener('touchcancel', endDraw);

    // Clear Button
    if (this.clearBtn) {
      this.clearBtn.addEventListener('click', () => this.clear());
    }

    // Window resize handler
    window.addEventListener('resize', () => {
      // Preserve current signature on resize if exists
      const dataUrl = this.isEmpty() ? null : this.toDataURL();
      const rect = this.canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      this.canvas.width = rect.width * dpr;
      this.canvas.height = rect.height * dpr;
      this.ctx.scale(dpr, dpr);
      this.ctx.strokeStyle = '#3A1019';
      this.ctx.lineWidth = 2.6;
      this.ctx.lineCap = 'round';
      this.ctx.lineJoin = 'round';

      if (dataUrl) {
        const img = new Image();
        img.onload = () => {
          this.ctx.drawImage(img, 0, 0, rect.width, rect.height);
        };
        img.src = dataUrl;
      }
    });
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.strokeCount = 0;
    this.points = [];
  }

  isEmpty() {
    return this.strokeCount === 0 || this.points.length < 5;
  }

  toDataURL() {
    return this.canvas.toDataURL('image/png');
  }
}

window.SignaturePadManager = SignaturePadManager;

