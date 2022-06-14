import pickle
import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ("localhost", 10000)
print("connecting to {} port {}".format(*server_address))
sock.connect(server_address)
l_data = list(range(30000))
# print(len(pickle.dumps(l)))
try:

    # Send data
    message = pickle.dumps(l_data)
    print(len(message))
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)
    # print(f"expected: {amount_expected}")

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print(len(data))
        print("received {!r}".format(data))
    print(f"final {amount_expected}")

finally:
    print("closing socket")
    sock.close()
