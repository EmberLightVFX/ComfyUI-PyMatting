import os
import sys
import subprocess
import threading
import locale


def handle_stream(stream, prefix):
    stream.reconfigure(encoding=locale.getpreferredencoding(), errors="replace")
    for msg in stream:
        if (
            prefix == "[!]"
            and ("it/s]" in msg or "s/it]" in msg)
            and ("%|" in msg or "it [" in msg)
        ):
            if msg.startswith("100%"):
                print("\r" + msg, end="", file=sys.stderr),
            else:
                print("\r" + msg[:-1], end="", file=sys.stderr),
        elif prefix == "[!]":
            print(prefix, msg, end="", file=sys.stderr)
        else:
            print(prefix, msg, end="")


def run_script(cmd, cwd="."):
    if len(cmd) > 0 and cmd[0].startswith("#"):
        print(f"[ComfyUI-Manager] Unexpected behavior: `{cmd}`")
        return 0

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    stdout_thread = threading.Thread(target=handle_stream, args=(process.stdout, ""))
    stderr_thread = threading.Thread(target=handle_stream, args=(process.stderr, "[!]"))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    return process.wait()


try:
    from .PyMatting import PyMatting
except Exception:
    my_path = os.path.dirname(__file__)
    requirements_path = os.path.join(my_path, "requirements.txt")

    print("## ComfyUI-PyMatting: installing dependencies")

    run_script([sys.executable, "-s", "-m", "pip", "install", "-r", requirements_path])

    try:
        from .PyMatting import PyMatting
    except Exception:
        print(
            "## [ERROR] ComfyUI-Manager: Attempting to reinstall dependencies using an alternative method."
        )
        run_script(
            [
                sys.executable,
                "-s",
                "-m",
                "pip",
                "install",
                "--user",
                "-r",
                requirements_path,
            ]
        )

        try:
            from .PyMatting import PyMatting
        except Exception:
            print(
                "## [ERROR] ComfyUI-Manager: Failed to install the GitPython package in the correct Python environment. Please install it manually in the appropriate environment. (You can seek help at https://app.element.io/#/room/%23comfyui_space%3Amatrix.org)"
            )

    print("## ComfyUI-Manager: installing dependencies done.")

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique

NODE_CLASS_MAPPINGS = {
    "PyMatting": PyMatting,
}
