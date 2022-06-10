import math
import pickle
import socket

# Create a TCP/IP socket
hw = 80
lw = 13
r = 0.1
cwnd_initial = 16

# This is for TCP
def increase_cwnd(cwnd):
    result = cwnd + (1 / cwnd)
    return result


def decrease_cwnd(cwnd):
    cwnd = cwnd / 2
    sst = cwnd
    return (cwnd, sst)


def timeout(cwnd):
    sst = max((cwnd / 2), cwnd_initial)
    cwnd = cwnd_initial
    return (cwnd, sst)


# This is for HSTCP
def increase_cwnd_hs(cwnd):
    g_beta = decrease_cwnd_hs(cwnd)
    numerator = pow(cwnd, 2) * (0.078 / 1.2) * 2 * (g_beta / (2 - g_beta)) + 0.5
    return numerator


def decrease_cwnd_hs(cwnd):
    result = (r - 0.5) * (
        ((math.log10(cwnd)) - (math.log10(lw))) / ((math.log10(hw)) - (math.log10(lw)))
    ) + 0.5
    return result


def loss_hs(cwnd):
    cwnd = (1 - decrease_cwnd_hs(cwnd)) * cwnd
    sst = cwnd
    return (cwnd, sst)


def timeout_hs(cwnd):
    cwnd = (1 - decrease_cwnd_hs(cwnd)) * cwnd
    sst = max(cwnd, cwnd_initial)
    cwnd = cwnd_initial
    return (cwnd, sst)


def main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ("localhost", 10000)
    print("starting up on {} port {}".format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)
    amount_rec = 0
    while True:
        # Wait for a connection
        print("waiting for a connection")
        connection, client_address = sock.accept()
        try:
            print("connection from", client_address)
            # Receive the data in small chunks and retransmit it
            cwnd = cwnd_initial
            while True:
                data = connection.recv(cwnd)
                # print(len(data))
                # print("received {!r}".format(pickle.dumps(data)))
                if data:
                    amount_rec += len(data)
                    # print("received {}".format(pickle.dumps(data)))
                    print(len(data))
                    print("sending data back to the client")
                    connection.sendall(pickle.dumps(data))
                else:
                    print("no data from", client_address)
                    break
        finally:
            # Clean up the connection
            print(f"final: {amount_rec}")
            connection.close()


if __name__ == "__main__":
    main()
