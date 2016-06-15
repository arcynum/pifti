from imageio.core.format import Format


def force_close_reader(reader):
    """ Close Imageio Reader

    Terminates a reader internally otherwise the subprocess is
    forcefully killed to prevent zombies

    Returns:
        Dead process
    """

    # Ensure object is Imageio Reader
    if isinstance(reader, Format.Reader):
        # Look for a running subprocess
        if hasattr(reader, '_proc') and not reader.closed:
            # Check for heartbeat
            if reader._proc.poll() is None:
                # Capture running process
                proc = reader._proc
                # Try gently first
                reader.close()
                # Check for zombie
                if proc.poll() is None:
                    # Force the issue, look away
                    proc.kill()
