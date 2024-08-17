# 设置根目录
# $rootDir = "C:\path\to\your\project"  # 请将此路径替换为你的项目根目录
$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# 进入工作目录
Set-Location $rootDir

# 设置.env文件路径
$envFilePath = "$rootDir\.env"

# 检查.env文件是否存在
if (-Not (Test-Path $envFilePath)) {
    Write-Host "File not found: .env" -ForegroundColor Red
    exit 1
}

# 打开.env文件并等待编辑完成
notepad "$rootDir\.env"

Write-Host ""
Write-Host "=== Please check the configs of '.env', and confirm to run Python script. ===" -ForegroundColor Blue
Pause

# 执行python脚本
python "$rootDir\xxx.py"

Pause
