// dashboard.js

const params = new URLSearchParams(window.location.search);
const accessToken = params.get("access_token");
const displayName = params.get("display_name") || "User";

const welcomeMsg = document.getElementById("welcomeMsg");
welcomeMsg.textContent = `Welcome, ${displayName}!`;

const recommendationsDiv = document.getElementById("recommendations");

async function fetchRecommendations() {
  if (!accessToken) {
    recommendationsDiv.innerHTML =
      "<p>Failed to fetch recommendations. Please log in again.</p>";
    return;
  }

  try {
    recommendationsDiv.innerHTML = "<p>Fetching your recommendations...</p>";
    const response = await fetch(`/recommendations?token=${accessToken}`);
    if (!response.ok) {
      console.error("Error fetching recommendations:", response.statusText);
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const data = await response.json();
    console.log("Fetched Recommendations:", data);

    displayRecommendations(data.tracks || []);
  } catch (error) {
    console.error("Error during fetchRecommendations:", error);
    recommendationsDiv.innerHTML =
      "<p>Error fetching recommendations. Please try again later.</p>";
  }
}

function displayRecommendations(tracks) {
  recommendationsDiv.innerHTML = "";

  if (tracks.length === 0) {
    recommendationsDiv.innerHTML = "<p>No recommendations found.</p>";
    return;
  }

  tracks.forEach((track) => {
    const item = document.createElement("div");
    item.classList.add("result-item");

    const trackTitle = document.createElement("h4");
    trackTitle.textContent = track.name;

    const artistNames = track.artists.map((a) => a.name).join(", ");
    const artistInfo = document.createElement("p");
    artistInfo.textContent = `by ${artistNames}`;

    const trackLink = document.createElement("a");
    trackLink.href = track.external_urls.spotify;
    trackLink.target = "_blank";
    trackLink.textContent = "Open in Spotify";

    item.appendChild(trackTitle);
    item.appendChild(artistInfo);
    item.appendChild(trackLink);

    recommendationsDiv.appendChild(item);
  });
}

const logoutBtn = document.getElementById("logoutBtn");
logoutBtn.addEventListener("click", () => {
  localStorage.clear();
  sessionStorage.clear();

  window.location.href = "/";
});

fetchRecommendations();
