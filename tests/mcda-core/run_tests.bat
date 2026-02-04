@echo off
REM MCDA Core - 测试运行脚本

echo ========================================
echo MCDA Core - 运行单元测试
echo ========================================
echo.

cd /d "%~dp0..\.."

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: Python 未安装或不在 PATH 中
    echo 请安装 Python 3.12+ 并添加到 PATH
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖...
pip install pytest pyyaml numpy -q

echo.
echo [3/3] 运行测试...
echo.

REM 运行数据模型测试
echo === 运行数据模型测试 ===
python -m pytest tests/mcda-core/test_models.py -v --tb=short

if errorlevel 1 (
    echo.
    echo 测试失败！
    pause
    exit /b 1
)

echo.
echo === 运行异常测试 ===
python -m pytest tests/mcda-core/test_exceptions.py -v --tb=short

if errorlevel 1 (
    echo.
    echo 测试失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 所有测试通过！
echo ========================================
pause
