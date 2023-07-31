// Get references to the help icon and the popup window
const helpIcon = document.getElementById("help-icon");
const directions_popup = document.getElementById("directions_popup");

const mouse_data_toggle_btn = document.getElementById("mouse-data");
const mouse_data_popup = document.getElementById("mouse_popup");
mouse_data_popup.style.display = "none";

// Toggle the popup when the help icon is clicked
mouse_data_toggle_btn.addEventListener("click", () => {
  console.log(typeof mouse_data_popup.style.display);

  if (mouse_data_popup.style.display === "none") {
    mouse_data_popup.style.display = "block";
  } else {
    mouse_data_popup.style.display = "none";
  }
});

// Show the popup when the help icon is hovered over
helpIcon.addEventListener("mouseover", () => {
  directions_popup.style.display = "block";
});

// Hide the popup when the mouse leaves the help icon
helpIcon.addEventListener("mouseout", () => {
  directions_popup.style.display = "none";
});
