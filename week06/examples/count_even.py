# 1〜10 のうち偶数を数える：for の中に if
count = 0
for i in range(1, 11):
    if i % 2 == 0:
        count = count + 1
print(f"偶数は {count} 個")
