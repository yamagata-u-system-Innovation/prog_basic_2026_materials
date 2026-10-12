# A03 配布準備・教員用手順（2026-10-12）

## 確認結果と未確定事項

| 項目 | 根拠・対応 |
| --- | --- |
| 公開教材 | mainにREADMEとweek02のみ。week03は存在しない |
| 提出テンプレート | mainにweek02、Python 3.13の形式チェック、年間提出方式のREADME。week03は存在しない |
| 第2回A02 | 10/9配布、10/15 23:59締切、profile.mdとhello.py、2点 |
| 第3回の実際の授業内容 | 現行GitHubにスライド・シラバス・第3回計画がなく確認できない。A02から到達度も判断できない |
| 第3回授業日・締切・配点 | 未確定。A02や前年度の日付・点数から推定しない |
| 前年度README | 価格、整数変換、条件分岐、ValueError、税率10%。小数・税率入力・再入力は任意 |
| 前年度Python | calc_tax_price.pyはfloat・税率入力・isdigit検証でtry/except未使用。READMEと一致しない |
| 2026対応 | 年間非公開リポジトリのweek03内で作業。新規週別repo・Issue提出報告を廃止。answer.mdにAI申告 |

教材案の「通常の商品です」は分岐を観察しやすくするための追加候補です。
負数や変換失敗で税込計算をしない仕様を明示しました。例題は独立した短い例で、完成解答は含みません。
Python雛形は構文的に実行可能ですが未実装です。既存Actionsの合格表示は正答や提出完了の証明にはなりません。

参照（確認時点のmain）:

- https://github.com/yamagata-u-system-Innovation/prog_basic_2026_materials/tree/88fa903d8d0bec0e4386dbd380a127aabe7ef809
- https://github.com/yamagata-u-system-Innovation/prog_basic_2026_template/tree/4e2853fb3e18a32c45189cce8a46b14aa2c2e07f
- https://github.com/yamagata-u-system-Innovation/prog_basic_2025_week3/blob/e21cd0dea270a6d9422d9f69fae413bbf7c05a9f/README.md
- https://github.com/yamagata-u-system-Innovation/prog_basic_2025_week3/blob/e21cd0dea270a6d9422d9f69fae413bbf7c05a9f/calc_tax_price.py

## 公開教材・テンプレートの配置

この段階はDraft PRでレビューするための準備です。未確定案のままmainへマージしません。
公開教材のweek03にはTASK.md、price_check.py、answer.mdとexamples/を置きます。
テンプレートには同じ3ファイルだけを置きます。例題は公開教材を参照します。
admin/a03/は教員用ツールです。学生へ配布しません。

1. 第3回のスライド／授業計画とA02の実施状況を照合し、条件分岐・入力検証・例外処理の必修範囲を確定する。
   例外処理を扱わない場合、TASK、雛形、動作確認表、例題03の掲載を合わせて編集する。
2. 授業日、締切（日本時間）、配点、評価基準を記入する。
   TASKの準備中の注意書き、未確定表記と全角［...］欄を除去し、見出しを確定版に変更する。
3. 両PRのTASK、price_check.py、answer.mdを同じバイト内容にする。
4. 公開教材READMEの回一覧に、確定した日付とweek03リンクを追加する。
   現在は案であり、学生が確定課題と誤認する案内をmainに追加していない。
5. PR差分でweek02・既存README・.github・feedbackに意図しない変更がないか確認する。
   採点用テストや解答例は公開教材に含めない。自己確認Actionsを採点と説明しない。
6. Python 3.13で雛形と例題を実行し、確定した期待結果を確認する。
7. レビュー後に両PRをマージ。公開教材mainの確定commit SHAを記録し、その版を配布元に固定する。

テンプレート更新は、以後に作成するリポジトリに反映されます。
既に作成済みの学生リポジトリには自動反映されません。以下の一括追加が必要です。

## 一括配布の前提

教員のPCでPython 3.13、Git、GitHub CLI（gh）を使用します。
`gh auth status`で認証、`gh auth setup-git`でGit認証を設定してください。
`git config user.name`、`git config user.email`が教員として設定されていることも確認します。
認証トークンはソース・名簿・ログに書きません。

対象一覧は実際の履修者とリポジトリ・教員アクセス権を照合して作成します。
自動検索で取得した全repoをそのまま対象にせず、学籍番号と履修者の一致を確認してください。
`targets.txt`にはowner/repoを1行ずつ記入します。
対象名は現在のREADMEに合わせて組織配下の `prog_basic_2026_数字` に限定しています。
組織外にある場合や別の命名方式の場合は、実際の運用を確認して制約をレビューしてから変更します。

targets.txt、plan.json、results.json、一時cloneは教員専用の作業フォルダで管理し、公開GitHubへ追加しません。
学生情報を含まない配布ツールとこの手順だけが公開対象です。
実際の対象一覧・授業内容が確定していないため、この準備では学生repoへアクセス・配布していません。

## ドライランと差分確認

確定・マージ済み教材をcloneし、記録したcommit SHAをcheckoutします。
以下はそのcloneの直下で実行するコマンドです。教員専用の作業フォルダを別途作成してください。
パス例では `../a03-private/` をそのフォルダとしています。

```powershell
python admin/a03/distribute.py plan --source week03 --roster ../a03-private/targets.txt --out ../a03-private/plan.json
```

planはGitHubの読み取りのみです。commitやpushを行いません。
未確定TASKは読み取りを始める前に拒否されます。
plan.jsonに各対象のdefault branch、head SHA、3ファイルのGit blob SHA、状態を記録します。

| 状態 | 意味 |
| --- | --- |
| ADD | week03がない。3ファイルを新規追加する予定 |
| ALREADY | 3ファイルだけが存在し、内容・通常ファイルmodeが完全一致。追加しない |
| BLOCKED | week03に既存の編集、追加ファイル、symlink等がある、公開repo、権限不足など。全体のapplyを拒否 |

対象数、repo名、ADD/ALREADY/BLOCKED、追加3ファイルの内容を確認してください。
初回は教員管理のテスト用非公開repo、次に少数の対象、最後に残りへ分けてplanします。
テスト用repoも命名制約を満たすものを別名簿に記入します。履修者と混ぜません。
既存week03が学生によって編集されている場合は、削除・上書きして配布を通してはいけません。
個別に状況を確認し、新規修正案内ファイルの追加などを別途レビューします。

## 配布

```powershell
python admin/a03/distribute.py apply --source week03 --roster ../a03-private/targets.txt --plan ../a03-private/plan.json --out ../a03-private/results.json
```

applyはplanと教材・対象一覧の完全一致を確認し、全対象のheadを再検証してから開始します。
各repoを一時cloneし、確認したheadを親に、3ファイルだけを新規追加するcommitを作ります。
Git属性や改行変換で内容が変わった場合も、blob SHAの照合で停止します。
commitメッセージは既存Actionsの仕様に合わせた `A03を配布` です。
通常pushのみを使い、force push、履歴上書き、学生変更の自動rebase、削除はしません。
push直前の再検証とnon-fast-forward拒否により、学生の並行更新があれば停止します。
失敗時は次のrepoへ進まず、配布済みの結果を残します。全体を跨ぐトランザクションではありません。

## 配布後検証・失敗時

results.jsonに配布前head、作成commit、結果が残ります。
配布commitの全treeを比較し、3ファイルの追加以外に変更がないことを検証します。

- VERIFIED：配布commitと現在headが一致し、全treeが期待通り。
- VERIFIED_HEAD_ADVANCED：配布commitの内容は検証済み。その後の学生更新は別途確認する。
- PUSHED_VERIFY_PENDING：pushは成功したが、通信失敗等で検証未完了。記録commitをGitHubで確認する。
- FAILED_OR_UNKNOWN：push前の失敗、または通信切断で成功不明の可能性。自動再実行しない。
- ALREADY：同一教材が存在し、新たなcommitを作成しない。

GitHubで記録commitがdefault branchに到達しているか、変更が3ファイルの追加だけか確認します。
学生が更新済みなら、そのcommitを保護したまま課題受領を確認します。
学生に同期後のweek03表示、雛形起動、提出後のGitHub上の更新を確認してもらいます。
全対象の完了数と名簿を照合し、未配布を残さないでください。
通信失敗や学生更新があった場合は、記録とGitHubを確認して新しいplan名で再planします。
同一教材の再配布はALREADYとなり、学生が編集済みならBLOCKEDとなります。
一括配布後の誤り訂正は、この新規追加専用ツールで強行しません。学生ファイルを保護する別手順で対応します。

## 検証範囲

ローカル自動テストは未確定教材の配布拒否、既存ファイル保護、plan不一致、公開repo拒否、
追加差分とtree検証、通常pushで並行更新を拒否することを対象とします。
実GitHubへの一括配布ドライラン・本配布は、確定教材と実対象一覧がそろってから実施します。

今回の実行環境はPython 3.12.14で、7件のテストが成功しました。
授業環境Python 3.13での確認は未実施です。配布前に同じテストを実行してください。

```powershell
python --version
python admin/a03/test_distribute.py
```
