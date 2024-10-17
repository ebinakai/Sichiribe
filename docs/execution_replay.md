# REPLAY Execution

7セグメント表示器を撮影した動画から表示内容を解析するには `replay.py` を実行する。  
パラメータを設定することができ、実行時に指定できる。実行例を以下に示す。

```bash
# 一番シンプルな例
python3 replay.py test/sample.mp4  

# 諸項目を設定する場合
python3 replay.py test/sample.mp4 --num-digits 4 --sampling-sec 5 --num-frames 30 --skip-sec 0 --format csv --save-frame --debug
```

## Arguments of replay.py

動画のパス以外はオプションなので、含めずに実行することも可能である。

| 引数 | 説明 |  
| --- | --- |  
| test/sample.mp4 | 解析する動画のパス |  
| --num-digits 4 | 7セグメント表示器の桁数 |
| --sampling-sec 5 | 動画をサンプリングする頻度 |  
| --num-frames 30 | 一回のサンプリングで何フレーム取得するか |  
| --skip-sec 0 | 動画の解析を始めるタイミング |  
| --format csv | 出力形式 (json または csv) |
| --save-frame | キャプチャしたフレームを保存するか（保存しない場合、メモリの使用量が増加します） |
| --debug | ログをデバッグモードにする場合は含める |

## Process Flow Configuration of replay.py

1. 指定された引数を元に設定を適用
2. カメラ画角の確認
3. 7セグメント表示器が写っている部分をクロップする
   1. クロップ部分を選択後、確認のウィンドウが立ち上がるが小さい場合があるので注意
   2. 確認ウィンドウがアクティブな状態で y/n のどちらかを押下する
4. クロップした部分を解析して表示内容を読み取る
   1. 設定された頻度でサンプリングを行う
   2. 設定された解析時間を超えた場合にサンプリングを終了
5. 読み取った内容を外部ファイル等に出力する