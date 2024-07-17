import socket
import threading
import sys

PROCESS_PORT = {
    1: 8080,
    2: 8081,
    3: 8082,
}

class LamportClock:
    clock: int
    thread_lock: threading.Lock
    
    def __init__(self) -> None:
        self.clock = 0
        self.thread_lock = threading.Lock()
    
    def receive_thread(self):
        process_number = int(sys.argv[1])
        process_port = PROCESS_PORT[process_number]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", process_port))
        sock.listen(10)
        while True:
            dest_sock, _ = sock.accept()
            dest_raw_clock = dest_sock.recv(8)
            dest_clock = int.from_bytes(dest_raw_clock, 'big')
            dest_sock.close()
            self.got_message(dest_clock)
    
    def calc_event(self):
        self.thread_lock.acquire()
        print(f"時刻{self.clock}: 計算イベント")
        self.clock += 1
        self.thread_lock.release()
    
    def got_message(self, another_process_clock: int):
        self.thread_lock.acquire()
        l = max(self.clock, another_process_clock)
        self.clock = l + 1
        print(f"時刻{self.clock}: メッセージを受信")
        self.thread_lock.release()

    def send_message(self, dest_process: int):
        dest_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest_sock.connect(("127.0.0.1", PROCESS_PORT[dest_process]))
        self.thread_lock.acquire()
        self.clock += 1
        print(f"時刻{self.clock}: メッセージを送信")
        dest_sock.send(self.clock.to_bytes(8, 'big'))
        dest_sock.close()
        self.thread_lock.release()

    def show_time(self):
        self.thread_lock.acquire()
        print(f"現在の時刻: {self.clock}")
        self.thread_lock.release()

def main():
    lamport_clock = LamportClock()
    clock_receive_thread = threading.Thread(target=lamport_clock.receive_thread)
    clock_receive_thread.start()
    while True:
        print(f"\n=== 時刻{lamport_clock.clock} ===")
        cmd = input("発生させるイベントを入力 (c: 計算イベント, s: メッセージ送信, t: 現在の時刻を表示): ")
        if cmd == "c":
            lamport_clock.calc_event()
        elif cmd == "s":
            process_num = input("プロセスナンバー: ")
            lamport_clock.send_message(int(process_num))
        elif cmd == "t":
            lamport_clock.show_time()
        else:
            print("再入力")
            continue
    


if __name__ == "__main__":
    main()
