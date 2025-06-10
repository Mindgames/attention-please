const cron = require("node-cron");
const player = require("play-sound")((opts = {}));
const notifier = require("node-notifier");
const path = require("path");
const os = require("os");

// Log startup
console.log("Grais Reminder System");
console.log("---------------------------");
console.log("Reminder will run hourly between 8am and 8pm");
console.log("Press Ctrl+C to exit");

// Function to check if current hour is between 8am and 8pm (8-20)
function isWithinActiveHours() {
  const currentHour = new Date().getHours();
  return currentHour >= 8 && currentHour <= 20;
}

// Function to play sound based on platform
function playSound() {
  const platform = os.platform();

  if (platform === "darwin") {
    // On macOS, use system sound
    player.play("/System/Library/Sounds/Glass.aiff", (err) => {
      if (err) {
        console.error("Error playing sound:", err);
        // Fallback to notification sound
        notifier.notify({
          title: "Grais Reminder",
          message: "Time to check back with the system!",
          sound: true,
        });
      }
    });
  } else if (platform === "win32") {
    // On Windows, use system sound
    player.play("C:\\Windows\\Media\\notify.wav", (err) => {
      if (err) {
        console.error("Error playing sound:", err);
        // Fallback to notification sound
        notifier.notify({
          title: "Grais Reminder",
          message: "Time to check back with the system!",
          sound: true,
        });
      }
    });
  } else {
    // For other platforms, rely on node-notifier's sound
    notifier.notify({
      title: "Grais Reminder",
      message: "Time to check back with the system!",
      sound: true,
    });
  }
}

// Function to play sound and show notification
function playReminder() {
  const currentTime = new Date().toLocaleTimeString();

  if (isWithinActiveHours()) {
    console.log(`[${currentTime}] Reminder activated!`);

    // Play sound and show notification
    playSound();

    // Show notification (without sound since we handle it separately)
    notifier.notify({
      title: "Grais Reminder",
      message: "Time to check back with the system!",
      icon: path.join(__dirname, "icon.png"), // Uses default icon if file doesn't exist
      sound: false,
      wait: false,
    });
  } else {
    console.log(
      `[${currentTime}] Outside active hours (8am-8pm). Skipping notification.`
    );
  }
}

// Schedule reminder to run every hour
cron.schedule("0 * * * *", playReminder);

// Run immediately on startup if within active hours
if (isWithinActiveHours()) {
  console.log("Within active hours - Running initial reminder...");
  playReminder();
} else {
  console.log(
    "Outside active hours (8am-8pm) - Waiting until next active hour."
  );
}
