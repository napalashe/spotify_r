const loginBtn = document.getElementById("loginBtn");
const recommendationForm = document.getElementById("recommendationForm");
const getRecsBtn = document.getElementById("getRecsBtn");
const results = document.getElementById("results");
const seedTracksInput = document.getElementById("seedTracks");

// We'll store the token here after the user logs in
let accessToken = null;

/**
 * 1. Click "Login" -> Browser goes to backend /login route -> Spotify Auth
 */
loginBtn.addEventListener("click", () => {
  // If your backend is running locally on port 8000, do:
  window.location.href = "http://localhost:8000/login";
});

/**
 * 2. After successful login, Spotify calls /spotify/callback.
 *    That route returns JSON with access_token. In a real app:
 *    - You might store the token in a cookie or redirect again with the token.
 *    - For simplicity, let's assume the user manually copies/pastes or
 *      we retrieve it from localStorage (this is just a demo).
 */

/**
 * 3. Request recommendations from our backend
 */
getRecsBtn.addEventListener("click", async () => {
  if (!accessToken) {
    alert("No access token. Please log in first or store your token.");
    return;
  }

  const seedTracks = seedTracksInput.value.split(",").map((t) => t.trim());
  const body = {
    seed_tracks: seedTracks,
    seed_artists: [],
    seed_genres: [],
  };

  try {
    const response = await fetch(
      `http://localhost:8000/recommendations?token=${accessToken}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }
    );

    const data = await response.json();
    if (data.tracks) {
      results.innerHTML = data.tracks
        .map((track) => {
          const artistNames = track.artists.map((a) => a.name).join(", ");
          return `<p>${track.name} by ${artistNames}</p>`;
        })
        .join("");
    } else {
      results.innerHTML = "<p>No recommendations found.</p>";
    }
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    results.innerHTML = "<p>Error fetching recommendations.</p>";
  }
});

/**
 * 4. (Optional) On page load, try retrieving a stored token from localStorage
 *    In a production app, you'd do a real OAuth flow with redirects, etc.
 */
window.onload = () => {
  accessToken = localStorage.getItem("access_token");
  if (accessToken) {
    recommendationForm.style.display = "block";
    loginBtn.style.display = "none";
  }
};
