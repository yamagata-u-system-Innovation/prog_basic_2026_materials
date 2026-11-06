# くり返しの中の変化を表示する（トレース）
total = 0
for i in range(1, 6):
    total = total + i
    print(f"i = {i} のとき total = {total}")
print(f"最後の total は {total}")
