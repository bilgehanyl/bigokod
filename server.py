import socket
import threading

clients = {}
channels = {}

def broadcast(message, sender_username, channel_name):
    for username, client_socket in channels[channel_name].items():
        if username != sender_username:
            try:
                client_socket.send(f"{sender_username}: {message}".encode('utf-8'))
            except Exception as e:
                print(f"Hata: {e}")
                remove_client(username, channel_name)

def send_private_message(message, sender_username, recipient_username):
    try:
        recipient_socket = clients[recipient_username]
        recipient_socket.send(f"(Özel) {sender_username}: {message}".encode('utf-8'))
    except KeyError:
        print(f"{recipient_username} bulunamadı. Mesaj gönderilemedi.")

def create_channel(sender_username, recipient_username):
    channel_name = f"{sender_username}-{recipient_username}"
    channels[channel_name] = {}
    return channel_name

def send_channel_invitation(sender_username, recipient_username):
    recipient_socket = clients[recipient_username]
    try:
        recipient_socket.send(f"{sender_username} sizi özel kanala davet ediyor. Katılmak ister misiniz? (Evet/Hayır): ".encode('utf-8'))
    except Exception as e:
        print(f"Hata: {e}")

def join_channel(username, channel_name):
    try:
        user_socket = clients[username]
        user_socket.send(f"Özel kanala katıldınız: {channel_name}".encode('utf-8'))
        channels[channel_name][username] = user_socket  # Kanala katılan kullanıcıyı ekleyin
        print(f"{username} kanala katıldı: {channel_name}")
    except KeyError:
        print(f"{username} bulunamadı. Kanala katılım sağlanamadı.")

    # Ekstra bir kontrol
    if channel_name in channels and username in channels[channel_name]:
        print(f"Aktif kanal üyeleri: {channels[channel_name]}")



def remove_client(username, channel_name):
    if channel_name and username in channels.get(channel_name, {}):
        del channels[channel_name][username]
        print(f"{username} sohbetten ayrıldı.")


def handle_client(client_socket, username):
    if username in clients:
        client_socket.send("Bu kullanıcı adı zaten kullanımda.".encode('utf-8'))
        # Bağlantıyı kapatma
        return

    clients[username] = client_socket
    print(f"{username} sohbete katıldı!")

    client_socket.send(f"Merhaba {username}! Sohbete hoş geldin!".encode('utf-8'))

    sender_username = None
    channel_name = None

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            print(f"{username}: {message}")

            log_message = f"{username}: {message}"
            with open('C:/Pythonkod/log.txt', 'a') as log_file:
                log_file.write(log_message + "\n")

            if message.startswith("/invite "):
                _, recipient = message.split(" ", 1)
                sender_username = username
                channel_name = create_channel(sender_username, recipient)
                send_channel_invitation(sender_username, recipient)
            elif message.lower() == "evet":
                join_channel(username, channel_name)
            elif channel_name and username in channels[channel_name]:
                send_channel_message(message, username, channel_name)
            else:
                broadcast(message, username, channel_name)

        except Exception as e:
            print(f"Hata: {e}")
            break

    remove_client(username, channel_name)

def send_channel_message(message, sender_username, channel_name):
    for username, client_socket in channels[channel_name].items():
        if username != sender_username:
            try:
                client_socket.send(f"{sender_username}: {message}".encode('utf-8'))
            except Exception as e:
                print(f"Hata: {e}")
                remove_client(username, channel_name)

def main():
    host = 'localhost'
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server dinleniyor {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Bağlantı kabul edildi: {addr}")

        username = client_socket.recv(1024).decode('utf-8')

        client_handler = threading.Thread(target=handle_client, args=(client_socket, username))
        client_handler.start()

if __name__ == "__main__":
    main()
