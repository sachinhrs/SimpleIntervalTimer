# Simple Interval Timer 

A clean, desktop interval timer built with GTK4, focused on simplicity, quick editing, and reliable cross-platform sound.

---

## Features

- **Simple UI**: Just click the countdown to set duration in HH:MM:SS—no extra fields clutter the main window.
- **Start/Stop**: One-button control with 1-second updates and continuous repeating intervals.
- **Custom Sounds**: Choose your own alarm file or use a system tone if none is selected.
- **Persistent Settings**: Saves duration and sound path to JSON between sessions.
- **Sound Control**: Alarm stops automatically at the next trigger, when the timer is stopped, or on exit.
- **Cross-Platform**: Works consistently on Windows, macOS, and Linux.

---

## Downloads

**Recommended:**  
Download the appropriate file for your OS from the [Release Assets](#) section and run it locally.  
Release assets are versioned and include bundled builds and release notes.

**Alternative:**  
Run from source—see below for requirements.

---

## Requirements (for building/running from source)

- **Python 3** and **PyGObject (GTK4)** installed on your system.
- **Platform sound tools** for playback (if using the system tone fallback):
  - **Windows:** Built-in `winsound`
  - **macOS:** `afplay`
  - **Linux:** Tries `play`, `paplay`, `aplay`, or `canberra-gtk-play` as available

---

## How to Use

1. Click **"Next: …"** to edit the timer duration.
2. Press **Start** to begin the countdown, **Stop** to halt.
3. While idle, the label displays the set duration.
4. Use the **music-note button** to pick a custom sound file. If none is selected, a system tone plays at each interval.

---

