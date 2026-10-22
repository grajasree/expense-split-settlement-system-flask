/**
 * Chart.js Integration for Expense Split and Settlement System
 * Theme: Midnight Indigo (#4338CA) & Ice Blue (#BAE6FD)
 * Fetches dynamic data from /api/chart-data with filter support (Group, Date Range).
 * Calculates Total Spending and Average Monthly Spending dynamically.
 * Adapts to Dark/Light themes seamlessly.
 */

(function () {
  let monthlyChartInstance = null;
  let categoryChartInstance = null;
  let groupChartInstance = null;
  let budgetChartInstance = null;

  function getChartThemeColors(isDark) {
    return {
      textColor: isDark ? '#F8FAFC' : '#1E1B4B',
      gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(67, 56, 202, 0.06)',
      cardBg: isDark ? '#151A28' : '#FFFFFF',
      purple: '#4338CA',
      purpleHover: '#3730A3',
      purpleLight: 'rgba(67, 56, 202, 0.18)',
      secondary: '#BAE6FD',
      iceBlue: '#BAE6FD',
      iceBlueDark: '#38BDF8',
      iceBlueHover: '#7DD3FC',
      teal: '#0284C7',
      green: '#059669',
      orange: '#EA580C',
      yellow: '#D97706',
      pink: '#6366F1',
      blue: '#38BDF8'
    };
  }

  async function loadAndRenderCharts(filters = {}) {
    const monthlyCanvas = document.getElementById('monthlyChart');
    const categoryCanvas = document.getElementById('categoryChart');
    const groupCanvas = document.getElementById('groupChart');
    const budgetCanvas = document.getElementById('budgetChart');

    // Only proceed if chart canvases are present on this page
    if (!monthlyCanvas && !categoryCanvas && !groupCanvas && !budgetCanvas) {
      return;
    }

    const groupEl = document.getElementById('analyticsGroupFilter');
    const startEl = document.getElementById('analyticsStartDate');
    const endEl = document.getElementById('analyticsEndDate');

    const groupVal = filters.groupId !== undefined ? filters.groupId : (groupEl ? groupEl.value : 'all');
    const startVal = filters.startDate !== undefined ? filters.startDate : (startEl ? startEl.value : '');
    const endVal = filters.endDate !== undefined ? filters.endDate : (endEl ? endEl.value : '');

    const params = new URLSearchParams();
    if (groupVal && groupVal !== 'all') params.append('group_id', groupVal);
    if (startVal) params.append('start_date', startVal);
    if (endVal) params.append('end_date', endVal);

    try {
      const url = '/api/chart-data' + (params.toString() ? '?' + params.toString() : '');
      const response = await fetch(url);
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

    // Update Analytics Section Metric Cards
    const totalEl = document.getElementById('analyticsTotalSpending');
    if (totalEl) {
      totalEl.textContent = '₹' + Number(data.total_spending || 0).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    }

    const avgEl = document.getElementById('analyticsAvgSpending');
    if (avgEl) {
      avgEl.textContent = '₹' + Number(data.avg_monthly_spending || 0).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    }

    const monthsEl = document.getElementById('analyticsActiveMonths');
    if (monthsEl) {
      monthsEl.textContent = data.active_months_count || 0;
    }

    // 1. Monthly Expenses Bar Chart (Midnight Indigo Theme)
    const monthlyCanvas = document.getElementById('monthlyChart');
    if (monthlyCanvas) {
      if (monthlyChartInstance) monthlyChartInstance.destroy();

      const hasMonthlyData = data.monthly && data.monthly.data && data.monthly.data.length > 0;
      if (!hasMonthlyData) {
        showEmptyChart(monthlyCanvas, 'No monthly spending records found for selected filter');
      } else {
        removeEmptyNotice(monthlyCanvas);
        monthlyChartInstance = new Chart(monthlyCanvas.getContext('2d'), {
          type: 'bar',
          data: {
            labels: data.monthly.labels,
            datasets: [{
              label: 'Monthly Expenses (₹)',
              data: data.monthly.data,
              backgroundColor: colors.purple,
              hoverBackgroundColor: colors.purpleHover,
              borderRadius: 8,
              borderWidth: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: (ctx) => ` Spent: ₹${Number(ctx.raw || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                }
              }
            },
            scales: {
              x: {
                ticks: { color: colors.textColor, font: { weight: '600' } },
                grid: { display: false }
              },
              y: {
                ticks: {
                  color: colors.textColor,
                  callback: (value) => '₹' + Number(value).toLocaleString('en-IN')
                },
                grid: { color: colors.gridColor }
              }
            }
          }
        });
      }
    }

    // 2. Expense Category Breakdown Pie Chart (Midnight Indigo & Ice Blue Palette)
    const categoryCanvas = document.getElementById('categoryChart');
    if (categoryCanvas) {
      if (categoryChartInstance) categoryChartInstance.destroy();

      const hasCategoryData = data.categories && data.categories.data && data.categories.data.length > 0;
      if (!hasCategoryData) {
        showEmptyChart(categoryCanvas, 'No category expense records found for selected filter');
      } else {
        removeEmptyNotice(categoryCanvas);
        const palette = [
          '#4338CA', '#38BDF8', '#6366F1', '#BAE6FD',
          '#0284C7', '#818CF8', '#0EA5E9', '#A5B4FC', '#0369A1'
        ];

        categoryChartInstance = new Chart(categoryCanvas.getContext('2d'), {
          type: 'pie',
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
                labels: { color: colors.textColor, boxWidth: 14, font: { size: 11, weight: '700' } }
              },
              tooltip: {
                callbacks: {
                  label: function (context) {
                    const val = Number(context.raw || 0);
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const pct = total > 0 ? ((val / total) * 100).toFixed(1) : '0.0';
                    return ` ${context.label}: ₹${val.toLocaleString('en-IN', { minimumFractionDigits: 2 })} (${pct}%)`;
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
        showEmptyChart(groupCanvas, 'No group expense records found');
      } else {
        removeEmptyNotice(groupCanvas);
        groupChartInstance = new Chart(groupCanvas.getContext('2d'), {
          type: 'bar',
          data: {
            labels: data.group_comparison.labels,
            datasets: [{
              label: 'Total Expenses (₹)',
              data: data.group_comparison.data,
              backgroundColor: colors.purple,
              hoverBackgroundColor: colors.purpleHover,
              borderRadius: 8
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
                ticks: { color: colors.textColor, font: { weight: '600' } },
                grid: { display: false }
              },
              y: {
                ticks: {
                  color: colors.textColor,
                  callback: (value) => '₹' + Number(value).toLocaleString('en-IN')
                },
                grid: { color: colors.gridColor }
              }
            }
          }
        });
      }
    }

    // 4. Budget Usage Chart (Group Spending vs Budget) - Midnight Indigo & Ice Blue Accents
    const budgetCanvas = document.getElementById('budgetChart');
    if (budgetCanvas) {
      if (budgetChartInstance) budgetChartInstance.destroy();

      const hasBudgetData = data.budget_comparison && data.budget_comparison.labels && data.budget_comparison.labels.length > 0;
      if (!hasBudgetData) {
        showEmptyChart(budgetCanvas, 'No group budget records found');
      } else {
        removeEmptyNotice(budgetCanvas);
        budgetChartInstance = new Chart(budgetCanvas.getContext('2d'), {
          type: 'bar',
          data: {
            labels: data.budget_comparison.labels,
            datasets: [
              {
                label: 'Spent Amount (₹)',
                data: data.budget_comparison.spent,
                backgroundColor: colors.purple,
                hoverBackgroundColor: colors.purpleHover,
                borderRadius: 8
              },
              {
                label: 'Monthly Budget (₹)',
                data: data.budget_comparison.budget,
                backgroundColor: colors.secondary,
                borderColor: colors.iceBlueDark,
                borderWidth: 1.5,
                borderRadius: 8
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { color: colors.textColor, font: { weight: '600' } }
              }
            },
            scales: {
              x: {
                ticks: { color: colors.textColor, font: { weight: '600' } },
                grid: { display: false }
              },
              y: {
                ticks: {
                  color: colors.textColor,
                  callback: (value) => '₹' + Number(value).toLocaleString('en-IN')
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
      emptyNotice.innerHTML = `<i class="fa-solid fa-chart-pie" style="font-size: 2.5rem; margin-bottom: 0.5rem; opacity: 0.5; color: var(--primary);"></i><p>${message}</p>`;
      canvas.style.display = 'none';
      parent.appendChild(emptyNotice);
    }
  }

  function removeEmptyNotice(canvas) {
    const parent = canvas.parentElement;
    const emptyNotice = parent.querySelector('.chart-empty-state');
    if (emptyNotice) {
      emptyNotice.remove();
    }
    canvas.style.display = 'block';
  }

  // Handle dark/light theme switch
  window.addEventListener('themeChanged', function () {
    loadAndRenderCharts();
  });

  document.addEventListener('DOMContentLoaded', function () {
    loadAndRenderCharts();

    const groupFilter = document.getElementById('analyticsGroupFilter');
    const startDateInput = document.getElementById('analyticsStartDate');
    const endDateInput = document.getElementById('analyticsEndDate');
    const btnApply = document.getElementById('btnApplyAnalyticsFilter');
    const btnReset = document.getElementById('btnResetAnalyticsFilter');

    if (btnApply) {
      btnApply.addEventListener('click', function () {
        loadAndRenderCharts();
      });
    }

    if (groupFilter) {
      groupFilter.addEventListener('change', function () {
        loadAndRenderCharts();
      });
    }

    if (btnReset) {
      btnReset.addEventListener('click', function () {
        if (groupFilter) groupFilter.value = 'all';
        if (startDateInput) startDateInput.value = '';
        if (endDateInput) endDateInput.value = '';
        loadAndRenderCharts({ groupId: 'all', startDate: '', endDate: '' });
      });
    }
  });

  window.ChartsManager = {
    reload: loadAndRenderCharts
  };
})();
