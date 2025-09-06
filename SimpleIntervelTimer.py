import json
import platform
import subprocess
from pathlib import Path
from threading import Thread

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gtk, GLib, Gio

# winsound is only on Windows; import conditionally
try:
    import winsound
except ImportError:
    winsound = None

SETTINGS_FILE = "timer_settings.json"

class IntervalTimerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Interval Timer")

        # State
        self.timer_duration_seconds = 60  # default 1 minute
        self.alarm_sound_path = None
        self.timer_running = False
        self.remaining_seconds = 0
        self._timer_source_id = None

        # Track playback to stop later
        self._sound_proc = None          # Popen handle for macOS/Linux subprocess players
        self._playing_windows = False    # Whether winsound async is active

        # Load settings
        self.load_settings()

        # Layout
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        for prop in ("margin_start", "margin_end", "margin_top", "margin_bottom"):
            getattr(hbox, f"set_{prop}")(12)
        self.set_child(hbox)

        # Countdown label (clickable to edit duration)
        self.countdown_label = Gtk.Label(label="Next: " + self.seconds_to_hms(self.timer_duration_seconds))
        self.countdown_label.set_xalign(0.0)
        # Make label clickable
        click = Gtk.GestureClick.new()
        click.connect("released", self.on_countdown_clicked)
        self.countdown_label.add_controller(click)
        hbox.append(self.countdown_label)

        # Start/Stop button
        self.start_stop_button = Gtk.Button(label="Start")
        self.start_stop_button.connect("clicked", self.on_start_stop_clicked)
        hbox.append(self.start_stop_button)

        # Sound select button (music note)
        self.sound_button = Gtk.Button(label="♫")
        self.sound_button.set_tooltip_text("Select alarm sound")
        self.sound_button.connect("clicked", self.on_sound_button_clicked)
        hbox.append(self.sound_button)

        # Initialize labels
        self.remaining_seconds = self.timer_duration_seconds
        self.update_labels()

        # Ensure cleanup when window closes
        self.connect("close-request", self.on_close_request)

    # Click countdown -> dialog to edit duration
    def on_countdown_clicked(self, gesture, n_press, x, y):
        dialog = Gtk.Dialog(title="Set Timer Duration", transient_for=self, modal=True)
        box = dialog.get_content_area()

        entry = Gtk.Entry()
        entry.set_placeholder_text("HH:MM:SS")
        entry.set_text(self.seconds_to_hms(self.timer_duration_seconds))
        entry.set_activates_default(True)
        box.append(entry)

        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        ok_btn = dialog.add_button("_OK", Gtk.ResponseType.OK)
        ok_btn.get_style_context().add_class("suggested-action")
        dialog.set_default_response(Gtk.ResponseType.OK)

        dialog.connect("response", lambda d, resp: self.on_duration_dialog_response(d, resp, entry))
        dialog.show()

    def on_duration_dialog_response(self, dialog, response, entry):
        if response == Gtk.ResponseType.OK:
            text = entry.get_text().strip()
            seconds = self.hms_to_seconds(text)
            if seconds > 0:
                self.timer_duration_seconds = seconds
                if not self.timer_running:
                    self.remaining_seconds = self.timer_duration_seconds
                self.save_settings()
                self.update_labels()
        dialog.destroy()

    def on_start_stop_clicked(self, button):
        if not self.timer_running:
            self.start_timer()
        else:
            self.stop_timer()

    def start_timer(self):
        if self.timer_running:
            return
        self.timer_running = True
        self.remaining_seconds = self.timer_duration_seconds
        self.start_stop_button.set_label("Stop")
        self.update_labels()
        self._timer_source_id = GLib.timeout_add_seconds(1, self._on_timer_tick)

    def stop_timer(self):
        if not self.timer_running:
            return
        self.timer_running = False
        if self._timer_source_id:
            GLib.source_remove(self._timer_source_id)
            self._timer_source_id = None
        self.start_stop_button.set_label("Start")
        self.remaining_seconds = self.timer_duration_seconds
        # Stop any ringing when timer is stopped
        self.stop_alarm_sound()
        self.update_labels()

    def _on_timer_tick(self):
        if self.remaining_seconds <= 0:
            # Stop any ongoing sound, trigger alarm, and restart next interval
            self.stop_alarm_sound()
            self.play_alarm_sound()
            self.remaining_seconds = self.timer_duration_seconds
        else:
            self.remaining_seconds -= 1
        self.update_labels()
        return True  # keep the timeout active

    def update_labels(self):
        shown = self.remaining_seconds if self.timer_running else self.timer_duration_seconds
        self.countdown_label.set_label("Next: " + self.seconds_to_hms(shown))

    # ---------- File chooser ----------
    def on_sound_button_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select Alarm Sound File",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK,
        )

        # Audio filter
        filter_audio = Gtk.FileFilter()
        filter_audio.set_name("Audio Files")
        for mt in ("audio/mpeg", "audio/x-wav", "audio/ogg", "audio/flac", "audio/aac"):
            filter_audio.add_mime_type(mt)
        for pat in ("*.mp3", "*.wav", "*.ogg", "*.flac", "*.aac", "*.m4a"):
            filter_audio.add_pattern(pat)
        dialog.add_filter(filter_audio)

        dialog.connect("response", self.on_file_dialog_response)
        dialog.show()

    def on_file_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            file = dialog.get_file()
            if file:
                path = file.get_path()
                if path:
                    self.alarm_sound_path = path
                    self.save_settings()
        dialog.destroy()

    # ---------- Sound playback (subprocess / system) ----------
    def stop_alarm_sound(self):
        # Stop subprocess-based players (macOS/Linux)
        if self._sound_proc is not None:
            try:
                self._sound_proc.terminate()
            except Exception:
                pass
            try:
                self._sound_proc.kill()
            except Exception:
                pass
            self._sound_proc = None

        # Stop winsound playback on Windows
        if winsound and self._playing_windows:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
            self._playing_windows = False

    def play_alarm_sound(self):
        def play():
            # Ensure previous sound is stopped before starting a new one
            self.stop_alarm_sound()

            system_name = platform.system()
            path = self.alarm_sound_path
            if path and Path(path).exists():
                try:
                    if system_name == "Windows" and winsound:
                        # Async so UI doesn't block; we can purge later
                        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        self._playing_windows = True
                        return
                    elif system_name == "Darwin":
                        # macOS: afplay
                        self._sound_proc = subprocess.Popen(["afplay", path])
                        return
                    elif system_name == "Linux":
                        # Try common CL players in order
                        for cmd in (["play", path], ["paplay", path], ["aplay", path]):
                            try:
                                self._sound_proc = subprocess.Popen(cmd)
                                return
                            except FileNotFoundError:
                                continue
                except Exception:
                    pass  # fall back to system sound

            # No custom file or failed: play default system sound
            self.play_system_sound(system_name)

        Thread(target=play, daemon=True).start()

    def play_system_sound(self, system_name):
        # Stop any ongoing first
        self.stop_alarm_sound()

        try:
            if system_name == "Windows" and winsound:
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
                self._playing_windows = True
            elif system_name == "Darwin":
                # Use a standard macOS sound
                self._sound_proc = subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
            elif system_name == "Linux":
                # Prefer a desktop helper; otherwise fall back to sample files
                for cmd in (
                    ["canberra-gtk-play", "-i", "bell"],
                    ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                    ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"],
                ):
                    try:
                        self._sound_proc = subprocess.Popen(cmd)
                        break
                    except FileNotFoundError:
                        continue
        except Exception:
            pass  # silent fallback

    # ---------- Settings ----------
    def save_settings(self):
        data = {
            "timer_duration_seconds": self.timer_duration_seconds,
            "alarm_sound_path": self.alarm_sound_path,
        }
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def load_settings(self):
        try:
            if Path(SETTINGS_FILE).exists():
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.timer_duration_seconds = data.get("timer_duration_seconds", 60)
                    self.alarm_sound_path = data.get("alarm_sound_path", None)
        except Exception:
            self.timer_duration_seconds = 60
            self.alarm_sound_path = None
        self.remaining_seconds = self.timer_duration_seconds

    # ---------- Window close ----------
    def on_close_request(self, *args):
        # Stop timer callbacks and any sound before exit
        if self._timer_source_id:
            GLib.source_remove(self._timer_source_id)
            self._timer_source_id = None
        self.stop_alarm_sound()
        return False  # allow closing

    # ---------- Helpers ----------
    @staticmethod
    def seconds_to_hms(seconds):
        seconds = max(0, int(seconds))
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def hms_to_seconds(hms):
        try:
            parts = [int(p) for p in hms.split(":")]
            if len(parts) == 3:
                h, m, s = parts
            elif len(parts) == 2:
                h, m, s = 0, parts, parts[18]
            elif len(parts) == 1:
                h, m, s = 0, 0, parts
            else:
                return 0
            if h < 0 or not (0 <= m < 60) or not (0 <= s < 60):
                return 0
            return h * 3600 + m * 60 + s
        except Exception:
            return 0

class IntervalTimerApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.intervaltimer")

    def do_activate(self):
        window = IntervalTimerWindow()
        window.set_application(self)
        window.present()

def main():
    app = IntervalTimerApp()
    app.run()

if __name__ == "__main__":
    main()
