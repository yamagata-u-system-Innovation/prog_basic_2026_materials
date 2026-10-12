# 条件分岐の例。priceを0、9999、10000、-1に変えて比較する。
price = 2500
if price < 0:
    print("0以上を入力してください")
elif price >= 10000:
    print("高額商品です")
else:
    print("通常の商品です")
