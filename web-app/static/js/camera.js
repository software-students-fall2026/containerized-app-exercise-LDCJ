const video = document.querySelector("#camera");
const canvas = document.querySelector("#canvas");
const preview = document.querySelector("#preview");
const statusMessage = document.querySelector("#status");
const result = document.querySelector("#result");

const startButton = document.querySelector("#start-camera");
const takeButton = document.querySelector("#take-photo");
const sendButton = document.querySelector("#send-photo");
const retakeButton = document.querySelector("#retake");

let stream = null;
let photoBlob = null;
let previewUrl = null;

startButton.addEventListener("click", async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { facingMode: "user" },
    });

    video.srcObject = stream;
    takeButton.disabled = false;
    statusMessage.textContent = "Camera is ready.";
  } catch (error) {
    statusMessage.textContent =
      "Could not start the camera. Check camera permissions and try again.";
  }
});

takeButton.addEventListener("click", () => {
  if (!video.videoWidth || !video.videoHeight) {
    statusMessage.textContent = "The camera is still starting. Try again in a moment.";
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  canvas.toBlob((blob) => {
    if (!blob) {
        statusMessage.textContent = "Could not capture the photo. Please try again.";
      return;
    }

    photoBlob = blob;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = URL.createObjectURL(blob);

    preview.src = previewUrl;
    preview.hidden = false;
    video.hidden = true;
    takeButton.hidden = true;
    sendButton.disabled = false;
    retakeButton.hidden = false;
    status.textContent = "Photo captured. Send it to the agent when ready.";
  }, "image/jpeg", 0.9);
});

retakeButton.addEventListener("click", () => {
  photoBlob = null;
  preview.hidden = true;
  video.hidden = false;
  takeButton.hidden = false;
  sendButton.disabled = true;
  retakeButton.hidden = true;
  result.textContent = "";
  statusMessage.textContent = "Take another photo.";

  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
});

sendButton.addEventListener("click", async () => {
  if (!photoBlob) return;

  const formData = new FormData();
  formData.append("image", photoBlob, "hand-photo.jpg");

  sendButton.disabled = true;
  statusMessage.textContent = "Sending photo to the agent…";

  try {
    const response = await fetch("/api/plays", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "The agent could not process the photo.");
    }

    result.textContent =
      `You played ${data.player_move}; the agent played ${data.opponent_move}. ` +
      `Result: ${data.outcome}.`;
      statusMessage.textContent = "";
  } catch (error) {
    statusMessage.textContent = error.message;
    sendButton.disabled = false;
  }
});