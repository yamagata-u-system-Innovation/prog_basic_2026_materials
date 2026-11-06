# 1〜20 のうち 3 の倍数の個数と合計
count = 0
total = 0
for i in range(1, 21):
    if i % 3 == 0:
        count = count + 1
        total = total + i
print(f"3 の倍数は {count} 個、合計 {total}")
