"""
主题管理器

提供图表主题的加载、切换和应用功能。
支持预定义主题和自定义主题。
"""

from pathlib import Path
from typing import Any, Optional, Union
import yaml
import matplotlib as mpl
import matplotlib.pyplot as plt


class ThemeManager:
    """主题管理器

    管理图表主题，支持主题加载、切换和应用。

    Example:
        ```python
        manager = ThemeManager()

        # 列出可用主题
        themes = manager.list_themes()
        print(themes)  # ['default', 'professional', 'minimal', 'colorful', 'dark']

        # 加载主题
        theme = manager.load_theme('default')

        # 应用主题
        manager.apply_theme(theme)

        # 设置主题（快捷方式）
        manager.set_theme('professional')
        ```
    """

    def __init__(self):
        """初始化主题管理器"""
        self._current_theme = None
        self._themes_dir = Path(__file__).parent / 'themes'

    # ========================================================================
    # 主题加载
    # ========================================================================

    def load_theme(self, theme_name: str) -> dict[str, Any]:
        """加载主题配置

        Args:
            theme_name: 主题名称（如 'default', 'professional'）

        Returns:
            主题配置字典

        Raises:
            FileNotFoundError: 主题文件不存在
        """
        # 支持自定义路径
        theme_path = Path(theme_name)
        if not theme_path.is_absolute():
            # 相对路径，从 themes 目录查找
            theme_path = self._themes_dir / f'{theme_name}.yaml'

        if not theme_path.exists():
            raise FileNotFoundError(f"主题文件不存在: {theme_name}")

        with open(theme_path, 'r', encoding='utf-8') as f:
            theme = yaml.safe_load(f)

        return theme

    def list_themes(self) -> list[str]:
        """列出所有可用主题

        Returns:
            主题名称列表（不含扩展名）
        """
        theme_files = self._themes_dir.glob('*.yaml')
        return [f.stem for f in theme_files if f.stem != '__init__']

    # ========================================================================
    # 主题应用
    # ========================================================================

    def apply_theme(self, theme: dict[str, Any]) -> None:
        """应用主题到 matplotlib

        Args:
            theme: 主题配置字典
        """
        if 'colors' in theme:
            colors = theme['colors']

            # 设置颜色
            if 'background' in colors:
                mpl.rcParams['figure.facecolor'] = colors['background']
                mpl.rcParams['axes.facecolor'] = colors['background']

            if 'text' in colors:
                mpl.rcParams['text.color'] = colors['text']
                mpl.rcParams['axes.labelcolor'] = colors['text']
                mpl.rcParams['xtick.color'] = colors['text']
                mpl.rcParams['ytick.color'] = colors['text']

            if 'title' in colors:
                mpl.rcParams['axes.titlecolor'] = colors['title']

            if 'grid' in colors:
                mpl.rcParams['grid.color'] = colors['grid']

            if 'axis' in colors:
                mpl.rcParams['axes.edgecolor'] = colors['axis']
                mpl.rcParams['axes.labelcolor'] = colors['axis']

        if 'fonts' in theme:
            fonts = theme['fonts']

            if 'family' in fonts:
                mpl.rcParams['font.family'] = fonts['family']

            if 'title_size' in fonts:
                mpl.rcParams['axes.titlesize'] = fonts['title_size']

            if 'label_size' in fonts:
                mpl.rcParams['axes.labelsize'] = fonts['label_size']

            if 'tick_size' in fonts:
                mpl.rcParams['xtick.labelsize'] = fonts['tick_size']
                mpl.rcParams['ytick.labelsize'] = fonts['tick_size']

            if 'legend_size' in fonts:
                mpl.rcParams['legend.fontsize'] = fonts['legend_size']

            if 'title_weight' in fonts:
                mpl.rcParams['axes.titleweight'] = fonts['title_weight']

            if 'label_weight' in fonts:
                mpl.rcParams['axes.labelweight'] = fonts['label_weight']

        if 'lines' in theme:
            lines = theme['lines']

            if 'linewidth' in lines:
                mpl.rcParams['lines.linewidth'] = lines['linewidth']

            if 'linestyle' in lines:
                mpl.rcParams['lines.linestyle'] = lines['linestyle']

            if 'marker' in lines:
                mpl.rcParams['lines.marker'] = lines['marker']

            if 'markersize' in lines:
                mpl.rcParams['lines.markersize'] = lines['markersize']

        if 'save' in theme:
            save_config = theme['save']

            if 'dpi' in save_config:
                mpl.rcParams['savefig.dpi'] = save_config['dpi']

            if 'format' in save_config:
                mpl.rcParams['savefig.format'] = save_config['format']

            if 'facecolor' in save_config:
                mpl.rcParams['savefig.facecolor'] = save_config['facecolor']

    def reset_theme(self) -> None:
        """重置为默认主题"""
        mpl.rcParams.clear()
        mpl.rcParams.update(mpl.rcParamsDefault)  # 恢复到 matplotlib 默认值
        self._current_theme = None

    # ========================================================================
    # 主题管理 API
    # ========================================================================

    def set_theme(self, theme_name: str) -> bool:
        """设置当前主题

        Args:
            theme_name: 主题名称

        Returns:
            是否成功设置
        """
        try:
            theme = self.load_theme(theme_name)
            self.apply_theme(theme)
            self._current_theme = theme_name
            return True
        except FileNotFoundError:
            return False

    def get_current_theme(self) -> Optional[str]:
        """获取当前主题名称

        Returns:
            当前主题名称，如果未设置则返回 None
        """
        return self._current_theme

    def get_theme_info(self, theme_name: str) -> Optional[dict[str, str]]:
        """获取主题信息

        Args:
            theme_name: 主题名称

        Returns:
            主题信息字典（name, description, version）
        """
        try:
            theme = self.load_theme(theme_name)
            return {
                'name': theme.get('name', ''),
                'description': theme.get('description', ''),
                'version': theme.get('version', '')
            }
        except FileNotFoundError:
            return None

    # ========================================================================
    # 自定义主题
    # ========================================================================

    def save_theme(self, theme: dict[str, Any], filepath: Union[str, Path]) -> None:
        """保存主题到文件

        Args:
            theme: 主题配置字典
            filepath: 保存路径
        """
        filepath = Path(filepath)

        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(theme, f, allow_unicode=True, default_flow_style=False)

    def create_custom_theme(
        self,
        name: str,
        colors: dict[str, str],
        fonts: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """创建自定义主题

        Args:
            name: 主题名称
            colors: 颜色配置
            fonts: 字体配置（可选）

        Returns:
            主题配置字典
        """
        theme = {
            'name': name,
            'version': '1.0.0',
            'colors': colors
        }

        if fonts:
            theme['fonts'] = fonts

        return theme
