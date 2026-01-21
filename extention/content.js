console.log("Loaded Content Script")
let emailId = null
function maybeCheckEmail() {
	// Gmail URL changes without reload
	const match = location.hash.match(/#inbox\/([^/]+)/);
	if (!match) return;
	if (emailId == match[1]) return;
	emailId = match[1];
	const listItemEl = document.querySelector("[role=listitem]");
	if (listItemEl === null) return;
	const parsedObj = {
		email: listItemEl.querySelector("[email]").attributes?.email.value,
		name: listItemEl.querySelector("[email]").attributes?.name.value,
		content: listItemEl.innerText,
	}
	console.log(parsedObj)
	chrome.runtime.sendMessage({ type: "OPENED_EMAIL", payload: parsedObj })
}

const observer = new MutationObserver(maybeCheckEmail)
observer.observe(document.body, { childList: true, subtree: true })

