# A05：条件分岐のあるプログラム
# この骨組みを「自分で決めた判定」に書きかえる。
# ・input() と int() で値を受け取る
# ・if / elif / else で 3つ以上の道に分ける
# ・結果は f文字列で表示する

score = int(input("点数は？ "))   # 入力：キーボードから受け取り、int() で整数にする

if score >= 80:                   # 処理：上から順に条件を調べる
    rank = "A"
elif score >= 60:
    rank = "B"
else:
    rank = "C"

print(f"{score} 点は {rank} です")  # 出力：f文字列で1回だけ表示する
