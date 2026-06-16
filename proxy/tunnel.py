"""Bidirectional TCP tunnel used for HTTPS CONNECT.

Uses select.select() over read/write/exceptional sets on both sockets so
neither side can block the other on a slow peer.
"""
import select
import socket

BUFFER_SIZE = 8192
SELECT_TIMEOUT = 30.0


def _relay(src: socket.socket, dst: socket.socket) -> bool:
    """Forward one batch of bytes from src -> dst. Returns False on EOF/error."""
    try:
        data = src.recv(BUFFER_SIZE)
    except OSError:
        return False
    if not data:
        return False
    try:
        dst.sendall(data)
    except OSError:
        return False
    return True


def tunnel_traffic(client: socket.socket, server: socket.socket):
    """Pump bytes between `client` and `server` until either side closes."""
    sockets = (client, server)
    try:
        while True:
            readable, writable, exceptional = select.select(
                sockets, sockets, sockets, SELECT_TIMEOUT
            )
            if exceptional:
                break
            if not readable and not writable:
                # Idle timeout
                continue
            for sock in readable:
                other = server if sock is client else client
                if not _relay(sock, other):
                    return
    except (select.error, OSError):
        pass
    finally:
        for s in (client, server):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                s.close()
            except OSError:
                pass
