# 赛博小镇一键启动脚本
# 用法：右键“使用 PowerShell 运行”，或在终端执行  .\start.ps1
# 作用：① 在新窗口启动 FastAPI 后端  ② 等后端就绪  ③ 启动 Godot 游戏

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$backend = Join-Path $root "backend"
$proj = Join-Path $root "helloagents-ai-town"

# 定位 Godot 引擎：优先 ..\_tools，其次 PATH 里的 godot
$godot = Join-Path $root "..\_tools\Godot_v4.5-stable_win64.exe"
if (-not (Test-Path $godot)) {
    $cmd = Get-Command godot -ErrorAction SilentlyContinue
    if ($cmd) { $godot = $cmd.Source } else {
        Write-Host "[ERROR] 找不到 Godot 引擎，请把 Godot exe 放到 _tools 目录或加入 PATH" -ForegroundColor Red
        exit 1
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " 赛博小镇启动器" -ForegroundColor Cyan
Write-Host " 后端: $backend"
Write-Host " 游戏: $proj"
Write-Host " 引擎: $godot"
Write-Host "============================================================" -ForegroundColor Cyan

# ① 在独立窗口启动后端（窗口保留，方便看对话日志）
Write-Host "[1/3] 启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "`$env:PYTHONIOENCODING='utf-8'; Set-Location '$backend'; py main.py"
)

# ② 等待后端就绪
Write-Host "[2/3] 等待后端就绪 (http://127.0.0.1:8000) ..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 40; $i++) {
    try { Invoke-RestMethod "http://127.0.0.1:8000/" -TimeoutSec 2 | Out-Null; $ready = $true; break }
    catch { Start-Sleep -Milliseconds 700 }
}
if (-not $ready) {
    Write-Host "[WARN] 后端未在预期时间内响应，仍将启动游戏（游戏内会自动重连）。" -ForegroundColor DarkYellow
} else {
    Write-Host "      后端已就绪 ✅" -ForegroundColor Green
}

# ③ 启动游戏（不加 --editor 表示直接运行主场景）
Write-Host "[3/3] 启动游戏... (WASD 移动, 靠近 NPC 按 E 对话)" -ForegroundColor Yellow
& $godot --path $proj

Write-Host "游戏已退出。后端窗口如不再需要可手动关闭。" -ForegroundColor Cyan
