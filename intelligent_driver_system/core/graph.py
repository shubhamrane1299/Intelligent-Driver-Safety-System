import matplotlib.pyplot as plt

states = []

def update_graph(state):
    states.append(state)

def show_graph():
    plt.plot(states)
    plt.title("Fatigue Level")
    plt.show()