import threading
import socket


import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("SERVER_PORT", 65432))

class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.clients = []
        
    def handle_client(self, conn, addr):
        print(f"Connected: {addr}")

        try:
            while True:
                data = conn.recv(2048)

                if not data:
                    break

                print(f"{addr}: {data.decode()}")

                for client in self.clients.copy():
                    if client != conn:
                        try:
                            client.sendall(data)
                        except OSError:
                            pass

        except OSError as e:
            print(f"Connection error: {e}")

        finally:
            if conn in self.clients:
                self.clients.remove(conn)

            conn.close()
            print(f"Disconnected: {addr}")
            
            
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            s.settimeout(1)

            print("Server running...")
            
            try:
                while True:
                    
                    try:                        
                        conn, addr = s.accept()
                        
                    except socket.timeout:
                        continue
                    
                    self.clients.append(conn)

                    thread = threading.Thread(
                        target=self.handle_client, args=(conn, addr), daemon=True
                    )
                    thread.start()
                    
            except KeyboardInterrupt:
                print("\nShutting down server...")
                for client in self.clients:
                    client.close()
                
                
if __name__ == "__main__":
    server = Server()
    server.start()