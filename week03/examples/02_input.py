# input()は文字列を返す。整数変換前後の型を観察する。
# 数字以外を入力するとValueErrorになる。03の例と比較する。
text = input("個数（整数）: ")
print(type(text))
count = int(text)
print(type(count))
print("個数:", count)
