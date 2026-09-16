const form = document.getElementById("entry-form");
const nameInput = document.getElementById("name");
const passwordInput = document.getElementById("password");
const moodInput = document.getElementById("mood");
const messageInput = document.getElementById("message");
const charCount = document.getElementById("char-count");
const formError = document.getElementById("form-error");

const entryList = document.getElementById("entry-list");
const entryCount = document.getElementById("entry-count");
const emptyMsg = document.getElementById("empty-msg");

const deleteModal = document.getElementById("delete-modal");
const deletePasswordInput = document.getElementById("delete-password");
const deleteError = document.getElementById("delete-error");
const cancelDeleteBtn = document.getElementById("cancel-delete");
const confirmDeleteBtn = document.getElementById("confirm-delete");

const toast = document.getElementById("toast");

let pendingDeleteId = null;
let toastTimer = null;

function showToast(text) {
  toast.textContent = text;
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, 2200);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function renderEntries(entries) {
  entryList.innerHTML = "";
  entryCount.textContent = entries.length;
  emptyMsg.hidden = entries.length > 0;

  entries.forEach((entry) => {
    const card = document.createElement("div");
    card.className = "entry";
    card.innerHTML = `
      <div class="entry-top">
        <span class="entry-author"><span class="entry-mood">${entry.mood}</span>${escapeHtml(entry.name)}</span>
        <span class="entry-date">${entry.created_at}</span>
      </div>
      <p class="entry-message">${escapeHtml(entry.message)}</p>
      <div class="entry-actions">
        <button class="btn-delete" data-id="${entry.id}">삭제</button>
      </div>
    `;
    entryList.appendChild(card);
  });

  document.querySelectorAll(".btn-delete").forEach((btn) => {
    btn.addEventListener("click", () => openDeleteModal(btn.dataset.id));
  });
}

async function loadEntries() {
  const res = await fetch("/api/entries");
  const data = await res.json();
  renderEntries(data.entries);
}

messageInput.addEventListener("input", () => {
  charCount.textContent = messageInput.value.length;
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.textContent = "";

  const payload = {
    name: nameInput.value.trim(),
    password: passwordInput.value,
    mood: moodInput.value,
    message: messageInput.value.trim(),
  };

  if (!payload.name || !payload.message || !payload.password) {
    formError.textContent = "이름, 내용, 비밀번호를 모두 입력해주세요.";
    return;
  }
  if (payload.password.length < 4) {
    formError.textContent = "비밀번호는 4자 이상으로 입력해주세요.";
    return;
  }

  const res = await fetch("/api/entries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok) {
    formError.textContent = data.error || "오류가 발생했습니다.";
    return;
  }

  form.reset();
  charCount.textContent = "0";
  showToast("방명록이 등록되었습니다 🌿");
  await loadEntries();
});

function openDeleteModal(id) {
  pendingDeleteId = id;
  deletePasswordInput.value = "";
  deleteError.textContent = "";
  deleteModal.hidden = false;
  deletePasswordInput.focus();
}

function closeDeleteModal() {
  deleteModal.hidden = true;
  pendingDeleteId = null;
}

cancelDeleteBtn.addEventListener("click", closeDeleteModal);

confirmDeleteBtn.addEventListener("click", async () => {
  if (!pendingDeleteId) return;
  const res = await fetch(`/api/entries/${pendingDeleteId}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: deletePasswordInput.value }),
  });
  const data = await res.json();

  if (!res.ok) {
    deleteError.textContent = data.error || "삭제에 실패했습니다.";
    return;
  }

  closeDeleteModal();
  showToast("삭제되었습니다.");
  await loadEntries();
});

deletePasswordInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") confirmDeleteBtn.click();
});

loadEntries();
