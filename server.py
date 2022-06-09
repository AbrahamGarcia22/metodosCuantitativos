import pickle
import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ("localhost", 10000)
print("starting up on {} port {}".format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
final = pickle.dumps("")
while True:
    # Wait for a connection
    print("waiting for a connection")
    connection, client_address = sock.accept()
    try:
        print("connection from", client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            # print("received {!r}".format(pickle.dumps(data)))
            if data:
                print("received {}".format(pickle.dumps(data)))
                print("sending data back to the client")
                final += data
                connection.sendall(pickle.dumps(data))
            else:
                print("no data from", client_address)
                break

    finally:
        # Clean up the connection
        print(f"hello {pickle.loads(final)}")
        connection.close()
