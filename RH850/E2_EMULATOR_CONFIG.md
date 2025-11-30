# E2エミュレータ接続設定

## 接続確認日時
2025-11-29 22:39

## ハードウェア構成

### E2エミュレータ
- **デバイス名**: Renesas E2 Emulator
- **シリアル番号**: 1GS008121D
- **ファームウェアバージョン**: V1.05.00.000
- **USB ID**: VID_045B&PID_82A1

### ターゲットマイコン
- **デバイス**: RH850/F1KM-S1 (RH850F1KMS-1)
- **フラッシュ**: 4MB (0x00000000 - 0x003FFFFF)
- **RAM**: 256KB (0xFEBD0000 - 0xFEC0FFFF)

## 接続設定（成功確認済み）

### Renesas Flash Programmer (RFP) 設定

```
Tool: E2 emulator
Interface: 2-wire UART
Main Clock Frequency: 20.000 MHz  ★重要★
Communication Speed: デフォルト (Auto)
Target Power Supply: ON
Supply Voltage: 3.3V
```

### 接続ピン配置

| ピン名 | 機能 | E2側コネクタ |
|--------|------|-------------|
| FLMD0 | フラッシュモード選択 | FLMD0 |
| TXD0 | UART送信 | RXD |
| RXD0 | UART受信 | TXD |
| RESET | システムリセット | RESET |
| VDD | 電源（3.3V） | VDD |
| GND | グランド | GND |

### フラッシュプログラミングモード

- **FLMD0**: GND (LOW) ← フラッシュ書き込み時
- **通常動作**: VDD (HIGH)

## CS+ デバッガ設定

### プロジェクト設定で使用する値

```
Debug Tool: E2 emulator
Serial Number: 1GS008121D
Interface: 2-wire UART
Main Clock: 20 MHz
Target Power: Supplied from E2 (3.3V)
```

### デバッガオプション
1. **Project** → **Debug Tool Settings**
2. **E2 emulator** を選択
3. **Clock** タブ → Main clock: `20.000 MHz`
4. **Power Supply** タブ → Enable target power supply: `3.3V`
5. **Connection** タブ → Interface: `2-wire UART`

## トラブルシューティング

### フレーミングエラーが発生する場合

**原因**: メインクロック周波数の不一致

**対処**:
1. Main Clock を 20 MHz に設定
2. それでもダメなら、8MHz, 16MHz, 24MHz を試す
3. Interface を 1-wire UART に変更

### 接続できない場合

**確認事項**:
- [ ] ターゲットボードに電源が供給されているか
- [ ] E2エミュレータがUSBで認識されているか（デバイスマネージャー確認）
- [ ] FLMD0ピンがGNDに接続されているか（プログラミング時）
- [ ] ケーブル接続は正しいか

### デバイスマネージャーでの確認

PowerShellコマンド:
```powershell
Get-PnpDevice | Where-Object { $_.FriendlyName -like "*E2*" }
```

期待される出力:
```
Status: OK
FriendlyName: Renesas E2
```

## ビルドとフラッシュプログラミング手順

### 1. プロジェクトビルド

```powershell
cd C:\Users\baoma\TRD\RH850
.\build.ps1
```

### 2. HEXファイル確認

生成ファイル: `build\output.hex`

### 3. RFPでフラッシュ書き込み

1. Renesas Flash Programmer V3.19 起動
2. Device: RH850 選択
3. Tool: E2 (1GS008121D) 選択
4. Interface: 2-wire UART, Main Clock: 20MHz
5. Power Supply: ON (3.3V)
6. Connect ボタンクリック
7. HEXファイルを選択
8. Program ボタンクリック

### 4. デバッグ実行（CS+）

1. CS+ 起動
2. Project 開く
3. Debug → Download (F3)
4. Debug Tool: E2 emulator, 20MHz
5. Go (F5) で実行開始

## メモ

- **正しいメインクロック周波数**: 20 MHz（これが最重要設定）
- このボードは16MHzではなく20MHzのクリスタルを使用している
- 2-wire UARTで正常動作確認済み
- ターゲット電源はE2から3.3Vで供給可能

## 参考ツールパス

```
Renesas Flash Programmer:
C:\Program Files (x86)\Renesas Electronics\Programming Tools\Renesas Flash Programmer V3.19\

CLI版:
rfp-cli.exe

GUI版:
RFPV3.exe
```

---

**最終接続確認**: 2025-11-29 22:39 ✅ 成功
