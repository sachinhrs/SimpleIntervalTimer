# SimpleIntervelTimer
Simple Interval Timer is a clean, no‑frills desktop timer for repeating intervals. Tap the countdown to set the time (HH:MM:SS), press Start/Stop, and get a chime at each interval. Choose your own sound or use a built‑in system tone. It remembers settings,

## Features

- **Simple Setup:** Tap the countdown to set your desired time (hours, minutes, seconds).
- **Start/Stop Control:** One button to start and stop the timer.
- **Custom Sounds:** Pick your own alarm sound file—or use a default system chime.
- **Saves Settings:** Remembers your timer duration and sound choice between sessions.
- **Clean Display:** Shows the set time when idle, and counts down when running.
- **Automatic Stop:** Sounds stop at the next interval or when you close the app.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

## Getting Started

### Prerequisites

- **Python 3.8 or higher**
- **PyGObject** (for GTK4 bindings)
- **GStreamer** (for fallback audio on some platforms—recommended but not always required)
- **Sound playback tools:** On macOS, `afplay` is built in; on Linux, try `canberra-gtk-play`, `paplay`, or `aplay`.

### Installation

1. **Clone or download** this repository.
2. **Install dependencies** (example for Linux with apt):
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good
text
3. **Run the app**:
python3 SimpleIntervalTimer.py
text

## Usage

- **Click the countdown** to set your interval (HH:MM:SS).
- **Press Start** to begin the timer.
- **Press Stop** to pause.
- **Click the music note** to choose a custom alarm sound—or let the app use a system beep.
- **Close the window** to quit. Your settings will be saved.

## Screenshots

*Add your own screenshots here if desired.*

## Support

If you encounter issues or have suggestions, please [open an issue](https://github.com/yourusername/simple-interval-timer/issues).

## Contributing

Contributions are welcome! Please fork the repository and create a pull request.

## License

This project is licensed under the **MIT License**—see the [LICENSE](LICENSE) file fo
