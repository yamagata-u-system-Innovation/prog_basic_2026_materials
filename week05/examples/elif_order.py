# elif の順番に注意：先に 60 以上を調べると、90 でも B になってしまう
score = 90
if score >= 60:
    print("B")
elif score >= 80:
    print("A")      # この行はどんな点数でも実行されない
else:
    print("C")
