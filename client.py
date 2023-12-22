import socket
import threading
import sys

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message, end='\n', flush=True)
        except Exception as e:
            print(f"Hata: {e}")
            break

def main():
    host = 'localhost'
    port = 5555

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    
    username = None

    while not username:
        try:
            
            username = input("Kullanıcı Adınızı Girin: ").strip()
            client_socket.send(username.encode('utf-8'))

            response = client_socket.recv(1024).decode('utf-8')
            print(response, end='\n', flush=True)

            if response.startswith("Bu kullanıcı adı zaten kullanımda."):
                print("Lütfen tekrar bağlanıp yeni kullanıcı adı giriniz.")
                sys.exit()

            print("Kullanıcı adınız başarıyla alındı.")

        except Exception as e:
            print(f"Hata: {e}")
            return

    message_receiver = threading.Thread(target=receive_messages, args=(client_socket,))
    message_receiver.start()

    while True:
        try:
            message = input("")
            if message.lower() == 'q':
                break

            client_socket.send(message.encode('utf-8'))

        except KeyboardInterrupt:
            break

        except EOFError:
            break

        except ConnectionAbortedError:
            print("Bağlantı kesildi. Tekrar bağlanıyor...")
            client_socket.close()

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((host, port))
                print("Yeniden bağlantı başarılı.")
                
                message_receiver = threading.Thread(target=receive_messages, args=(client_socket,))
                message_receiver.start()
            except Exception as e:
                print(f"Bağlantı hatası: {e}")
                break

        except Exception as e:
        
            break

    client_socket.close()

if __name__ == "__main__":
    main()
