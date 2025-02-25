from colorama import init, Fore, Back  # 终端字体染色
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Iterable, Union, Literal
import csv
import requests

# import inspect  # 判断是否传参

init(autoreset=True)  # 字体颜色复位True


class SCUscraper(object):
    """抓取SCU教务处信息"""

    # TODO: 远期设计 拆分get_info方法为 自动检查更新 和 遍历查询 两种模式
    # TODO: 自动检查更新方法可以在已有get_info的基础上改造，其只需要遍历首页的信息
    # TODO: 遍历查询方法考虑基于get_info重写，直接对通知公告页进行遍历

    __slots__ = (
        "_mode",  # 信息采集模式:"realtime" / "quantity"
        "_site",  # 教务处主页地址
        "_next_page_url",  # 下一页地址信息
        "info",  # 全部已获取信息
    )

    def __init__(self, site: str, mode: Literal["realtime", "quantity"]):
        self._site = site
        self._mode = mode
        self.get_info()

    def get_info(self, params_dict: dict = None):  # TODO:功能拆分为多个私有方法
        """抓取教务处通知公告栏"""

        if self._mode == "realtime":
            self._realtime_mode(params_dict)
        elif self._mode == "quantity":
            self._quantity_mode(params_dict)

    def _fetch_homepage(self):
        """爬取教务处主页"""
        # TODO:设计间隔监测功能

        """解析教务处主页"""
        response = requests.get(self._site)
        html_content = response.content  # NOTE:不要用.text，中文会乱码
        soup = BeautifulSoup(html_content, "html.parser")

        """解析主页通知栏的<li>标签下的通知信息并以元组列表形式存储"""
        notice_board = soup.find("div", class_="sect2-l").find_all("li")
        info_list = list()
        for notice in notice_board:
            notice_url = self._site + str(
                notice.find_all("a")[0].get("href")
            )  # NOTE:文章链接
            # 寻找<a>标签中的href属性，即url
            notice_title = str(notice.find_all("p")[0].get_text())  # NOTE:文章标题
            # 寻找<p>标签并获取标签里的文本，即标题
            notice_time = datetime.strptime(
                str(notice.find_all("span")[0].get_text()), "%Y/%m/%d"
            )  # NOTE:发布时间
            # 寻找<span>标签并格式化获取其中的发布时间文本
            tag_dict = {
                "manage": "行政管理",
                "teach": "教学工作",
                "sty": "学生学业",
            }
            notice_tag = tag_dict[notice["class"][0]]  # NOTE:文章类型
            # 寻找<li>标签的class并自动匹配为相应中文
            notice_is_top = bool(
                notice.find("div", class_="bq").get_text()
            )  # NOTE:文章是否置顶
            # div bq 如果被设为置顶就有内容，反之则无内容
            info_list.append(
                {
                    "ID": hash(notice_url),  # 消息的哈希值作为唯一标识符
                    "url": notice_url,
                    "title": notice_title,
                    "time": notice_time,  # NOTE: time是yyyy-mm-dd的datetime对象
                    "tag": notice_tag,
                    "is_top": notice_is_top,
                }
            )
        self.info = SCUscraper._remove_repetitions(info_list)  # 不改变顺序去重

        if self._mode == "quantity":
            """NOTE:如果是批量搜索模式则自动获取下一页地址"""
            next_page_url = (
                soup.find("div", class_="sect2-l")
                .find("div", class_="title")
                .find("a")
                .get("href")
            )
            self._next_page_url = self._site + next_page_url

    def _realtime_mode(self, params_dict: dict = None):
        """get_info私有方法: 实时监测模式"""
        # TODO:需要添加csv存储比对
        self._fetch_homepage()

    def _quantity_mode(self, params_dict: dict = None):
        """get_info私有方法: 大批量查询模式"""
        self._fetch_homepage()

    @staticmethod
    def _remove_repetitions(info_list):
        """静态方法:消除info_list中的重复消息字典"""
        # TODO:通过比对哈希值，保留重复项中属性较多的一项

        info_set = set()
        unique_info_list = []
        for d in info_list:
            key = tuple(sorted(d.items()))  # 将字典转换为可哈希的排序元组
            if not key in info_set:
                info_set.add(key)
                unique_info_list.append(d)
        return unique_info_list

    def filter_info(
        self,
        title_contains: str = None,  # 标题包含的字符串
        time_after: str = None,  # 发布时间应晚于该时间(需符合time_format格式)
        time_before: str = None,  # 发布时间应早于该时间(需符合time_format格式)
        tag_is: Union[str, Iterable[str], None] = None,  # 通知类别
        top=None,  # 置顶状态过滤(True=仅置顶，False=仅非置顶，None=不限制)
        time_format="%Y-%m-%d",
        print_filter=False,  # 是否同时打印过滤器信息
    ):
        """信息过滤器"""
        # tag_is 预处理转tags集合
        if isinstance(tag_is, str):
            tags = {tag_is}  # 单个字符串转为集合
        elif tag_is is not None:
            try:
                tags = set(tag_is)  # 转换为集合去重
            except TypeError:
                raise TypeError("tag_is 必须是字符串或可迭代对象")
        else:
            tags = None

        flitered_info_list = list()
        for notice in self.info:
            match = True

            # 过滤标题
            # TODO:需要更好的文字匹配模式
            if not title_contains is None and not title_contains in notice["title"]:
                match = False

            # 过滤时间
            try:
                if time_after:
                    after_dt = datetime.strptime(time_after, time_format)
                    if notice["time"] <= after_dt:
                        match = False
                if time_before:
                    before_dt = datetime.strptime(time_before, time_format)
                    if notice["time"] >= before_dt:
                        match = False
            except ValueError:  # 时间格式错误视为不匹配
                match = False

            # 过滤tag
            if not tags is None and not notice["tag"] in tags:
                match = False

            # 过滤置顶
            if not top is None and not notice["is_top"] is top:
                match = False

            if match:
                flitered_info_list.append(notice)

        if print_filter:  # 打印过滤信息
            print(Back.LIGHTBLACK_EX + Fore.BLACK + "过滤信息:", end=" ")
            if not tags is None:
                print(
                    Back.LIGHTBLACK_EX
                    + Fore.BLACK
                    + "类别"
                    + "".join(f"[{x}]" for x in tags),
                    end=" ",
                )
            if not title_contains is None:  # TODO:需要改造输出模式
                print(
                    Back.LIGHTBLACK_EX + Fore.BLACK + f'关键字"{title_contains}"',
                    end=" ",
                )
            if not time_after is None:
                print(
                    Back.LIGHTBLACK_EX + Fore.BLACK + f"发布时间在{time_after}之后",
                    end=" ",
                )
            if not time_before is None:
                print(
                    Back.LIGHTBLACK_EX + Fore.BLACK + f"发布时间在{time_before}之前",
                    end=" ",
                )
            if top is True:
                print(Back.LIGHTBLACK_EX + Fore.BLACK + "仅置顶信息", end=" ")
            elif top is False:
                print(Back.LIGHTBLACK_EX + Fore.BLACK + "仅非置顶信息", end=" ")
            print()

        self.info = flitered_info_list

    def show_info(self):
        """格式化输出采集到的信息内容"""
        for notice in self.info:
            print(Fore.CYAN + notice["url"], end=" ")
            print(Fore.RED + notice["time"].strftime("%y-%m-%d"), end=" ")
            print(Fore.YELLOW + f'[{notice["tag"]}]', end="")
            print(Fore.MAGENTA + notice["title"], end="")
            if notice["is_top"]:
                print(Back.LIGHTYELLOW_EX + Fore.BLACK + "[置顶]")
            else:
                print()
            # print(str(notice["ID"]))

    @property
    def mode(self):
        return self._mode


def main():
    scraper = SCUscraper("https://jwc.scu.edu.cn/", mode="realtime")
    # scraper.filter_info(
    #     title_contains="四川大学",
    #     time_after="2024-10-10",
    #     tag_is="教学工作",
    #     top=None,
    #     print_filter=True,
    # )
    scraper.show_info()


if __name__ == "__main__":
    main()
