#kekehoさんのコード
import socket#ソケット通信をするためのライブラリ
import threading#並行処理を可能にするライブラリ
import sys#実行時にコマンドライン引数を渡して実行するためのライブラリ
# どのプロセスが、どのポートか示す表

PROCESS_PORT = {

    1: 8080,
    2: 8081,
    3: 8082,
    
}

class LamportClock:
    clock: int#クロックのデータ型のヒント
    thread_lock: threading.Lock#スレッドのロック
    
    def __init__(self) -> None:#戻り値の型ヒント、コンストラクタ
        self.clock = 0  # 変数の初期化
        self.thread_lock = threading.Lock()#インスタンスの作成
    
    def receive_thread(self):#他の並行処理から何か引数とかを受け取るためのメソッド
        process_number = int(sys.argv[1])#コマンドライン引数で、もらったデータを整数型にし、ナンバーに格納している。
        process_port = PROCESS_PORT[process_number]#さっき出てきたプロセスポートリストの、”プロセスナンバーと対応する要素番号の値”を変数に代入

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#ソケットの通信方法を決定している。ipv4でTCPだよ〜
        sock.bind(("127.0.0.1", process_port))#これは使うポートとそれに対するipアドレスを決定している
        sock.listen(10)#通信に使う受け付け窓口のかずを決定している
        while True:#クライアントからの受信を常に待つためのわいる
            dest_sock, _ = sock.accept()#acceptでゲットした値を二つの変数に格納している。また、アドレス情報（IPとポート番号）は不要なため、_に入れている。
            dest_raw_clock = dest_sock.recv(8)  # 受け取った情報を、8byte=64bitで読み込む。そしてそれを宛先クロックのリアルタイムの変数に格納
            dest_clock = int.from_bytes(dest_raw_clock, 'big')#一個上の関数で受け取ったデータを整数型にしてる。bigで統一して解釈することにする。
            dest_sock.close()#受信待ち一旦やめる。
            self.got_message(dest_clock)#ゲットしたメッセージを処理する関数に引数としてdest_clockの値を渡してる。さっき受信したデータの整数型バージョン
    
    def calc_event(self):#計算イベントを行う
        self.thread_lock.acquire()#スレッドロックを取得している
        print(f"時刻{self.clock}: 計算イベント")#f文字列フォーマット→f"文字列 {式}"
        self.clock += 1#論理時計の値をインクリメントしている
        self.thread_lock.release()#スレッドの開放
    
    def got_message(self, another_process_clock: int):#メッセ受信時の挙動
        self.thread_lock.acquire()#スレッドロックを取得
        l = max(self.clock, another_process_clock)#受信したクロックと自分のクロックで大きい方を選び変数に格納する
        self.clock = l + 1#時刻を進める
        print(f"時刻{self.clock}: メッセージを受信")#受信した時刻を表示
        self.thread_lock.release()#スレッドを開放

    def send_message(self, dest_process: int):#メッセ送信時の挙動
        dest_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#通信方式を決めてる
        dest_sock.connect(("127.0.0.1", PROCESS_PORT[dest_process]))#引数で受け取った値に対応するプロセスポートリストの要素を使うポートにしてる
        self.thread_lock.acquire()#スレッドロックの取得し、
        self.clock += 1#自分のクロックをインクリメントしてから
        print(f"時刻{self.clock}: メッセージを送信")#送信時の時刻を表示して
        dest_sock.send(self.clock.to_bytes(8, 'big'))#big方式で受け取ることの表明して送信！
        dest_sock.close()#ソケット閉じて
        self.thread_lock.release()#スレッド開放

def main():#メインの挙動
    lamport_clock = LamportClock()#インスタンスの作成
    clock_receive_thread = threading.Thread(target=lamport_clock.receive_thread)#スレッド使用のためのインスタンス作成
    clock_receive_thread.start()#スレッド使用の開始
    while True:
        print(f"\n=== 時刻{lamport_clock.clock} ===")#時刻を表示
        cmd = input("発生させるイベントを入力 (c: 計算イベント, s: メッセージ送信): ")
        if cmd == "c":
            lamport_clock.calc_event()#計算イベントを呼び出す
        elif cmd == "s":
            process_num = input("プロセスナンバー: ")
            lamport_clock.send_message(int(process_num))#コマンドラインで受け取った引数を整数型にしsend_message()に引数として渡す
        else:
            print("再入力")#c、s以外のデータを受け取った時にもう一度入力させる。
            continue
    
    clock_receive_thread.join()#これはなんだろう？スレッドの受信を終わらせるのかな

if __name__ == "__main__":#再利用性を高めてる→これ書くことで他のモジュールで呼び出す時に変にmain()が実行されたりしない
    main()
