# input と for を組み合わせる：A06 の骨組み

n = int(input("いくつまで？ "))   # 入力：キーボードから受け取り、int() で整数にする

count = 0                        # 個数の箱。くり返しの前に 0 にしておく
total = 0                        # 合計の箱。くり返しの前に 0 にしておく

for i in range(1, n + 1):        # 処理：i に 1, 2, …, n が順に入る
    if i % 2 == 0:               # 条件に合うとき（偶数のとき）だけ
        count = count + 1        # 個数を 1 増やす
        total = total + i        # 合計に i を足す

print(f"偶数は {count} 個、合計 {total}")  # 出力：f文字列で1回だけ表示する
