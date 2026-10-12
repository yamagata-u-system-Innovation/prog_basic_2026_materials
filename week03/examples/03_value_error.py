# 例外処理を授業で扱う場合の参考例。課題の完成解答ではない。
try:
    count = int(input("個数（整数）: "))
except ValueError:
    print("整数を入力してください")
else:
    if count < 0:
        print("0以上を入力してください")
    else:
        print("受け付けた個数:", count)
