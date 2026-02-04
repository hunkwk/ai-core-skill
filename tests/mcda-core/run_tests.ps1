# MCDA Core - PowerShell 测试运行脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MCDA Core - 运行单元测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到项目根目录
Set-Location "$PSScriptRoot\..\.."

# 检查 Python 环境
Write-Host "[1/4] 检查 Python 环境..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  Python 版本: $pythonVersion" -ForegroundColor Green

# 安装依赖
Write-Host ""
Write-Host "[2/4] 安装/更新依赖..." -ForegroundColor Yellow
python -m pip install pytest pyyaml numpy -q --disable-pip-version-check 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  依赖安装成功" -ForegroundColor Green
} else {
    Write-Host "  警告: 依赖安装可能失败，继续尝试运行测试" -ForegroundColor Yellow
}

# 运行数据模型测试
Write-Host ""
Write-Host "[3/4] 运行数据模型测试..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
python -m pytest tests/mcda-core/test_models.py -v --tb=short

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ 数据模型测试失败！" -ForegroundColor Red
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit $LASTEXITCODE
}

# 运行异常测试
Write-Host ""
Write-Host "[4/4] 运行异常测试..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
python -m pytest tests/mcda-core/test_exceptions.py -v --tb=short

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ 异常测试失败！" -ForegroundColor Red
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit $LASTEXITCODE
}

# 成功
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 所有测试通过！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 显示测试覆盖率（如果有 pytest-cov）
Write-Host "测试覆盖率报告:" -ForegroundColor Yellow
python -m pytest tests/mcda-core/ --cov=skills/mcda-core/lib --cov-report=term-missing 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  覆盖率报告已生成" -ForegroundColor Green
} else {
    Write-Host "  提示: 安装 pytest-cov 可查看覆盖率 (pip install pytest-cov)" -ForegroundColor Gray
}

Write-Host ""
Read-Host "按 Enter 键退出"
