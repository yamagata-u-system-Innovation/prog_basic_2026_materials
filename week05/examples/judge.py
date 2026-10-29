# input と if を組み合わせる：実行するたびに違う値を入れて、違う道を通る
score = int(input("点数は？ "))
if score >= 80:
    rank = "A"
elif score >= 60:
    rank = "B"
else:
    rank = "C"
print(f"{score} 点は {rank} です")
