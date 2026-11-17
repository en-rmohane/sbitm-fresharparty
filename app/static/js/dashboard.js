/**
 * SANSKRITI 2026 - Live Approval Dashboard & Visualizations
 * Chart.js Integration & Real-Time Stats Updates
 */

class SanskritiDashboard {
  constructor(apiEndpoint) {
    this.apiEndpoint = apiEndpoint || '/approvals/api/stats';
    this.chart = null;
    this.pieChart = null;
    this.init();
  }

  async init() {
    await this.fetchAndRender();
    // Auto-refresh stats every 15 seconds
    setInterval(() => this.fetchAndRender(), 15000);
  }

  async fetchAndRender() {
    try {
      const res = await fetch(this.apiEndpoint);
      if (!res.ok) return;
      const data = await res.json();

      this.updateCounters(data);
      this.renderDepartmentChart(data.departments);
      this.renderRatioChart(data);
    } catch (e) {
      console.warn('Dashboard stats fetch failed:', e);
    }
  }

  updateCounters(data) {
    const el = (id) => document.getElementById(id);
    if (el('statTotalDepts')) el('statTotalDepts').textContent = data.total_departments;
    if (el('statTotalFaculty')) el('statTotalFaculty').textContent = data.total_faculty;
    if (el('statApprovedCount')) el('statApprovedCount').textContent = data.approved_count;
    if (el('statPendingCount')) el('statPendingCount').textContent = data.pending_count;
    if (el('statProgressPercent')) {
      const pct = data.completion_percentage + '%';
      el('statProgressPercent').textContent = pct;
      const bar = el('statProgressBar');
      if (bar) bar.style.width = pct;
    }
  }

  renderDepartmentChart(departments) {
    const ctx = document.getElementById('deptApprovalChart');
    if (!ctx) return;

    const labels = departments.map((d) => d.code);
    const approvedData = departments.map((d) => d.approved);
    const totalData = departments.map((d) => d.total);

    if (this.chart) {
      this.chart.data.labels = labels;
      this.chart.data.datasets[0].data = approvedData;
      this.chart.data.datasets[1].data = totalData;
      this.chart.update();
      return;
    }

    if (typeof Chart === 'undefined') return;

    this.chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Approved',
            data: approvedData,
            backgroundColor: '#C6A15B',
            borderColor: '#FFEBB8',
            borderWidth: 1,
            borderRadius: 6,
          },
          {
            label: 'Total Required',
            data: totalData,
            backgroundColor: 'rgba(100, 30, 40, 0.45)',
            borderColor: 'rgba(198, 161, 91, 0.3)',
            borderWidth: 1,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#FFF8EB',
              font: { family: "'Poppins', sans-serif" },
            },
          },
        },
        scales: {
          x: {
            ticks: { color: '#F5EBD9' },
            grid: { color: 'rgba(198, 161, 91, 0.1)' },
          },
          y: {
            beginAtZero: true,
            ticks: { color: '#F5EBD9', precision: 0 },
            grid: { color: 'rgba(198, 161, 91, 0.15)' },
          },
        },
      },
    });
  }

  renderRatioChart(data) {
    const ctx = document.getElementById('approvalRatioChart');
    if (!ctx) return;

    if (this.pieChart) {
      this.pieChart.data.datasets[0].data = [data.approved_count, data.pending_count];
      this.pieChart.update();
      return;
    }

    if (typeof Chart === 'undefined') return;

    this.pieChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Approved', 'Pending'],
        datasets: [
          {
            data: [data.approved_count, data.pending_count],
            backgroundColor: ['#C6A15B', '#4A1520'],
            borderColor: ['#FFEBB8', '#3A1019'],
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#FFF8EB',
              font: { family: "'Poppins', sans-serif" },
            },
          },
        },
        cutout: '70%',
      },
    });
  }
}

window.SanskritiDashboard = SanskritiDashboard;

