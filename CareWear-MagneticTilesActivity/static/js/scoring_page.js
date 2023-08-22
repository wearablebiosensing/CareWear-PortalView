// Global Constants
const userID = getLocalStorageOrNull("userID");
const level = getLocalStorageOrNull("currentLevel");
const completetion_time_display = document.getElementById("completion_time");

// Update localStorage so that the next level is displayed on tiles_game page
const nextLevelBtn = document.getElementById("next_level");
nextLevelBtn.addEventListener("click", () => {
  let current_level = Number(localStorage.getItem("currentLevel"));
  localStorage.setItem("currentLevel", current_level + 1); // Next Level
});

// Make a fetch request to the completion-time endpoint
fetch(`/completion_time/${userID}/${level}`)
  .then((response) => response.text())
  .then((completionTime) => {
    // Display the completion time on the page
    completetion_time_display.textContent = completionTime;
  })
  .catch((error) => {
    completetion_time_display.textContent = "Error fetching completion time";
    console.error("Error fetching completion time:", error);
  });

//Getting Graphs from flask server
function loadImage(url, container) {
  const loadingElement = container.querySelector(".loading");
  const errorElement = container.querySelector(".error");
  const imageElement = container.querySelector(".image");

  //Start with loading
  loadingElement.style.display = "block";

  fetch(url)
    .then((response) => {
      if (!response.ok) {
        //Error
        loadingElement.style.display = "none";
        errorElement.style.display = "block";

        throw new Error("Network response was not ok");
      }
      return response.blob();
    })
    .then((blob) => {
      //Success
      loadingElement.style.display = "none";
      errorElement.style.display = "none";
      imageElement.style.display = "block";

      const imageURL = URL.createObjectURL(blob);
      imageElement.src = imageURL;
    })
    .catch((error) => {
      //Error
      loadingElement.style.display = "none";
      errorElement.style.display = "block";
      console.error("Error loading image:", error);
    });
}

function getGraph(currentUserID, currentLevel, containerID) {
  const container = document.getElementById(containerID);
  const endpoint = container.getAttribute("data-endpoint");

  const url = `/${endpoint}/${currentUserID}/${currentLevel}`;

  loadImage(url, container);
}

// Call the function with appropriate parameters and unique element IDs
getGraph(userID, level, "mouse_movement_graph");
getGraph(userID, level, "acceleration_graph");
