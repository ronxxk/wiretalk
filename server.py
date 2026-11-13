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
            MAX_MESSAGE_SIZE = 400

            buffer = b""

            disconnect = False
            
            while True:
                data = conn.recv(2048)

                if not data:
                    break
                

                    
                buffer += data
                

                while b"\n" in buffer:
                    
                    message, buffer = buffer.split(b"\n", 1)
                    
                    if len(message) > MAX_MESSAGE_SIZE:
                        
                        print("Message too large!")
                        
                        disconnect = True
                        
                        break
                    
                    print(f"{addr}: {message.decode('utf-8', errors='replace')}")

                    for client in self.clients.copy():
                        if client != conn:
                            try:
                                client.sendall(message + b"\n")
                            except OSError:
                                pass
                if len(buffer) > MAX_MESSAGE_SIZE:
                    print(f"{addr}: Incomplete message too large. Disconnecting.")
                    break
                
                if disconnect:
                    break
                                
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