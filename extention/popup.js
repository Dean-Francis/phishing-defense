console.log("Hello World");

document
  .getElementById("dashboardBtn")
  .addEventListener("click", () => {
    chrome.tabs.create({
      url: chrome.runtime.getURL("dashboard.html")
    });
  });
