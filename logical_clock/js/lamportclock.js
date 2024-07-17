const net = require('net');
const readline = require('readline');
const { Mutex } = require('async-mutex');

const PROCESS_PORT = {//OK
    1: 8080,
    2: 8081,
    3: 8082,
};

class LamportClock {//OK
    constructor() {
        this.clock = 0;
        this.mutex = new Mutex();
    }

    async receiveThread(processNumber) {//非同期関数として定義
        const processPort = PROCESS_PORT[processNumber];

        const server = net.createServer(async (socket) => {
            const destRawClock = await this.receiveMessage(socket);
            const destClock = parseInt(destRawClock, 10);
            await this.gotMessage(destClock);
        });

        server.listen(processPort, '127.0.0.1');
    }

    async receiveMessage(socket) {
        return new Promise((resolve) => {
            socket.on('data', (data) => {
                resolve(data.toString());
                socket.destroy();
            });
        });
    }

    async calcEvent() {
        const release = await this.mutex.acquire();//ロック取得
        try {
            console.log(`時刻${this.clock}: 計算イベント`);
            this.clock += 1;
        } finally {
            release();
        }
    }

    async gotMessage(anotherProcessClock) {
        const release = await this.mutex.acquire();
        try {
            const l = Math.max(this.clock, anotherProcessClock);
            this.clock = l + 1;
            console.log(`時刻${this.clock}: メッセージを受信`);
        } finally {
            release();
        }
    }

    async sendMessage(destProcess) {
        const destPort = PROCESS_PORT[destProcess];
        const client = new net.Socket();
        const release = await this.mutex.acquire();
        try {
            this.clock += 1;
            console.log(`時刻${this.clock}: メッセージを送信`);
            client.connect(destPort, '127.0.0.1', () => {
                client.write(this.clock.toString());
                client.destroy();
            });
        } finally {
            release();
        }
    }

    async showTime() {
        const release = await this.mutex.acquire();
        try {
            console.log(`現在の時刻: ${this.clock}`);
        } finally {
            release();
        }
    }
}

const main = async () => {
    const processNumber = parseInt(process.argv[2], 10);
    if (!PROCESS_PORT[processNumber]) {
        console.error('プロセスナンバーが割り当てられていません。');
        process.exit(1);
    }

    const lamportClock = new LamportClock();
    lamportClock.receiveThread(processNumber);

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const prompt = () => {
        rl.question(`\n=== 時刻${lamportClock.clock} ===\n発生させるイベントを入力 (c: 計算イベント, s: メッセージ送信, t: 現在の時刻を表示): `, async (cmd) => {
            if (cmd === 'c') {
                await lamportClock.calcEvent();
            } else if (cmd === 's') {
                rl.question('プロセスナンバー: ', async (processNum) => {
                    await lamportClock.sendMessage(parseInt(processNum, 10));
                });
            } else if (cmd === 't') {
                await lamportClock.showTime();
            } else {
                console.log('再入力');
            }
            prompt();
        });
    };

    prompt();
};

main();
