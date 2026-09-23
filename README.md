# tabilog

EXIF付きの写真から旅の道程を復元し、しおり（PDF）にするプロトタイプ。

```
python3 -m http.server 8000   # → http://localhost:8000
```

file:// で直接開くとタイル配信元に弾かれることがあるので http 経由で。

## できること

- 写真を複数選択 → GPS + 撮影日時を読んで時系列に並べ、地図にルート描画
- 地図クリックで手動ピン追加（写真のない場所の補完用）
- タイトル・まえがき・各スポットのメモを記入（localStorage に保存）
- 「しおりにする」で A4 実寸のレイアウトに切替 → 「PDFにする」で出力
  - 表紙（☆で選んだ写真を全面）/ 道程＋総括 / 1日1ページ
- テーマ色は編集モードの色ピッカーで変更

## テストデータ

`local-data/` の写真に辻褄の合う旅程の EXIF を焼き込む（gitignore 対象）:

```
python3 tools/stamp-exif.py
```

ファイル名昇順に `tools/stamp-exif.py` の `ROUTE` を割り当てる。写真を入れ替えたら再実行。

## 動作確認

`http://localhost:8000/?selftest` を開いて console。
