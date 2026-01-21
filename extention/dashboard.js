const girdEl = document.getElementById("email-grid");
chrome.storage.local.get({ emails: [] }, (result) => {
	for (const msg of result.emails) {
		const { email, name, content } = msg.payload
		const row = document.createElement("div");
		row.className = "email-row"
		row.innerHTML = `
		      <div class="cell">${email ?? "(unknown)"}</div>
		      <div class="cell">${name ?? "(unknown)"}</div>
		      <div class="cell content">${content ?? ""}</div>
		`
		girdEl.appendChild(row)
	}
})


