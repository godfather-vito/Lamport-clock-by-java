import java.net.*;
import java.util.Scanner;
import java.util.Map;
import java.util.concurrent.locks.ReentrantLock;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

class LamportClock {
    private int clock;
    private ReentrantLock threadLock = new ReentrantLock();
    private static Map<Integer, Integer> PROCESS_PORT = Map.of(
        1, 8080,
        2, 8081,
        3, 8082
    );

    LamportClock() {
        this.clock = 0;
    }

    void receiveThread(int processNumber) {
        int processPort = PROCESS_PORT.get(processNumber);
        try {
            ServerSocket serverSocket = new ServerSocket(processPort);
            while (true) {
                Socket socket = serverSocket.accept();
                DataInputStream input = new DataInputStream(socket.getInputStream());
                int destClock = input.readInt();
                socket.close();
                gotMessage(destClock);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    void calcEvent() {
        threadLock.lock();
        this.clock++;
        System.out.println("時刻" + this.clock + ": 計算イベント");
        threadLock.unlock();
    }

    void gotMessage(int anotherProcessClock) {
        threadLock.lock();
        this.clock = Math.max(anotherProcessClock, this.clock) + 1;
        System.out.println("時刻" + this.clock + ": メッセージを受信");
        threadLock.unlock();
    }

    void sendMessage(int destProcess) {
        int destPort = PROCESS_PORT.get(destProcess);
        try {
            Socket socket = new Socket("127.0.0.1", destPort);
            DataOutputStream output = new DataOutputStream(socket.getOutputStream());
            threadLock.lock();
            this.clock++;
            System.out.println("時刻" + this.clock + ": メッセージを送信");
            output.writeInt(this.clock);
            socket.close();
            threadLock.unlock();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    void showTime() {
        threadLock.lock();
        System.out.println("現在の時刻: " + this.clock);
        threadLock.unlock();
    }

    public static void main(String[] args) {

            int processNumber = Integer.parseInt(args[0]);
            LamportClock lamportClock = new LamportClock();
            Thread receiveThread = new Thread(() -> lamportClock.receiveThread(processNumber));
            Scanner scanner = new Scanner(System.in);
            receiveThread.start();
            while (true) {
                System.out.println("\n=== 時刻" + lamportClock.clock + " ===");
                System.out.println("イベントの種類を決めてください(c: 計算イベント, s: メッセージ送信, t: 現在の時刻を表示): ");
                String cmd = scanner.nextLine();
                switch (cmd) {
                    case "c":
                        lamportClock.calcEvent();
                        break;
                    case "s":
                        System.out.print("プロセスナンバー: ");
                        int processNum = Integer.parseInt(scanner.nextLine());
                        lamportClock.sendMessage(processNum);
                        break;
                    case "t":
                        lamportClock.showTime();
                        break;
                    default:
                        System.out.println("再入力");
                        break;
                }
            }
       
    }
}
