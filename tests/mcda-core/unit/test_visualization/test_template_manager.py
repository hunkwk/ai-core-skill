"""
模板管理器单元测试

测试 Jinja2 模板系统功能：
- 模板加载
- 模板渲染
- 模板继承
- 自定义变量和过滤器
"""

import pytest
from pathlib import Path
import sys

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent.parent
mcda_core_path = project_root / "skills" / "mcda-core" / "lib"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from visualization.template_manager import TemplateManager


class TestTemplateLoading:
    """模板加载测试"""

    def test_load_default_template(self):
        """测试加载默认模板"""
        manager = TemplateManager()
        template = manager.load_template('default_report')

        assert template is not None
        assert hasattr(template, 'render')

    def test_load_professional_template(self):
        """测试加载专业模板"""
        manager = TemplateManager()
        template = manager.load_template('professional_report')

        assert template is not None

    def test_load_minimal_template(self):
        """测试加载极简模板"""
        manager = TemplateManager()
        template = manager.load_template('minimal_report')

        assert template is not None

    def test_load_invalid_template(self):
        """测试加载不存在的模板"""
        manager = TemplateManager()

        with pytest.raises(FileNotFoundError):
            manager.load_template('nonexistent')

    def test_list_available_templates(self):
        """测试列出可用模板"""
        manager = TemplateManager()
        templates = manager.list_templates()

        assert isinstance(templates, list)
        assert 'default_report' in templates
        assert 'professional_report' in templates
        assert 'minimal_report' in templates

    def test_load_base_template(self):
        """测试加载基础模板"""
        manager = TemplateManager()
        template = manager.load_template('base')

        assert template is not None


class TestTemplateRendering:
    """模板渲染测试"""

    def test_render_template_with_context(self):
        """测试渲染模板（带上下文）"""
        manager = TemplateManager()

        context = {
            'title': '测试报告',
            'content': '这是测试内容'
        }

        html = manager.render_template('default_report', context)

        assert isinstance(html, str)
        assert len(html) > 0
        assert '测试报告' in html

    def test_render_template_with_charts(self):
        """测试渲染模板（带图表）"""
        manager = TemplateManager()

        context = {
            'title': '决策报告',
            'charts': [
                {'title': '排名图', 'image': 'data:image/png;base64,...'},
                {'title': '热力图', 'image': 'data:image/png;base64,...'}
            ]
        }

        html = manager.render_template('default_report', context)

        assert '决策报告' in html
        assert '排名图' in html
        assert '热力图' in html

    def test_render_minimal_template(self):
        """测试渲染极简模板"""
        manager = TemplateManager()

        context = {
            'title': '极简报告',
            'summary': '决策摘要'
        }

        html = manager.render_template('minimal_report', context)

        assert '极简报告' in html
        assert '决策摘要' in html

    def test_render_with_custom_theme(self):
        """测试使用自定义主题渲染"""
        manager = TemplateManager()

        context = {
            'title': '专业报告',
            'theme': 'professional',
            'data': {'score': 0.85}
        }

        html = manager.render_template('professional_report', context)

        assert '专业报告' in html


class TestTemplateInheritance:
    """模板继承测试"""

    def test_base_template_blocks(self):
        """测试基础模板的块定义"""
        manager = TemplateManager()

        # 渲染子模板，应该包含基础模板的内容
        context = {'title': '继承测试'}
        html = manager.render_template('default_report', context)

        # 应该包含基础模板的元素（如 header, footer）
        assert '<html>' in html or '<!DOCTYPE html>' in html
        assert '</html>' in html

    def test_component_inclusion(self):
        """测试组件包含"""
        manager = TemplateManager()

        context = {
            'title': '组件测试',
            'show_header': True,
            'show_footer': True
        }

        html = manager.render_template('default_report', context)

        # 应该包含组件
        assert html is not None
        assert len(html) > 0


class TestCustomFilters:
    """自定义过滤器测试"""

    def test_percentage_filter(self):
        """测试百分比过滤器"""
        manager = TemplateManager()

        context = {'value': 0.85, 'score': 0.8567}
        html = manager.render_template('test_filters', context)

        assert '85%' in html or '85.0%' in html

    def test_round_filter(self):
        """测试舍入过滤器"""
        manager = TemplateManager()

        context = {'value': 0.85, 'score': 0.8567}
        html = manager.render_template('test_filters', context)

        assert '0.86' in html or '0.857' in html


class TestTemplateManagerAPI:
    """模板管理器 API 测试"""

    def test_add_template_path(self):
        """测试添加模板路径"""
        manager = TemplateManager()

        # 添加自定义模板目录
        custom_path = Path('/tmp/custom_templates')
        manager.add_template_path(custom_path)

        # 验证路径已添加
        assert custom_path in manager.template_paths

    def test_get_template_info(self):
        """测试获取模板信息"""
        manager = TemplateManager()

        info = manager.get_template_info('default_report')

        assert info is not None
        assert 'name' in info
        assert 'description' in info

    def test_set_global_context(self):
        """测试设置全局上下文"""
        manager = TemplateManager()

        # 设置全局变量
        manager.set_global_context({
            'company_name': '测试公司',
            'logo_url': '/logo.png'
        })

        # 渲染模板，应该包含全局变量
        html = manager.render_template('default_report', {'title': '测试'})

        assert html is not None


class TestReportGeneration:
    """报告生成测试"""

    def test_generate_decision_report(self, tmp_path):
        """测试生成决策报告"""
        manager = TemplateManager()

        context = {
            'title': 'MCDA 决策报告',
            'algorithm': 'TOPSIS',
            'alternatives': ['方案A', '方案B', '方案C'],
            'rankings': [
                {'rank': 1, 'alternative': '方案A', 'score': 0.85},
                {'rank': 2, 'alternative': '方案B', 'score': 0.72},
                {'rank': 3, 'alternative': '方案C', 'score': 0.63}
            ],
            'charts': [
                {'title': '排名对比', 'image': 'base64data...'}
            ]
        }

        html = manager.render_template('default_report', context)

        # 验证报告内容
        assert 'MCDA 决策报告' in html
        assert 'TOPSIS' in html
        assert '方案A' in html
        assert '0.85' in html

        # 保存到文件
        output_file = tmp_path / 'report.html'
        manager.save_report(html, output_file)

        assert output_file.exists()

    def test_generate_minimal_report(self, tmp_path):
        """测试生成极简报告"""
        manager = TemplateManager()

        context = {
            'title': '快速决策报告',
            'summary': '推荐方案A',
            'top_alternative': '方案A',
            'score': 0.85
        }

        html = manager.render_template('minimal_report', context)

        assert '快速决策报告' in html
        assert '方案A' in html

        # 保存报告
        output_file = tmp_path / 'minimal_report.html'
        manager.save_report(html, output_file)

        assert output_file.exists()


class TestCustomTemplate:
    """自定义模板测试"""

    def test_load_custom_template_from_file(self, tmp_path):
        """测试从文件加载自定义模板"""
        manager = TemplateManager()

        # 创建自定义模板
        custom_template = tmp_path / 'my_template.html'
        custom_template.write_text('<html><body>{{ title }}</body></html>')

        # 加载并渲染
        html = manager.render_template(str(custom_template), {'title': '自定义'})

        assert '自定义' in html

    def test_create_template_from_string(self):
        """测试从字符串创建模板"""
        manager = TemplateManager()

        template_string = '<html><body>{{ content }}</body></html>'
        html = manager.render_from_string(template_string, {'content': '测试内容'})

        assert '测试内容' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
