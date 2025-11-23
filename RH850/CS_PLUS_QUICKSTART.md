# CS+ プロジェクトセットアップガイド

CS+がインストール済みの環境で、RH850F1KMS-1スタートアップコードを使用する手順です。

## クイックスタート

### 1. CS+を起動

```
スタートメニュー → Renesas → CS+ → CS+ for CC
```

### 2. 新規プロジェクト作成

1. **File → Create New Project**
2. **プロジェクト設定:**
   - **Project Type**: Application
   - **Target Device**: RH850 → F1KM → RH850/F1KM-S1
   - **Tool-Chain**: CC-RH (Renesas C Compiler)
   - **Project Name**: RH850_Startup_Demo
   - **Location**: `C:\Users\baoma\TRD\RH850\CS_Project`

3. **Finish**をクリック

### 3. ファイルをプロジェクトに追加

**プロジェクトツリーで右クリック → Add → Add Files to Project:**

#### 必須ファイル:
```
✓ C:\Users\baoma\TRD\RH850\src\startup_rh850f1kms1_csp.asm
✓ C:\Users\baoma\TRD\RH850\src\main.c
```

#### デバイスファイル:
```
✓ C:\Users\baoma\TRD\RH850\src\rh850f1kms1_csp.dr
```

### 4. デバイスファイル設定

**方法1: プロジェクト設定から**
1. プロジェクト名を右クリック → **Properties**
2. **Link Options** → **Device File** タブ
3. **Browse** → `rh850f1kms1_csp.dr` を選択
4. **OK**

**方法2: プロジェクトフォルダに配置**
- `rh850f1kms1_csp.dr` をプロジェクトフォルダにコピー
- CS+が自動的に認識

### 5. ビルド設定（オプション）

**プロジェクト → Properties → Compile Options:**

- **Optimization**: `-O2` (Speed)
- **Debug Information**: `-g` (Full)
- **Warning Level**: `-Wall` (All warnings)

### 6. ビルド実行

```
Build → Build Project (F7)
または
Build → Rebuild All (Shift + F7)
```

**出力確認:**
```
Output Window に "Build Finished" と表示
Debug\RH850_Startup_Demo.abs ファイルが生成
```

## デバッグ実行

### デバッガ接続

1. **Debug → Download** (F3)
2. **デバッガ選択:**
   - E2エミュレータ
   - E1エミュレータ
   - E20エミュレータ
   - シミュレータ（実機なしでテスト可能）

### ブレークポイント設定

**startup_rh850f1kms1_csp.asm を開く:**
1. `_RESET:` の行をダブルクリック → ブレークポイント設定
2. `jarl _main, lp` の行にもブレークポイント

**main.c を開く:**
1. `main()` 関数の最初の行にブレークポイント

### 実行

```
F5  - Go (実行)
F10 - Step Over (ステップオーバー)
F11 - Step Into (ステップイン)
F6  - Reset Go (リセット後実行)
```

### メモリ確認

**BSS/DATAセクションの初期化確認:**

1. **View → Memory**
2. アドレス入力:
   - BSS開始: `0xFEBD0000`
   - DATA開始: 確認したいアドレス

3. ブレークポイントで停止後、メモリがゼロクリアされているか確認

## トラブルシューティング

### ビルドエラー: "Cannot find device file"

**解決方法:**
1. `rh850f1kms1_csp.dr` がプロジェクトに追加されているか確認
2. Link Options → Device File で正しく指定されているか確認

### ビルドエラー: "Undefined symbol '__stkend'"

**原因:** デバイスファイルが正しく読み込まれていない

**解決方法:**
1. プロジェクトをクリーン: **Build → Clean**
2. デバイスファイルを再設定
3. リビルド: **Build → Rebuild All**

### ビルドエラー: "Section '.intvect' not found"

**原因:** スタートアップファイルがプロジェクトに追加されていない

**解決方法:**
1. `startup_rh850f1kms1_csp.asm` をプロジェクトに追加
2. リビルド

### デバッガが接続できない

**確認事項:**
1. デバッガ（E2など）がPCに接続されているか
2. ターゲットボードに電源が入っているか
3. デバッガドライバがインストールされているか

**シミュレータを使用する場合:**
1. **Debug → Debug Tool → Simulator**
2. 実機なしでコードの動作確認が可能

## ビルド出力の確認

### 生成されるファイル

```
Debug\
├── RH850_Startup_Demo.abs    (実行ファイル)
├── RH850_Startup_Demo.hex    (Hexファイル)
├── RH850_Startup_Demo.map    (マップファイル)
└── *.obj                      (オブジェクトファイル)
```

### メモリ使用量確認

**Build Output Window で確認:**
```
ROM (Code + Const):  XXX bytes
RAM (Data + BSS):    XXX bytes
```

## 次のステップ

### 1. アプリケーション開発

`main.c` を編集してアプリケーションロジックを実装:

```c
int main(void) {
    // ペリフェラル初期化
    // GPIO設定
    // タイマー設定

    while(1) {
        // メインループ
    }

    return 0;
}
```

### 2. 割り込みハンドラ追加

```c
// main.c に追加
void _INT0_Handler(void) {
    // INT0割り込み処理
}
```

### 3. 最適化確認

**32バイトブロック最適化の効果を確認:**
1. デバッガでBSSクリアのループにブレークポイント
2. ステップ実行で8ワード一括処理を確認
3. 従来の1ワードずつと比較

## 参考情報

### CS+ドキュメント

- **CS+ User's Manual**: ヘルプ → User's Manual
- **CC-RH Compiler Manual**: ヘルプ → Compiler Manual
- **デバッガマニュアル**: ヘルプ → Debugger Manual

### ショートカットキー

| キー | 機能 |
|------|------|
| F7 | Build |
| Shift+F7 | Rebuild All |
| F3 | Download |
| F5 | Go |
| F6 | Reset Go |
| F10 | Step Over |
| F11 | Step Into |
| Shift+F5 | Stop Debug |

---

**準備完了！** CS+でビルドとデバッグを開始できます。
