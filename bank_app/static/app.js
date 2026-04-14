const stateUrl = "/api/state";
const feedback = document.getElementById("feedback");
const accountsGrid = document.getElementById("accountsGrid");
const accountCardTemplate = document.getElementById("accountCardTemplate");

const moneyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

async function fetchState() {
  const response = await fetch(stateUrl);
  const payload = await response.json();
  renderState(payload);
}

function renderState(state) {
  document.getElementById("totalAccounts").textContent = state.summary.totalAccounts;
  document.getElementById("activeAccounts").textContent = state.summary.activeAccounts;
  document.getElementById("lockedAccounts").textContent = state.summary.lockedAccounts;
  document.getElementById("totalBalance").textContent = moneyFormatter.format(
    state.summary.totalBalance,
  );

  accountsGrid.innerHTML = "";

  if (!state.accounts.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No accounts yet. Open one to get started.";
    accountsGrid.appendChild(empty);
    return;
  }

  state.accounts.forEach((account) => {
    const fragment = accountCardTemplate.content.cloneNode(true);
    fragment.querySelector(".account-number").textContent = account.accountNumber;
    fragment.querySelector(".balance-value").textContent = moneyFormatter.format(
      account.balance,
    );

    const badge = fragment.querySelector(".badge");
    badge.textContent = account.locked ? "Locked" : "Active";
    badge.classList.add(account.locked ? "is-locked" : "is-active");

    const historyList = fragment.querySelector(".history-list");
    account.history.forEach((entry) => {
      const item = document.createElement("li");
      item.innerHTML = `
        <strong>${entry.message}</strong>
        <span>${entry.timestamp}</span>
      `;
      historyList.appendChild(item);
    });

    if (!account.history.length) {
      const item = document.createElement("li");
      item.innerHTML = `
        <strong>No activity yet</strong>
        <span>New accounts will show their latest activity here.</span>
      `;
      historyList.appendChild(item);
    }

    accountsGrid.appendChild(fragment);
  });
}

function setFeedback(message, type) {
  feedback.hidden = false;
  feedback.textContent = message;
  feedback.className = `feedback is-${type}`;
}

async function submitForm(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch(form.dataset.endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error || "Something went wrong.");
    }

    setFeedback(body.message || form.dataset.success || "Saved.", "success");
    renderState(body.state);
    form.reset();
  } catch (error) {
    setFeedback(error.message, "error");
  }
}

document.querySelectorAll("form[data-endpoint]").forEach((form) => {
  form.addEventListener("submit", submitForm);
});

fetchState().catch(() => {
  setFeedback("Could not load the dashboard state.", "error");
});
