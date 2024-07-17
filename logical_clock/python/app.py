from flask import Flask, render_template
from flask_socketio import SocketIO
import random
import time
from threading import Thread
from queue import Queue

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)

class Node:
    def __init__(self, node_id, queue):
        self.node_id = node_id
        self.clock = 0
        self.queue = queue

    def send_message(self, recipient_queue, recipient_id):
        self.clock += 1
        timestamp = time.time()
        recipient_queue.put((self.node_id, self.clock, timestamp))
        socketio.emit('message_send', {
            'sender': self.node_id, 
            'recipient': recipient_id, 
            'clock': self.clock,
            'timestamp': timestamp
        })

    def receive_message(self):
        if not self.queue.empty():
            sender_id, sender_clock, sender_timestamp = self.queue.get()
            self.clock = max(self.clock, sender_clock) + 1
            socketio.emit('clock_update', {
                'node': self.node_id, 
                'clock': self.clock,
                'timestamp': sender_timestamp
            })
        else:
            self.clock += 1

    def general_event(self):
        self.clock += 1

    def run(self):
        while True:
            event = random.choice(["general", "send"])
            if event == "general":
                self.general_event()
            else:
                recipient_id = random.choice([i for i in range(3) if i != self.node_id])
                recipient_queue = node_queues[recipient_id]
                self.send_message(recipient_queue, recipient_id)
            time.sleep(1)
            socketio.emit('clock_update', {
                'node': self.node_id, 
                'clock': self.clock,
                'timestamp': time.time()
            })

node_queues = [Queue() for _ in range(3)]
nodes = [Node(i, node_queues[i]) for i in range(3)]
threads = [Thread(target=node.run) for node in nodes]

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    for thread in threads:
        thread.start()
    socketio.run(app, host='0.0.0.0', port=3000)
