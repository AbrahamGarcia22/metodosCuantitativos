import math
import pickle
import random
import socket

import matplotlib.pyplot as plt

# Create a TCP/IP socket
hw = 2000
lw = 60
r = 0.1
cwnd_initial = 16
PROBS = [0, 0, 0, 0, 1, 0, 0, 0, 1]
# TIMES = list(range(0, 50))  # Used to determine is there was a timeout
# This is for TCP
def increase_cwnd(cwnd):
    # This part was modified from original method to produce significant change
    cwnd += cwnd * 0.2
    return cwnd


def decrease_cwnd(cwnd):
    cwnd = cwnd / 2
    sst = cwnd
    return (max(cwnd, 1), sst)


def timeout(cwnd):
    sst = max((cwnd / 2), cwnd_initial)
    cwnd = cwnd_initial
    return (cwnd, sst)


# This is for HSTCP
def increase_cwnd_hs(cwnd):
    g_beta = decrease_cwnd_hs(cwnd)
    f_alpha = pow(cwnd, 2) * (0.078 / 1.2) * 2 * (g_beta / (2 - g_beta)) + 0.5
    cwnd += f_alpha / cwnd
    return cwnd


def decrease_cwnd_hs(cwnd):
    result = (r - 0.5) * (
        ((math.log10(cwnd)) - (math.log10(lw))) / ((math.log10(hw)) - (math.log10(lw)))
    ) + 0.5
    return result


def loss_hs(cwnd):
    cwnd = (1 - decrease_cwnd_hs(cwnd)) * cwnd
    sst = cwnd
    cwnd = max(cwnd, cwnd_initial)
    return (cwnd, sst)


def timeout_hs(cwnd):
    cwnd = (1 - decrease_cwnd_hs(cwnd)) * cwnd
    sst = max(cwnd, cwnd_initial)
    cwnd = cwnd_initial
    return (cwnd, sst)


def plot_cwnd(results: list):
    fig, ax = plt.subplots(figsize=(50, 10))
    ax.plot(results)
    plt.title("HSTCP Behavior")
    plt.ylabel("Congestion Window")
    plt.xlabel("Packets received")
    # Guardar el gráfico en formato png
    plt.savefig("graphic_result.png")
    plt.cla()
    plt.clf()


def get_new_cwnd(cwnd, sst):
    loss = random.choice(PROBS)
    time = random.choice(PROBS)
    if cwnd < lw:
        if time:
            cwnd, sst = timeout(cwnd)
            print("Timeout")
        elif loss:
            print("Packet Loss")
            cwnd, sst = decrease_cwnd(cwnd)
        else:
            cwnd = increase_cwnd(cwnd)
    else:
        if time:
            print("Timeout")
            cwnd, sst = timeout_hs(cwnd)
        elif loss:
            print("Packet Loss")
            cwnd, sst = loss_hs(cwnd)
        else:
            cwnd = increase_cwnd_hs(cwnd)
    print(f"New cwnd:{cwnd}, New sst:{sst}")
    return cwnd, sst


def main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ("localhost", 10000)
    print("starting up on {} port {}".format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)
    amount_rec = 0
    cwnds = [0, cwnd_initial]
    sst = cwnd_initial
    while True:
        # Wait for a connection
        print("waiting for a connection")
        connection, client_address = sock.accept()
        try:
            print("connection from", client_address)
            # Receive the data in small chunks and retransmit it
            cwnd = cwnd_initial
            print(cwnd)
            while True:
                data = connection.recv(int(cwnd))
                cwnd, sst = get_new_cwnd(cwnd, sst)
                cwnds.append(cwnd)
                # print(len(data))
                # print("received {!r}".format(pickle.dumps(data)))
                if data:
                    amount_rec += len(data)
                    # print("received {}".format(pickle.dumps(data)))
                    # print("sending data back to the client")
                    connection.sendall(pickle.dumps(data))
                else:
                    print("no data from", client_address)
                    break
        except socket.error:
            print("Connection closed by client")
        finally:
            # Clean up the connection
            plot_cwnd(cwnds)
            print(f"final: {amount_rec}")
            connection.close()


if __name__ == "__main__":
    main()
