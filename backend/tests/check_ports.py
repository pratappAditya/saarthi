import socket
import httpx

def check_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

print(f"Port 11434 (Ollama): {check_port('127.0.0.1', 11434)}")
print(f"Port 8000 (Backend): {check_port('127.0.0.1', 8000)}")
print(f"Port 5173 (Frontend): {check_port('127.0.0.1', 5173)}")
