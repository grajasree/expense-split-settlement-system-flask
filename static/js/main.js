/**
 * Main Application Logic
 * - Password Show/Hide toggle
 * - Dynamic Expense Splits (Equal, Percentage, Custom)
 * - What-If Expense Simulator interactivity
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Password Visibility Toggle
  initPasswordToggles();

  // 2. Dynamic Expense Form Setup (if present)
  initExpenseForm();

  // 3. Simulator Form Setup (if present)
  initSimulator();
});

/* ==========================================================================
   1. Password Visibility Toggles
   ========================================================================== */
function initPasswordToggles() {
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';

      const icon = this.querySelector('i');
      if (icon) {
        icon.className = isPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
      }
    });
  });
}

/* ==========================================================================
   2. Dynamic Expense Split Logic
   ========================================================================== */
function initExpenseForm() {
  const groupSelect = document.getElementById('expense-group-select');
  const amountInput = document.getElementById('expense-amount-input');
  const splitTypeRadios = document.querySelectorAll('input[name="split_type"]');
  const participantsContainer = document.getElementById('participants-container');
  const payerSelect = document.getElementById('expense-payer-select');

  if (!groupSelect || !participantsContainer) return;

  async function loadGroupMembers(groupId) {
    if (!groupId) {
      participantsContainer.innerHTML = '<p class="text-muted">Please select a group first.</p>';
      if (payerSelect) payerSelect.innerHTML = '<option value="">Select Payer</option>';
      return;
    }

    try {
      const res = await fetch(`/expenses/api/group-members/${groupId}`);
      if (!res.ok) throw new Error('Failed to load group members');
      const data = await res.json();
      renderMemberInputs(data.members);
    } catch (err) {
      participantsContainer.innerHTML = '<p class="text-danger">Error loading members.</p>';
    }
  }

  function getSelectedSplitType() {
    const checked = document.querySelector('input[name="split_type"]:checked');
    return checked ? checked.value : 'EQUAL';
  }

  function renderMemberInputs(members) {
    if (!members || members.length === 0) {
      participantsContainer.innerHTML = '<p class="text-muted">No members found in this group.</p>';
      return;
    }

    // Populate Payer Select
    if (payerSelect) {
      const currentVal = payerSelect.value;
      payerSelect.innerHTML = '';
      members.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id;
        opt.textContent = `${m.name} (${m.email})`;
        if (String(m.id) === String(currentVal) || (!currentVal && String(m.id) === String(window.currentUserId))) {
          opt.selected = true;
        }
        payerSelect.appendChild(opt);
      });
    }

    // Render Participants List
    const splitType = getSelectedSplitType();
    let html = '<div class="participants-list" style="display: flex; flex-direction: column; gap: 0.75rem;">';

    members.forEach(m => {
      html += `
        <div class="participant-row card" style="padding: 0.75rem 1rem; margin-bottom: 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
          <label style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0; cursor: pointer;">
            <input type="checkbox" name="participants" value="${m.id}" checked class="participant-checkbox" data-user-id="${m.id}" style="width: 18px; height: 18px; accent-color: var(--primary);">
            <span><strong>${m.name}</strong> <small class="text-muted">(${m.email})</small></span>
          </label>
          <div class="split-input-wrapper" id="split-input-${m.id}" style="display: flex; align-items: center; gap: 0.5rem;">
            <!-- Dynamic split field based on type -->
          </div>
        </div>
      `;
    });

    html += '</div>';
    html += '<div id="split-summary-notice" style="margin-top: 0.75rem; font-weight: 600; font-size: 0.9rem;"></div>';
    participantsContainer.innerHTML = html;

    // Attach listeners to new checkboxes
    document.querySelectorAll('.participant-checkbox').forEach(cb => {
      cb.addEventListener('change', updateSplitFields);
    });

    updateSplitFields();
  }

  function updateSplitFields() {
    const splitType = getSelectedSplitType();
    const amount = parseFloat(amountInput ? amountInput.value : 0) || 0;
    const checkedBoxes = Array.from(document.querySelectorAll('.participant-checkbox:checked'));
    const count = checkedBoxes.length;
    const summaryNotice = document.getElementById('split-summary-notice');

    if (count === 0) {
      if (summaryNotice) {
        summaryNotice.innerHTML = '<span style="color: var(--danger);">⚠️ Please select at least one participant.</span>';
      }
      return;
    }

    const equalShare = count > 0 ? (amount / count).toFixed(2) : 0;

    document.querySelectorAll('.participant-checkbox').forEach(cb => {
      const uid = cb.getAttribute('data-user-id');
      const wrapper = document.getElementById(`split-input-${uid}`);
      if (!wrapper) return;

      if (!cb.checked) {
        wrapper.innerHTML = '<span class="badge badge-secondary">Excluded</span>';
        return;
      }

      if (splitType === 'EQUAL') {
        wrapper.innerHTML = `<span class="badge badge-purple">₹${equalShare}</span>`;
      } else if (splitType === 'PERCENTAGE') {
        const defaultPct = (100 / count).toFixed(2);
        wrapper.innerHTML = `
          <div style="display: flex; align-items: center; gap: 4px;">
            <input type="number" step="0.01" min="0" max="100" name="percentage_${uid}" value="${defaultPct}" class="form-control pct-input" style="width: 85px; padding: 0.35rem 0.5rem;" required>
            <span>%</span>
          </div>
        `;
      } else if (splitType === 'CUSTOM') {
        wrapper.innerHTML = `
          <div style="display: flex; align-items: center; gap: 4px;">
            <span>₹</span>
            <input type="number" step="0.01" min="0" name="custom_amount_${uid}" value="${equalShare}" class="form-control custom-amt-input" style="width: 100px; padding: 0.35rem 0.5rem;" required>
          </div>
        `;
      }
    });

    validateSplitTotals();

    // Attach listeners to input fields
    document.querySelectorAll('.pct-input, .custom-amt-input').forEach(inp => {
      inp.addEventListener('input', validateSplitTotals);
    });
  }

  function validateSplitTotals() {
    const splitType = getSelectedSplitType();
    const amount = parseFloat(amountInput ? amountInput.value : 0) || 0;
    const summaryNotice = document.getElementById('split-summary-notice');
    if (!summaryNotice) return;

    if (splitType === 'PERCENTAGE') {
      let sumPct = 0;
      document.querySelectorAll('.pct-input').forEach(inp => {
        sumPct += parseFloat(inp.value) || 0;
      });
      sumPct = Math.round(sumPct * 100) / 100;

      if (Math.abs(sumPct - 100) < 0.1) {
        summaryNotice.innerHTML = `<span style="color: var(--success);"><i class="fa-solid fa-circle-check"></i> Total: 100% (Valid)</span>`;
      } else {
        summaryNotice.innerHTML = `<span style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> Total: ${sumPct}% (Must equal exactly 100%)</span>`;
      }
    } else if (splitType === 'CUSTOM') {
      let sumAmt = 0;
      document.querySelectorAll('.custom-amt-input').forEach(inp => {
        sumAmt += parseFloat(inp.value) || 0;
      });
      sumAmt = Math.round(sumAmt * 100) / 100;

      if (Math.abs(sumAmt - amount) < 0.01 && amount > 0) {
        summaryNotice.innerHTML = `<span style="color: var(--success);"><i class="fa-solid fa-circle-check"></i> Total: ₹${sumAmt.toFixed(2)} (Matches Expense Amount)</span>`;
      } else {
        summaryNotice.innerHTML = `<span style="color: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> Total: ₹${sumAmt.toFixed(2)} (Must equal total ₹${amount.toFixed(2)})</span>`;
      }
    } else {
      summaryNotice.innerHTML = `<span style="color: var(--info);"><i class="fa-solid fa-circle-info"></i> Divided equally among selected members.</span>`;
    }
  }

  groupSelect.addEventListener('change', function () {
    loadGroupMembers(this.value);
  });

  if (amountInput) {
    amountInput.addEventListener('input', updateSplitFields);
  }

  splitTypeRadios.forEach(radio => {
    radio.addEventListener('change', updateSplitFields);
  });

  // If initial group selected (e.g. from preset query param)
  if (groupSelect.value) {
    loadGroupMembers(groupSelect.value);
  }
}

/* ==========================================================================
   3. What-If Expense Simulator
   ========================================================================== */
function initSimulator() {
  const simGroupSelect = document.getElementById('sim-group-select') || document.getElementById('expense-group-select');
  const simAmountInput = document.getElementById('sim-amount-input') || document.getElementById('expense-amount-input');
  const simBtn = document.getElementById('run-sim-btn');
  const simResultsBox = document.getElementById('simulator-results-box');

  if (!simBtn || !simGroupSelect) return;

  simBtn.addEventListener('click', async function (e) {
    e.preventDefault();

    const groupId = simGroupSelect.value;
    const desc = document.getElementById('sim-desc-input') ? document.getElementById('sim-desc-input').value : '';
    const amount = parseFloat(simAmountInput ? simAmountInput.value : 0) || 0;
    const splitType = document.querySelector('input[name="split_type"]:checked')?.value || 'EQUAL';

    if (!groupId) {
      alert('Please select a group to simulate.');
      return;
    }
    if (amount <= 0) {
      alert('Please enter a valid expense amount greater than 0.');
      return;
    }

    // Collect checked participants
    const participants = [];
    document.querySelectorAll('.participant-checkbox:checked').forEach(cb => {
      const uid = cb.getAttribute('data-user-id');
      const pct = document.querySelector(`input[name="percentage_${uid}"]`)?.value || 0;
      const customAmt = document.querySelector(`input[name="custom_amount_${uid}"]`)?.value || 0;
      participants.push({
        user_id: uid,
        percentage: pct,
        custom_amount: customAmt
      });
    });

    if (participants.length === 0) {
      alert('Please select at least one participant.');
      return;
    }

    try {
      simBtn.disabled = true;
      simBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Simulating...';

      const response = await fetch('/simulator/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          group_id: groupId,
          amount: amount,
          split_type: splitType,
          participants: participants
        })
      });

      const res = await response.json();
      if (!response.ok) {
        alert(res.error || 'Simulation failed.');
        return;
      }

      // Render Simulation Results
      renderSimulationResults(res, desc, amount, groupId, splitType);
    } catch (err) {
      alert('Network error while simulating: ' + err.message);
    } finally {
      simBtn.disabled = false;
      simBtn.innerHTML = '<i class="fa-solid fa-calculator"></i> Run Simulation';
    }
  });

  function renderSimulationResults(data, desc, amount, groupId, splitType) {
    if (!simResultsBox) return;

    let sharesHtml = '';
    data.simulated_shares.forEach(s => {
      sharesHtml += `
        <tr>
          <td><strong>${s.name}</strong></td>
          <td>${s.percentage}%</td>
          <td style="font-weight: 700; color: var(--primary);">₹${s.share.toFixed(2)}</td>
        </tr>
      `;
    });

    const isExceeded = data.budget_exceeded;
    const alertBanner = isExceeded
      ? `<div class="alert alert-danger"><i class="fa-solid fa-triangle-exclamation"></i> <strong>Budget Exceeded Alert:</strong> This expense of ₹${data.expense_amount.toFixed(2)} will cause ${data.group_name}'s budget to be exceeded by ₹${(data.projected_spending - data.monthly_budget).toFixed(2)}!</div>`
      : `<div class="alert alert-${data.projected_percent >= 90 ? 'danger' : (data.projected_percent >= 75 ? 'warning' : 'success')}"><i class="fa-solid fa-circle-info"></i> Projected Status: <strong>${data.projected_status}</strong> (${data.projected_percent}% of budget used)</div>`;

    simResultsBox.innerHTML = `
      <div class="card" style="border: 2px solid var(--primary); box-shadow: var(--shadow-md);">
        <div class="card-header">
          <h3 class="card-title"><i class="fa-solid fa-chart-line"></i> Simulation Preview for: "${desc || 'Proposed Expense'}"</h3>
          <span class="badge ${data.projected_badge}">${data.projected_status}</span>
        </div>

        ${alertBanner}

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
          <div class="card" style="margin-bottom:0; background: var(--bg-page);">
            <small class="text-secondary">Group Budget</small>
            <div style="font-size: 1.25rem; font-weight: 700;">₹${data.monthly_budget.toLocaleString()}</div>
          </div>
          <div class="card" style="margin-bottom:0; background: var(--bg-page);">
            <small class="text-secondary">Current Spending</small>
            <div style="font-size: 1.25rem; font-weight: 700;">₹${data.current_spending.toLocaleString()}</div>
            <small class="text-muted">Remaining: ₹${data.current_remaining.toLocaleString()}</small>
          </div>
          <div class="card" style="margin-bottom:0; background: var(--bg-page); border-left: 4px solid var(--primary);">
            <small class="text-secondary">Projected Spending</small>
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">₹${data.projected_spending.toLocaleString()}</div>
            <small style="color: ${data.projected_remaining < 0 ? 'var(--danger)' : 'var(--text-secondary)'};">
              Projected Remaining: ₹${data.projected_remaining.toLocaleString()}
            </small>
          </div>
        </div>

        <h4 style="margin-bottom: 0.75rem; font-size: 1rem;">Estimated Member Shares:</h4>
        <div class="table-responsive" style="margin-bottom: 1.5rem;">
          <table class="table">
            <thead>
              <tr>
                <th>Member</th>
                <th>Share %</th>
                <th>Estimated Amount</th>
              </tr>
            </thead>
            <tbody>
              ${sharesHtml}
            </tbody>
          </table>
        </div>

        <div style="background: var(--bg-page); padding: 1.25rem; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
          <div>
            <strong>Notice:</strong> This simulation is a preview only and has <em>not</em> been saved to the database.
          </div>
          <form action="/expenses/add" method="POST" id="confirm-expense-form">
            <input type="hidden" name="csrf_token" value="${document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''}">
            <input type="hidden" name="group_id" value="${groupId}">
            <input type="hidden" name="description" value="${desc || 'Simulated Expense'}">
            <input type="hidden" name="amount" value="${amount}">
            <input type="hidden" name="category" value="Other">
            <input type="hidden" name="date" value="${new Date().toISOString().split('T')[0]}">
            <input type="hidden" name="paid_by" value="${window.currentUserId || ''}">
            <input type="hidden" name="split_type" value="${splitType}">
            <!-- Insert dynamic participant values -->
            <div id="confirm-participants-inputs"></div>
            <button type="submit" class="btn btn-primary">
              <i class="fa-solid fa-check-double"></i> Confirm & Add Expense to Database
            </button>
          </form>
        </div>
      </div>
    `;

    // Populate hidden inputs in confirmation form
    const confirmInputsContainer = document.getElementById('confirm-participants-inputs');
    if (confirmInputsContainer) {
      data.simulated_shares.forEach(s => {
        const pInp = document.createElement('input');
        pInp.type = 'hidden';
        pInp.name = 'participants';
        pInp.value = s.user_id;
        confirmInputsContainer.appendChild(pInp);

        if (splitType === 'PERCENTAGE') {
          const pctInp = document.createElement('input');
          pctInp.type = 'hidden';
          pctInp.name = `percentage_${s.user_id}`;
          pctInp.value = s.percentage;
          confirmInputsContainer.appendChild(pctInp);
        } else if (splitType === 'CUSTOM') {
          const amtInp = document.createElement('input');
          amtInp.type = 'hidden';
          amtInp.name = `custom_amount_${s.user_id}`;
          amtInp.value = s.share;
          confirmInputsContainer.appendChild(amtInp);
        }
      });
    }

    simResultsBox.scrollIntoView({ behavior: 'smooth' });
  }
}
