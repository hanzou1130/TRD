# CS+ Build Instructions

CS+がインストールされている環境でのビルド方法です。

## 方法1: CS+ IDE使用（推奨）

### プロジェクト作成とビルド

1. **CS+を起動**
   ```
   スタートメニュー → Renesas → CS+ for CC
   ```

2. **新規プロジェクト作成**
   - File → Create New Project
   - Target: RH850/F1KM-S1
   - Tool-Chain: CC-RH
   - Project Name: RH850_Startup

3. **ファイル追加**
   - プロジェクトツリーで右クリック → Add Files
   - 追加するファイル:
     ```
     src\startup_rh850f1kms1_csp.asm
     src\main.c
     src\rh850f1kms1_csp.dr (デバイスファイル)
     ```

4. **ビルド実行**
   ```
   Build → Build Project (F7)
   ```

## 方法2: コマンドラインビルド

CS+がインストールされている場合、CC-RHコンパイラも利用可能です。

### CC-RHコンパイラの場所を確認

```powershell
# 一般的なインストールパス
C:\Program Files (x86)\Renesas Electronics\CS+\CC\CC-RH\V2.xx.xx\bin\
```

### 環境変数に追加

```powershell
# 一時的に追加
$env:Path += ";C:\Program Files (x86)\Renesas Electronics\CS+\CC\CC-RH\V2.06.00\bin"

# 確認
ccrh --version
```

### ビルドコマンド

```powershell
# アセンブル
ccrh -c -cpu=g3m ..\src\startup_rh850f1kms1_csp.asm -o startup.obj

# コンパイル
ccrh -c -cpu=g3m -O2 -g ..\src\main.c -o main.obj

# リンク
rlink -device=..\src\rh850f1kms1_csp.dr startup.obj main.obj -output=application.abs
```

## 現在の状況

CS+はインストール済みですが、コマンドラインツールがPATHに設定されていない可能性があります。

### 推奨アクション

**CS+ IDEを使用してビルド:**
1. CS+を起動
2. 上記の手順でプロジェクトを作成
3. F7キーでビルド

これが最も確実で簡単な方法です。

### ビルド成功の確認

ビルドが成功すると、以下のファイルが生成されます:
```
Debug\
├── RH850_Startup.abs    (実行ファイル)
├── RH850_Startup.hex    (Hexファイル)
└── RH850_Startup.map    (マップファイル)
```

## トラブルシューティング

### CS+が見つからない場合

**確認:**
```
スタートメニューで "CS+" を検索
```

**再インストールが必要な場合:**
- Renesas公式サイトからCS+ for CCをダウンロード
- https://www.renesas.com/software-tool/cs

### ビルドエラーが出る場合

**CS_PLUS_QUICKSTART.md** を参照してください。
詳細なトラブルシューティング手順が記載されています。

---

**次のステップ:** CS+ IDEを起動してプロジェクトを作成し、ビルドを実行してください。
