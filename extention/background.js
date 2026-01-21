chrome.runtime.onMessage.addListener((msg, sender) => {
	if (msg.type == "OPENED_EMAIL") {
		console.log(`received ${sender}`);
		console.log(msg);
		chrome.storage.local.get({ emails: [] }, (result) => {
			result.emails.push(msg);
			chrome.storage.local.set({ emails: result.emails })
		})
	}
})
