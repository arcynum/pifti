"""
Various utilities for Pifti
"""


def force_close_reader(reader):
    """ Close Imageio Reader

    Terminates a reader otherwise the subprocess is forcefully killed

    Note: A zombie processes may remain
    """
    from imageio.core.format import Format

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
                # Check for unresponsive running process after SIGTERM
                if proc.poll() is None:
                    # SIGKILL
                    proc.kill() # NOQA
        elif not reader.closed:
            # Terminate normally
            reader.close()
