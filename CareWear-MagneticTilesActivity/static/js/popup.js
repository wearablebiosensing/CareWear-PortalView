// Get references to the help icon and the popup window
const helpIcon = document.getElementById("help-icon");
const popup = document.getElementById("popup");

// Show the popup when the help icon is hovered over
helpIcon.addEventListener("mouseover", () => {
  popup.style.display = "block";
});

// Hide the popup when the mouse leaves the help icon
helpIcon.addEventListener("mouseout", () => {
  popup.style.display = "none";
});
