# fileviewer

シンプルなファイルブラウザ。Markdown プレビュー・画像表示・削除・軽量化がキーボードだけで完結。

## 機能

- `.md` ファイルのプレビュー（marked.js）
- 画像プレビュー（jpg/png/gif/webp/svg）
- ソート：フルパス / ファイル名 / 更新日 / 作成日 / サイズ / mime
- 同一サイズファイルに `dup?` バッジ表示
- サイドバー幅ドラッグ調整
- 画像の JPEG 軽量化（quality 85）

## キーボードショートカット

| キー | 動作 |
|------|------|
| `↑` / `↓` | リスト移動 |
| `Enter` | ファイルを開く |
| `/` | 検索ボックスにフォーカス |
| `d` | 削除（confirm あり） |
| `c` | 軽量化（画像のみ） |

## セットアップ

```bash
pip3 install flask pillow
python3 app.py
```

`SEARCH_ROOTS` に検索対象ディレクトリを設定してください（デフォルト: `/home/alice`, `/home/ec2-user`）。
