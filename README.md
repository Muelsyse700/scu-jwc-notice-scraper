# SCU Notice Scraper

一个用于采集和过滤四川大学相关网站通知的Python工具，支持多条件筛选和格式化输出。

## 功能特性

*   **实时采集**：支持实时从指定网站获取最新通知信息
*   **智能过滤**：提供多种过滤条件筛选所需信息
*   **标签分类**：按通知类别进行分组和筛选
*   **时间过滤**：支持按发布时间范围筛选
*   **置顶识别**：可区分并筛选置顶通知
*   **彩色输出**：终端彩色格式化显示结果
*   **灵活配置**：支持多种参数组合，满足不同需求

## 安装要求

### Python版本
*   Python 3.7+

### 依赖库

```bash
# 主要依赖（根据实际代码需要）
pip install datetime colorama
```

## 使用方法

### 基本使用

```python
from scu_notice_scraper import SCUscraper

# 初始化采集器
scraper = SCUscraper("https://jwc.scu.edu.cn/", mode="realtime")

# 显示所有通知
scraper.show_info()
```

### 过滤器使用示例

```python
# 单条件过滤：按标题关键词
scraper.filter_info(title_contains="四川大学")

# 多条件组合过滤
scraper.filter_info(
    title_contains="报名",                # 标题包含"报名"
    time_after="2024-10-01",             # 2024年10月1日之后
    time_before="2024-12-31",            # 2024年12月31日之前
    tag_is="教学工作",                    # 通知类别为"教学工作"
    top=True,                            # 仅显示置顶通知
    print_filter=True                    # 打印过滤条件
)

# 显示过滤结果
scraper.show_info()
```

### 标签过滤支持格式

```python
# 单标签（字符串）
scraper.filter_info(tag_is="教学工作")

# 多标签（列表）
scraper.filter_info(tag_is=["教学工作", "科研动态", "学术讲座"])

# 多标签（集合）
scraper.filter_info(tag_is={"教学工作", "学术讲座"})

# 多标签（元组）
scraper.filter_info(tag_is=("教学工作", "科研动态"))
```

## API参考

### `SCUscraper` 类

#### 初始化参数

```python
SCUscraper(url: str, mode: str = "realtime")
```

*   `url`: 目标网站URL
*   `mode`: 采集模式，目前支持 "realtime"

### `filter_info` 方法

#### 参数说明

```python
def filter_info(
    self,
    title_contains: Optional[str] = None,      # 标题包含的关键词
    time_after: Optional[str] = None,          # 发布时间在此之后（格式需符合time_format）
    time_before: Optional[str] = None,         # 发布时间在此之前（格式需符合time_format）
    tag_is: Union[str, Iterable[str], None] = None,  # 通知类别
    top: Optional[bool] = None,                # 置顶状态（True=仅置顶，False=仅非置顶）
    time_format: str = "%Y-%m-%d",             # 时间格式字符串
    print_filter: bool = False                 # 是否打印过滤条件
)
```

#### 过滤逻辑

1.  **标题过滤**：检查通知标题是否包含指定关键词
2.  **时间过滤**：支持时间范围筛选，支持自定义时间格式
3.  **标签过滤**：支持单个或多个标签筛选
4.  **置顶过滤**：可筛选置顶或非置顶通知
5.  **条件组合**：多个过滤条件之间为"与"关系

### `show_info` 方法

格式化输出通知信息，包含以下内容：

*   **URL**：通知链接（青色显示）
*   **时间**：发布时间（红色显示，格式：yy-mm-dd）
*   **标签**：通知类别（黄色显示）
*   **标题**：通知标题（洋红色显示）
*   **置顶标识**：置顶通知会显示"[置顶]"标识（黄底黑字）

## 输出示例

```
过滤信息: 类别[教学工作] 关键字"报名" 发布时间在2024-10-01之后 发布时间在2024-12-31之前 仅置顶信息 
https://jwc.scu.edu.cn/xxxx 24-10-15 [教学工作]关于xxx报名的通知[置顶]
https://jwc.scu.edu.cn/xxxx 24-10-10 [教学工作]2024年秋季学期报名通知[置顶]
```

## 错误处理

*   **时间格式错误**：如果提供的时间字符串不符合指定的`time_format`格式，该条通知将被过滤掉
*   **标签类型错误**：如果`tag_is`参数不是字符串或可迭代对象，将抛出`TypeError`
*   **空结果处理**：过滤后如果没有匹配的通知，`info`列表将为空

## 注意事项

1.  **时间格式**：默认使用"%Y-%m-%d"格式（如：2024-10-01），可通过`time_format`参数自定义
2.  **字符串匹配**：标题关键词匹配为简单字符串包含匹配，区分大小写
3.  **置顶过滤**：`top=True`仅显示置顶，`top=False`仅显示非置顶，`top=None`不限制
4.  **性能考虑**：过滤器会遍历所有通知，大数据量时可能需要优化
5.  **颜色支持**：需要终端支持ANSI颜色代码

## 开发计划

*   [ ] 改进标题匹配算法（支持模糊匹配、正则表达式）
*   [ ] 添加更多采集模式支持
*   [ ] 优化过滤性能
*   [ ] 添加结果导出功能（CSV、JSON等格式）
*   [ ] 添加Web界面

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 作者

Muelsyse700; Y-jiiemo

---

**提示**：使用本工具时请遵守目标网站的Robots协议和相关使用条款，不要过度频繁请求以免对服务器造成压力。
