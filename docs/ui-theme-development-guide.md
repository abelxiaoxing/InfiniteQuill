# UI主题开发指南

## 概述
本文档提供InfiniteQuill应用UI主题开发的指导原则和最佳实践。

## 主题架构

### 文件结构
```
ui_qt/
├── styles/
│   ├── material_dark.qss     # 暗色主题样式表
│   └── material_light.qss    # 浅色主题样式表
├── utils/
│   └── theme_manager.py      # 主题管理器
└── widgets/
    ├── role_manager.py       # 角色管理器
    └── ...
```

### 主题管理器使用
```python
from ui_qt.utils.theme_manager import ThemeManager

# 创建主题管理器
theme_manager = ThemeManager()

# 切换主题
theme_manager.switch_theme("dark")
theme_manager.switch_theme("light")

# 获取当前主题
current = theme_manager.get_current_theme()

# 获取可用主题
available = theme_manager.get_available_themes()
```

## 主题开发规范

### 颜色规范
- **暗色主题背景**: #2b2b2b
- **暗色主题选中项**: #3a3a3a (Story 2.2)
- **浅色主题背景**: #ffffff
- **浅色主题选中项**: #e3f2fd

### 组件响应主题切换
所有自定义Widget都应该正确响应主题切换：

```python
class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化UI...

    def changeEvent(self, event):
        if event.type() == event.Type.StyleChange:
            # 重新应用自定义样式
            self.update_custom_styles()
        super().changeEvent(event)

    def update_custom_styles(self):
        # 根据当前主题更新样式
        theme_manager = ThemeManager()
        current_theme = theme_manager.get_current_theme()
        # 应用主题相关样式...
```

### 样式一致性检查清单
- [ ] 文字颜色与背景色对比度≥4.5:1
- [ ] 所有交互状态(悬停、选中、禁用)清晰可辨
- [ ] 边框、圆角、阴影风格统一
- [ ] 图标在不同主题下都可见
- [ ] 间距和布局在主题切换后保持一致

## 测试

### 自动化测试
运行主题一致性测试：
```bash
python test_theme_consistency.py
```

### 截图对比测试
```bash
python -c "from test_theme_consistency import run_screenshot_comparison; run_screenshot_comparison()"
```

### 极端情况测试
```bash
python -c "from test_theme_consistency import test_extreme_scenarios; test_extreme_scenarios()"
```

## 常见问题

### Q: 组件不响应主题切换？
A: 检查是否正确实现了changeEvent()方法，并处理QEvent.StyleChange事件。

### Q: 主题切换后样式不立即生效？
A: 调用widget.style().unpolish(widget)和widget.style().polish(widget)强制重绘。

### Q: 自定义绘制在主题切换后异常？
A: 在changeEvent中重新设置绘制相关的调色板和画笔。

## 版本历史
- v1.0: 基础主题系统 (Story 2.1, 2.2)
- v1.1: 主题一致性验证 (Story 2.3)
- v1.2: 增强测试覆盖率和文档

---
*最后更新: Story 2.3完成*
