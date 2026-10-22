# 第4回 例題3：print() で表示する

print("こんにちは")
print(5)
x = 8
print(x)
print("合計", x)            # カンマで区切ると、空白をはさんで並ぶ → 合計 8
print("合計", x, "円")      # 合計 8 円

print("---")

# 文字列と数は別のもの：同じ + でも意味が変わる
print(5 + 3)          # 8（数と数：足し算）
print("5" + "3")      # 53（文字列と文字列：つなぐ）
# print("5" + 3)      # TypeError（文字列と数は + でつなげない）。# を外して試してみよう

print("---")

# f文字列：" " の前に f をつけ、変数や式を { } で囲むと、文と数を1つにして表示できる
price = 120
count = 3
total = price * count
print(f"合計は {total} 円")             # 合計は 360 円
print(f"{count} 冊で {total} 円")        # 3 冊で 360 円
print(f"{count} 冊で {price * count} 円")  # { } の中は式でもよい
