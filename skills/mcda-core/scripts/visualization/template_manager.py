"""
模板管理器

提供 Jinja2 模板的加载、渲染和管理功能。
支持模板继承、自定义过滤器和全局上下文。
"""

from pathlib import Path
from typing import Any, Optional, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape
import base64
from io import BytesIO


class TemplateManager:
    """模板管理器

    管理 Jinja2 模板，支持模板加载、渲染和自定义。

    Example:
        ```python
        manager = TemplateManager()

        # 渲染模板
        context = {'title': '决策报告', 'content': '...'}
        html = manager.render_template('default_report', context)

        # 保存报告
        manager.save_report(html, 'report.html')
        ```
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """初始化模板管理器

        Args:
            template_dir: 模板目录路径（默认使用内置模板）
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / 'templates'

        self.template_dir = Path(template_dir)
        self.template_paths = [self.template_dir]

        # 初始化 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(self.template_paths),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 添加自定义过滤器
        self._register_filters()

        # 全局上下文
        self.global_context = {}

    # ========================================================================
    # 模板加载
    # ========================================================================

    def load_template(self, template_name: str):
        """加载模板

        Args:
            template_name: 模板名称或路径（不含扩展名）

        Returns:
            Jinja2 Template 对象

        Raises:
            FileNotFoundError: 模板文件不存在
        """
        # 如果是绝对路径，添加到模板路径中
        template_path = Path(template_name)
        if template_path.is_absolute():
            if not template_path.exists():
                raise FileNotFoundError(f"模板文件不存在: {template_name}")

            # 添加父目录到搜索路径
            parent_dir = template_path.parent
            if parent_dir not in self.template_paths:
                self.add_template_path(parent_dir)

            # 使用文件名加载
            template_name = template_path.stem

        # 添加 .html 扩展名（如果需要）
        if not template_name.endswith('.html'):
            template_name = f'{template_name}.html'

        try:
            return self.env.get_template(template_name)
        except Exception as e:
            raise FileNotFoundError(f"模板文件不存在: {template_name}") from e

    def list_templates(self) -> list[str]:
        """列出所有可用模板

        Returns:
            模板名称列表（不含扩展名）
        """
        templates = []

        for template_path in self.template_paths:
            if template_path.exists():
                for f in template_path.glob('*.html'):
                    # 排除组件和基础模板
                    if f.stem not in ['base', 'test_filters']:
                        templates.append(f.stem)

        return sorted(list(set(templates)))

    # ========================================================================
    # 模板渲染
    # ========================================================================

    def render_template(
        self,
        template_name: str,
        context: dict[str, Any]
    ) -> str:
        """渲染模板

        Args:
            template_name: 模板名称
            context: 模板上下文变量

        Returns:
            渲染后的 HTML 字符串
        """
        # 合并全局上下文
        full_context = {**self.global_context, **context}

        # 加载并渲染模板
        template = self.load_template(template_name)
        return template.render(**full_context)

    def render_from_string(
        self,
        template_string: str,
        context: dict[str, Any]
    ) -> str:
        """从字符串渲染模板

        Args:
            template_string: 模板字符串
            context: 模板上下文变量

        Returns:
            渲染后的 HTML 字符串
        """
        # 合并全局上下文
        full_context = {**self.global_context, **context}

        # 从字符串创建模板
        template = self.env.from_string(template_string)
        return template.render(**full_context)

    # ========================================================================
    # 报告生成
    # ========================================================================

    def save_report(
        self,
        html: str,
        filepath: Union[str, Path],
        encoding: str = 'utf-8'
    ) -> None:
        """保存报告到文件

        Args:
            html: HTML 内容
            filepath: 输出文件路径
            encoding: 文件编码
        """
        filepath = Path(filepath)

        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(html)

    def generate_report(
        self,
        template_name: str,
        context: dict[str, Any],
        output_path: Union[str, Path]
    ) -> str:
        """生成报告（一步完成）

        Args:
            template_name: 模板名称
            context: 模板上下文
            output_path: 输出文件路径

        Returns:
            渲染后的 HTML 字符串
        """
        html = self.render_template(template_name, context)
        self.save_report(html, output_path)
        return html

    # ========================================================================
    # 模板管理 API
    # ========================================================================

    def add_template_path(self, path: Union[str, Path]) -> None:
        """添加模板搜索路径

        Args:
            path: 模板目录路径
        """
        path = Path(path)

        if path not in self.template_paths:
            self.template_paths.append(path)

        # 更新 Jinja2 环境
        self.env.loader = FileSystemLoader(self.template_paths)

    def set_global_context(self, context: dict[str, Any]) -> None:
        """设置全局上下文变量

        Args:
            context: 全局变量字典
        """
        self.global_context.update(context)

    def get_template_info(self, template_name: str) -> Optional[dict[str, str]]:
        """获取模板信息

        Args:
            template_name: 模板名称

        Returns:
            模板信息字典（如果存在）
        """
        try:
            template = self.load_template(template_name)

            # 从模板注释中提取信息（如果有）
            info = {
                'name': template_name,
                'description': '',
                'version': '1.0.0'
            }

            return info
        except FileNotFoundError:
            return None

    # ========================================================================
    # 自定义过滤器
    # ========================================================================

    def _register_filters(self) -> None:
        """注册自定义过滤器"""

        # 百分比过滤器
        def percentage(value: float, decimals: int = 1) -> str:
            """将小数转换为百分比字符串"""
            return f"{value * 100:.{decimals}f}%"

        # 舍入过滤器
        def round_filter(value: float, precision: int = 2) -> float:
            """舍入到指定精度"""
            return round(value, precision)

        # 格式化分数
        def format_score(value: float, decimals: int = 4) -> str:
            """格式化分数"""
            return f"{value:.{decimals}f}"

        # 添加到环境
        self.env.filters['percentage'] = percentage
        self.env.filters['round'] = round_filter
        self.env.filters['format_score'] = format_score

    # ========================================================================
    # 工具方法
    # ========================================================================

    @staticmethod
    def figure_to_base64(fig, format: str = 'png') -> str:
        """将 matplotlib 图表转换为 base64 字符串

        Args:
            fig: matplotlib Figure 对象
            format: 图像格式（png, svg, pdf）

        Returns:
            base64 编码的图像字符串（带 data URI 前缀）
        """
        import matplotlib.pyplot as plt

        # 保存到 BytesIO
        buf = BytesIO()
        fig.savefig(buf, format=format, bbox_inches='tight', facecolor='white')
        buf.seek(0)

        # 转换为 base64
        img_bytes = buf.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # 添加 data URI 前缀
        mime_type = f'image/{format}'
        return f'data:{mime_type};base64,{img_base64}'
