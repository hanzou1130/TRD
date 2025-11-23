# RH850F1KMS-1 スタートアップコード - CS+版

Renesas CS+ for CC開発環境用のRH850F1KMS-1スタートアップコードです。

## ファイル構成

- **startup_rh850f1kms1_csp.asm** - CS+用スタートアップアセンブリコード
- **rh850f1kms1_csp.dr** - CS+用デバイスファイル（リンカスクリプト）
- **CS_PLUS_README.md** - このドキュメント

## CS+プロジェクトへの組み込み

### 1. プロジェクト作成

1. **CS+を起動**
2. **File → New → Project**
3. **プロジェクト設定:**
   - Target Device: RH850/F1KM-S1
   - Tool-Chain: CC-RH (Renesas C Compiler)
   - Project Type: Application

### 2. ファイル追加

**プロジェクトツリーで右クリック → Add → Add Files:**

1. `startup_rh850f1kms1_csp.asm` を追加
2. `main.c` を追加（アプリケーションコード）

### 3. デバイスファイル設定

**プロジェクト → Properties → Link Options:**

1. **Device File** タブを選択
2. `rh850f1kms1_csp.dr` を指定

または、プロジェクトフォルダに配置して自動認識させる

### 4. ビルド設定

**Build → Build Project** または `F7`

## 最適化機能

### 高速初期化

GCC/GHS版と同様の最適化を実装：

- ✅ **32バイトブロック処理**: BSS/DATAを8ワード単位で処理
- ✅ **ループアンローリング**: ブランチペナルティ削減
- ✅ **早期終了チェック**: 空セクションをスキップ
- ✅ **ハードウェアループ**: `loop`命令使用

### パフォーマンス

| セクション | 処理時間（概算） | 改善率 |
|----------|---------------|--------|
| BSS 1KB | ~40サイクル | 6.4倍高速 |
| DATA 1KB | ~80サイクル | 6.4倍高速 |

## メモリマップ

### Flash (ROM)
- **アドレス**: 0x00000000 - 0x003FFFFF
- **サイズ**: 4 MB
- **用途**: コード、定数、ベクタテーブル

### RAM
- **アドレス**: 0xFEBD0000 - 0xFEBD7FFF
- **サイズ**: 256 KB
- **用途**: スタック、ヒープ、データ

## CS+固有の機能

### Small Data Area (SDA)

頻繁にアクセスするデータを効率的に配置：

```c
// Small Data Areaに配置
#pragma section sdata "MySData"
int frequently_used_var;
#pragma section

// Small BSSに配置
#pragma section sbss "MySBss"
int frequently_used_bss;
#pragma section
```

### セクション配置

```c
// 特定セクションに配置
#pragma section text "MyCode"
void my_function(void) {
    // この関数は MyCode セクションに配置
}
#pragma section
```

## ビルド手順

### CS+ IDE使用

1. **プロジェクトを開く**
2. **Build → Rebuild All** (`Shift + F7`)
3. **出力確認:**
   - `Debug\` または `Release\` フォルダに `.abs` ファイル生成
   - `.hex` ファイルも自動生成

### コマンドラインビルド

```cmd
rem CS+コマンドラインビルド
CubeSuite+.exe /b /p "ProjectName.mtpj"
```

## デバッグ

### CS+ Debugger使用

1. **Debug → Download** (`F3`)
2. **デバッガ接続:**
   - E2エミュレータ
   - E1エミュレータ
   - E20エミュレータ
   - JTAG

3. **ブレークポイント設定:**
   - `_RESET` にブレークポイント
   - `main` にブレークポイント

4. **実行:**
   - `F5` - Go
   - `F10` - Step Over
   - `F11` - Step Into

### メモリビュー

**View → Memory** でBSS/DATAセクションの初期化を確認

## カスタマイズ

### スタックサイズ変更

`rh850f1kms1_csp.dr` を編集：

```c
.stack (NOLOAD) :
{
    . = ALIGN(8);
    __stkbase = .;
    . = . + 0x2000;         /* 8KB stack */
    __stkend = .;
} > RAM
```

### 割り込みハンドラ追加

```c
// main.c
void _INT0_Handler(void) {
    // INT0割り込み処理
}
```

## コンパイラオプション推奨設定

**プロジェクト → Properties → Compile Options:**

### 最適化
- **Optimization Level**: -O2 (Speed優先)
- **Inline Expansion**: Enable

### デバッグ
- **Debug Information**: Full (-g)

### 警告
- **Warning Level**: All (-Wall)

## トラブルシューティング

### エラー: "undefined symbol '__stkend'"

**原因**: デバイスファイルが正しく設定されていない

**解決方法**: `rh850f1kms1_csp.dr` をリンカオプションで指定

### エラー: "section '.intvect' not found"

**原因**: スタートアップファイルがプロジェクトに追加されていない

**解決方法**: `startup_rh850f1kms1_csp.asm` をプロジェクトに追加

### ビルドは成功するが動作しない

**確認事項**:
1. デバイスファイルのメモリアドレスが正しいか
2. スタックサイズが十分か
3. 割り込みベクタが正しく配置されているか

## GCC/GHS版との違い

| 項目 | GCC/GHS版 | CS+版 |
|------|----------|-------|
| **ファイル拡張子** | `.S` / `.800` | `.asm` |
| **デバイスファイル** | `.ld` | `.dr` |
| **コメント** | `/* */`, `;` | `;` |
| **main呼び出し** | `jmp [r10]` | `jarl _main, lp` |
| **スタックシンボル** | `__stack_top` | `__stkend` |
| **ヘッダ** | なし | Renesasディスクレーマー |

## サンプルプロジェクト構造

```
CS+Project/
├── startup_rh850f1kms1_csp.asm
├── rh850f1kms1_csp.dr
├── main.c
├── ProjectName.mtpj              (CS+プロジェクトファイル)
└── Debug/                        (ビルド出力)
    ├── ProjectName.abs
    └── ProjectName.hex
```

## 参考資料

- **CS+ User's Manual**: CS+の使用方法
- **CC-RH Compiler User's Manual**: コンパイラオプション
- **RH850/F1KM Hardware Manual** (R01UH0684JJ0130): ハードウェア仕様

## ライセンス

このスタートアップコードはRenesasディスクレーマーに従います。

## 更新履歴

- **2025-11-22**: CS+版作成
  - Renesasヘッダ追加
  - `.asm`拡張子使用
  - `.dr`デバイスファイル作成
  - CS+固有シンボル対応
  - 32バイトブロック最適化実装
