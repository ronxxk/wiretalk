import threading
import socket


import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("CLIENT_HOST", "127.0.0.1")
PORT = int(os.getenv("CLIENT_PORT", 65432))



class Client:
    def __init__(self, host, port, username):
        self.username = username
        self.host = host
        self.port = port
        self.running = True
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_messages(self):
        while True:
            try:
                data = self.s.recv(2048)
                if not data:
                    break
                print(f"\n{data.decode()}")
                print("You: ", end="", flush=True)
            except ConnectionResetError:
                if self.running:
                    print("\nConnection lost.")
                break

            except OSError:
                if self.running:
                    print("\nSocket error.")
                break
            
    def connect(self):
        try:
            with self.s:
                self.s.connect((self.host, self.port))
                self.s.sendall(f"{self.username} joined \n \n".encode("utf-8"))
                
                thread = threading.Thread(target=self.receive_messages, daemon=True)
                
                thread.start()
                try:
                    while True:
                        message = str(input("You: "))
                        if message == "close":
                            self.running = False
                            self.s.sendall(f"{self.username} dissconected \n".encode("utf-8"))
                            break
                        self.s.sendall(f"{self.username}: {message}\n".encode("utf-8"))
                except KeyboardInterrupt:
                    self.s.sendall(f"{self.username} disconnected \n".encode("utf-8"))
                    self.running = False

                    
        except ConnectionResetError:
            print("Connection was reset by the server.")

        except ConnectionRefusedError:
            print("Could not connect. Is the server running?")

        except OSError as e:
            print(f"Connection error: {e}")
                
if __name__ == "__main__":
    name = str(input("Enter Your Username: "))
    
    client = Client(host=HOST, port=PORT, username=name)
    client.connect()
        