# elif：3つ以上に分ける（上から順に調べ、最初に True になった1つだけ実行）
score = 75
if score >= 80:
    print("A")
elif score >= 60:
    print("B")
else:
    print("C")
