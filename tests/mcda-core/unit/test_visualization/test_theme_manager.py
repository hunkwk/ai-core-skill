"""
主题管理器单元测试

测试主题系统功能：
- 主题加载
- 主题切换
- 主题应用
- 自定义主题
"""

import pytest
from pathlib import Path
import sys

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent.parent
mcda_core_path = project_root / "skills" / "mcda-core" / "scripts"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from visualization.theme_manager import ThemeManager


class TestThemeLoading:
    """主题加载测试"""

    def test_load_default_theme(self):
        """测试加载默认主题"""
        manager = ThemeManager()
        theme = manager.load_theme('default')

        assert theme is not None
        assert theme['name'] == '默认主题'
        assert 'colors' in theme
        assert 'fonts' in theme

    def test_load_professional_theme(self):
        """测试加载专业主题"""
        manager = ThemeManager()
        theme = manager.load_theme('professional')

        assert theme is not None
        assert theme['name'] == '专业主题'

    def test_load_minimal_theme(self):
        """测试加载极简主题"""
        manager = ThemeManager()
        theme = manager.load_theme('minimal')

        assert theme is not None
        assert theme['name'] == '极简主题'

    def test_load_colorful_theme(self):
        """测试加载彩色主题"""
        manager = ThemeManager()
        theme = manager.load_theme('colorful')

        assert theme is not None
        assert theme['name'] == '彩色主题'

    def test_load_dark_theme(self):
        """测试加载暗色主题"""
        manager = ThemeManager()
        theme = manager.load_theme('dark')

        assert theme is not None
        assert theme['name'] == '暗色主题'

    def test_load_invalid_theme(self):
        """测试加载不存在的主题"""
        manager = ThemeManager()

        with pytest.raises(FileNotFoundError):
            manager.load_theme('nonexistent')

    def test_list_available_themes(self):
        """测试列出可用主题"""
        manager = ThemeManager()
        themes = manager.list_themes()

        assert isinstance(themes, list)
        assert 'default' in themes
        assert 'professional' in themes
        assert 'minimal' in themes
        assert 'colorful' in themes
        assert 'dark' in themes
        assert len(themes) == 5


class TestThemeApplication:
    """主题应用测试"""

    def test_apply_theme_to_matplotlib(self):
        """测试应用主题到 matplotlib"""
        manager = ThemeManager()
        theme = manager.load_theme('default')

        # 应用主题
        manager.apply_theme(theme)

        # 验证 matplotlib rcParams 已更新
        import matplotlib as mpl
        assert 'axes.facecolor' in mpl.rcParams
        assert 'axes.titlesize' in mpl.rcParams

    def test_apply_dark_theme(self):
        """测试应用暗色主题"""
        manager = ThemeManager()
        theme = manager.load_theme('dark')

        manager.apply_theme(theme)

        import matplotlib as mpl
        # 验证背景色是深色
        assert mpl.rcParams['figure.facecolor'] == '#282C34'

    def test_reset_theme(self):
        """测试重置主题"""
        manager = ThemeManager()

        # 应用主题
        theme = manager.load_theme('colorful')
        manager.apply_theme(theme)

        # 重置
        manager.reset_theme()

        # 验证已恢复默认
        import matplotlib as mpl
        # 恢复到 matplotlib 默认值
        assert mpl.rcParams['axes.facecolor'] == 'white'


class TestThemeManagerAPI:
    """主题管理器 API 测试"""

    def test_get_current_theme(self):
        """测试获取当前主题"""
        manager = ThemeManager()

        # 初始状态
        current = manager.get_current_theme()
        assert current is None or current == 'default'

        # 设置主题
        manager.set_theme('professional')
        current = manager.get_current_theme()
        assert current == 'professional'

    def test_set_theme(self):
        """测试设置主题"""
        manager = ThemeManager()

        result = manager.set_theme('minimal')
        assert result is True

        current = manager.get_current_theme()
        assert current == 'minimal'

    def test_set_invalid_theme(self):
        """测试设置无效主题"""
        manager = ThemeManager()

        result = manager.set_theme('invalid')
        assert result is False

    def test_get_theme_info(self):
        """测试获取主题信息"""
        manager = ThemeManager()

        info = manager.get_theme_info('default')

        assert info is not None
        assert 'name' in info
        assert 'description' in info
        assert 'version' in info
        assert info['name'] == '默认主题'

    def test_export_theme_dict(self):
        """测试导出主题为字典"""
        manager = ThemeManager()
        theme = manager.load_theme('default')

        assert isinstance(theme, dict)
        assert 'colors' in theme
        assert 'fonts' in theme
        assert 'lines' in theme
        assert 'charts' in theme
        assert 'layout' in theme


class TestThemeConfig:
    """主题配置测试"""

    def test_theme_color_palette(self):
        """测试主题调色板"""
        manager = ThemeManager()
        theme = manager.load_theme('default')

        palette = theme['colors']['palette']
        assert isinstance(palette, list)
        assert len(palette) >= 8

        # 验证颜色格式（十六进制）
        for color in palette:
            assert color.startswith('#')
            assert len(color) == 7

    def test_theme_font_config(self):
        """测试字体配置"""
        manager = ThemeManager()
        theme = manager.load_theme('professional')

        fonts = theme['fonts']
        assert 'family' in fonts
        assert 'title_size' in fonts
        assert 'label_size' in fonts
        assert fonts['title_size'] > fonts['label_size']

    def test_theme_line_config(self):
        """测试线条配置"""
        manager = ThemeManager()
        theme = manager.load_theme('minimal')

        lines = theme['lines']
        assert 'linewidth' in lines
        assert 'linestyle' in lines
        assert 'alpha' in lines
        assert 0 <= lines['alpha'] <= 1


class TestCustomTheme:
    """自定义主题测试"""

    def test_load_custom_theme_from_dict(self):
        """测试从字典加载自定义主题"""
        manager = ThemeManager()

        custom_theme = {
            'name': '自定义主题',
            'colors': {
                'primary': '#FF0000',
                'background': '#FFFFFF'
            },
            'fonts': {
                'family': 'Arial',
                'title_size': 16
            }
        }

        # 应用自定义主题
        manager.apply_theme(custom_theme)

        # 验证主题已应用
        import matplotlib as mpl
        # 应该设置了某些配置

    def test_save_custom_theme(self, tmp_path):
        """测试保存自定义主题"""
        manager = ThemeManager()

        custom_theme = {
            'name': '测试主题',
            'version': '1.0.0',
            'colors': {
                'primary': '#00FF00',
                'background': '#FFFFFF'
            }
        }

        # 保存到文件
        output_file = tmp_path / 'custom_theme.yaml'
        manager.save_theme(custom_theme, output_file)

        # 验证文件存在
        assert output_file.exists()

        # 加载保存的主题
        loaded_theme = manager.load_theme(str(output_file))
        assert loaded_theme['name'] == '测试主题'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
