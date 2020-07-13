import socket
from _thread import *
import pickle
from game import Game

server = "localhost"
port = 5555
server_ip = socket.gethostbyname(server)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(4)
print("接続を待っています。サーバを開始します")

connected = set()
games = {}
idCount = 0


def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(1024).decode()

            if gameId in games:
                game = games[gameId]

                if not data:
                    print("Not Data")
                    break
                else:
                    if data == "reset":
                        game.new()
                        print("new")
                    elif data == "tumo":
                        game.tumo(p)
                        print("tumo")
                    elif data == "hantei":
                        game.hantei(p)
                        print("hantei")
                    elif "dahai" in data:
                        game.dahai(p, data)
                        print("dahai")
                    elif data == "next":
                        game.next_turn(p)
                        print("next")
                    elif data == "new_ba":
                        game.new_ba()
                        print("new_ba")

                    print(data)
                    print(game)
                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            print("Fuck")
            break

    print("接続を失いました")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    p = idCount % 4
    idCount += 1

    gameId = (idCount - 1) // 4
    if idCount % 4 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
        games[gameId].ready = True  # deb
    else:
        if idCount % 4 == 0:
            games[gameId].ready = True

    start_new_thread(threaded_client, (conn, p, gameId))