let token = "";
let currentGroup = "";
const api = "http://localhost:8000";

function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const form = new FormData();
  form.append("username", username);
  form.append("password", password);
  fetch(api + "/login", { method: "POST", body: form })
    .then(r => r.json())
    .then(data => {
      token = data.token;
      document.getElementById("login").style.display = "none";
      document.getElementById("chat").style.display = "block";
      loadGroups();
    });
}

function authHeaders() {
  return { Authorization: "Bearer " + token };
}

function loadGroups() {
  fetch(api + "/groups", { headers: authHeaders() })
    .then(r => r.json())
    .then(gs => {
      const list = document.getElementById("groups");
      list.innerHTML = "";
      gs.forEach(g => {
        const li = document.createElement("li");
        li.textContent = g.name;
        li.onclick = () => { currentGroup = g.id; loadMessages(); };
        list.appendChild(li);
      });
    });
}

function createGroup() {
  const name = document.getElementById("groupName").value;
  const form = new FormData();
  form.append("name", name);
  fetch(api + "/groups", { method: "POST", body: form, headers: authHeaders() })
    .then(() => loadGroups());
}

function loadMessages() {
  if (!currentGroup) return;
  fetch(`${api}/groups/${currentGroup}/messages`, { headers: authHeaders() })
    .then(r => r.json())
    .then(msgs => {
      const div = document.getElementById("messages");
      div.innerHTML = msgs.map(m => `<p><b>${m.sender_id}</b>: ${m.content}</p>`).join("\n");
    });
}

function sendMessage() {
  if (!currentGroup) return;
  const content = document.getElementById("message").value;
  const form = new FormData();
  form.append("content", content);
  fetch(`${api}/groups/${currentGroup}/messages`, { method: "POST", body: form, headers: authHeaders() })
    .then(() => { document.getElementById("message").value = ""; loadMessages(); });
}
