/**
 * Chart.js Integration for Expense Split and Settlement System
 * Fetches dynamic data from /api/chart-data and adapts to Dark/Light themes.
 */

(function () {
  let monthlyChartInstance = null;
  let categoryChartInstance = null;
  let groupChartInstance = null;
  let budgetChartInstance = null;

  function getChartThemeColors(isDark) {
    return {
      textColor: isDark ? '#f1f2f6' : '#2d3436',
      gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
      cardBg: isDark ? '#181a27' : '#ffffff',
      purple: '#6c5ce7',
      purpleLight: 'rgba(108, 92, 231, 0.25)',
      secondary: '#a29bfe',
      teal: '#00cec9',
      green: '#00b894',
      orange: '#e17055',
      yellow: '#fdcb6e',
      pink: '#e84393',
      blue: '#0984e3'
    };
  }

  async function loadAndRenderCharts() {
    const monthlyCanvas = document.getElementById('monthlyChart');
    const categoryCanvas = document.getElementById('categoryChart');
    const groupCanvas = document.getElementById('groupChart');
    const budgetCanvas = document.getElementById('budgetChart');

    // Only proceed if chart canvases are present on this page (dashboard)
    if (!monthlyCanvas && !categoryCanvas && !groupCanvas && !budgetCanvas) {
      return;
    }

    try {
      const response = await fetch('/api/chart-data');
      if (!response.ok) {
        console.warn('Could not fetch chart data.');
        return;
      }
      const data = await response.json();
      renderAllCharts(data);
    } catch (err) {
      console.error('Error fetching chart data:', err);
    }
  }

  function renderAllCharts(data) {
    const isDark = document.body.classList.contains('dark-theme');
    const colors = getChartThemeColors(isDark);

    // 1. Monthly Spending Trend
    const monthlyCanvas = document.getElementById('monthlyChart');
    if (monthlyCanvas) {
      if (monthlyChartInstance) monthlyChartInstance.destroy();

      const hasMonthlyData = data.monthly && data.monthly.data && data.monthly.data.length > 0;
      if (!hasMonthlyData) {
        showEmptyChart(monthlyCanvas, 'No monthly spending data yet');
      } else {
        monthlyChartInstance = new Chart(monthlyCanvas.getContext('2d'), {
          type: 'line',
          data: {
            labels: data.monthly.labels,
            datasets: [{
              label: 'Monthly Spending (₹)',
              data: data.monthly.data,
              borderColor: colors.purple,
              backgroundColor: colors.purpleLight,
              fill: true,
              tension: 0.35,
              borderWidth: 2.5,
              pointBackgroundColor: colors.purple,
              pointRadius: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              x: {
                ticks: { color: colors.textColor },
                grid: { color: colors.gridColor }
              },
              y: {
                ticks: {
                  color: colors.textColor,
                  callback: (value) => '₹' + value.toLocaleString()
                },
                grid: { color: colors.gridColor }
              }
            }
          }
        });
      }
    }

    // 2. Expense Category Breakdown (Doughnut)
    const categoryCanvas = document.getElementById('categoryChart');
    if (categoryCanvas) {
      if (categoryChartInstance) categoryChartInstance.destroy();

      const hasCategoryData = data.categories && data.categories.data && data.categories.data.length > 0;
      if (!hasCategoryData) {
        showEmptyChart(categoryCanvas, 'No category data yet');
      } else {
        const palette = [
          '#6c5ce7', '#00b894', '#0984e3', '#fdcb6e',
          '#e17055', '#e84393', '#00cec9', '#636e72', '#a29bfe'
        ];

        categoryChartInstance = new Chart(categoryCanvas.getContext('2d'), {
          type: 'doughnut',
          data: {
            labels: data.categories.labels,
            datasets: [{
              data: data.categories.data,
              backgroundColor: palette.slice(0, data.categories.labels.length),
              borderWidth: 2,
              borderColor: colors.cardBg
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: { color: colors.textColor, boxWidth: 14, font: { size: 11 } }
              },
              tooltip: {
                callbacks: {
                  label: function (context) {
                    const val = context.raw || 0;
                    return ` ${context.label}: ₹${val.toLocaleString()}`;
                  }
                }
              }
            }
          }
        });
      }
    }

    // 3. Group-wise Expense Comparison
    const groupCanvas = document.getElementById('groupChart');
    if (groupCanvas) {
      if (groupChartInstance) groupChartInstance.destroy();

      const hasGroupData = data.group_comparison && data.group_comparison.data && data.group_comparison.data.length > 0;
      if (!hasGroupData) {
        showEmptyChart(groupCanvas, 'No group expense data yet');
      } else {
        groupChartInstance = new Chart(groupCanvas.getContext('2d'), {
          type: 'bar',
          data: {
            labels: data.group_comparison.labels,
            datasets: [{
              label: 'Total Expenses (₹)',
              data: data.group_comparison.data,
              backgroundColor: colors.purple,
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              x: {
                ticks: { color: colors.textColor },
                grid: { display: false }
              },
              y: {
                ticks: {
                  color: colors.textColor,
                  callback: (value) => '₹' + value.toLocaleString()
                },
                grid: { color: colors.gridColor }
              }
            }
          }
        });
      }
    }

    // 4. Budget Usage Chart (Group Spending vs Budget)
    const budgetCanvas = document.getElementById('budgetChart');
    if (budgetCanvas) {
      if (budgetChartInstance) budgetChartInstance.destroy();

      const hasBudgetData = data.budget_comparison && data.budget_comparison.labels && data.budget_comparison.labels.length > 0;
      if (!hasBudgetData) {
        showEmptyChart(budgetCanvas, 'No group budget data yet');
      } else {
        budgetChartInstance = new Chart(budgetCanvas.getContext('2d'), {
          type: 'bar',
          data: {
            labels: data.budget_comparison.labels,
            datasets: [
              {
                label: 'Spent Amount (₹)',
                data: data.budget_comparison.spent,
                backgroundColor: '#e17055',
                borderRadius: 6
              },
              {
                label: 'Monthly Budget (₹)',
                data: data.budget_comparison.budget,
                backgroundColor: '#00b894',
                borderRadius: 6
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { color: colors.textColor }
              }
            },
            scales: {
              x: {
                ticks: { color: colors.textColor },
                grid: { display: false }
              },
              y: {
                ticks: {
                  color: colors.textColor,
                  callback: (value) => '₹' + value.toLocaleString()
                },
                grid: { color: colors.gridColor }
              }
            }
          }
        });
      }
    }
  }

  function showEmptyChart(canvas, message) {
    const parent = canvas.parentElement;
    let emptyNotice = parent.querySelector('.chart-empty-state');
    if (!emptyNotice) {
      emptyNotice = document.createElement('div');
      emptyNotice.className = 'chart-empty-state';
      emptyNotice.style.textAlign = 'center';
      emptyNotice.style.padding = '4rem 1rem';
      emptyNotice.style.color = 'var(--text-secondary)';
      emptyNotice.innerHTML = `<i class="fa-solid fa-chart-pie" style="font-size: 2.5rem; margin-bottom: 0.5rem; opacity: 0.5;"></i><p>${message}</p>`;
      canvas.style.display = 'none';
      parent.appendChild(emptyNotice);
    }
  }

  // Handle dark/light theme switch
  window.addEventListener('themeChanged', function () {
    loadAndRenderCharts();
  });

  document.addEventListener('DOMContentLoaded', function () {
    loadAndRenderCharts();
  });

  window.ChartsManager = {
    reload: loadAndRenderCharts
  };
})();
