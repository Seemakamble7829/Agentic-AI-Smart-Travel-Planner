"""Start the Streamlit app and open it automatically in the default browser.

Usage:
    python run_and_open.py

This script runs Streamlit using the current Python interpreter, polls the
local server until it responds, then opens the URL in your default browser.
It leaves the Streamlit process running in the background.
"""
import subprocess
import sys
import time
import webbrowser

import requests


def start_streamlit(app_path: str = "app.py", port: int = 8501):
    """Start Streamlit as a subprocess using the same Python interpreter."""
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.port", str(port), "--server.headless", "true"]
    # Start process without blocking; inherit stdout/stderr so you can inspect logs if desired
    proc = subprocess.Popen(cmd)
    return proc


def wait_for_server(url: str, timeout: int = 30):
    """Poll the `url` until it returns a successful response or timeout (seconds)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main():
    url = "http://localhost:8501"
    print("Starting Streamlit...")
    proc = start_streamlit()
    try:
        ok = wait_for_server(url, timeout=30)
        if ok:
            print(f"Streamlit appears online at {url}; opening in browser...")
            webbrowser.open(url)
        else:
            print(f"Timed out waiting for Streamlit at {url}. Check logs; the process is running (PID={proc.pid}).")
    except KeyboardInterrupt:
        print("Interrupted; leaving Streamlit process running.")


if __name__ == "__main__":
    main()
