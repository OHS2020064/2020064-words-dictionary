"""
中国证券投资基金业协会
"""
import json

import scrapy

from scrapy_words.items.c_sec_item import (
    CSec21Item,
    CSec22Item,
    CSec23Item,
    CSec24Item,
    CSec25Item,
)
from scrapy_words.spiders.base_spider import BaseSpider

# 2.1 基金协会会员单位
from scrapy_words.utils.string_utils import extract_pure_text


class CSec21Spider(BaseSpider):
    """
    基金协会会员单位
    https://gs.amac.org.cn/amac-infodisc/res/pof/member/index.html
    """
    name = 'c_sec'
    payload = {}
    total_pages = None

    def start_requests(self):
        super().start_requests()
        return [scrapy.Request(method="POST",
                               url=self.start_urls[0],
                               headers={'Content-Type': 'application/json'},
                               body=json.dumps(self.payload),
                               callback=self.parse)]

    def parse(self, response, **kwargs):
        """
        解析列表页
        """
        # 获取总页码并设置给类变量
        if self.total_pages is None:
            self.total_pages = int(json.loads(response.text)["totalPages"])
        # 当前页码
        current_page = int(json.loads(response.text)["number"])
        res_list_data = json.loads(response.text)["content"]
        for each_data in res_list_data:
            item = CSec21Item()
            item['parent'] = each_data["managerName"]
            item['cat'] = 'list'
            item['word'] = each_data["memberBehalf"]
            item['word_level'] = 120
            item['pos'] = 'n'
            yield item
            item['word'] = each_data["memberType"]
            yield item
            item['word'] = each_data["memberCode"]
            yield item
            # 解析详情页(详情页部分页面地址不同,分别处理)
            yield scrapy.Request(
                url="https://gs.amac.org.cn/amac-infodisc/res/pof/member/{}.html".format(each_data["userTenantId"]),
                meta=item,
                callback=self.parse_detail
            )
        # 爬取下一页
        print("2.1的当前页码是", current_page)
        # 这里当前页的判断依据不正确,爬虫无法终止。
        if current_page < self.total_pages:
            yield scrapy.Request(
                method="POST",
                url='https://gs.amac.org.cn/amac-infodisc/api/pof/pofMember?rand=0.033337234974890606&page={}&size=10'.format(
                    current_page + 1),
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.payload),
                callback=self.parse
            )

    def parse_detail(self, response):
        """
        解析详情页
        """
        list_item = response.meta
        # 判断响应是否正常，不正常更新url重新请求一次且仅一次
        if response.status == 404:
            # 替换url
            new_url = str(response.request.url)
            if "member" in new_url:
                new_url = new_url.replace("member", "manager")
            elif "manager" in new_url:
                new_url = new_url.replace("manager", "member")
            yield scrapy.Request(
                url=new_url,
                meta=list_item,
                callback=self.parse_detail
            )
        # 响应200 返回详细信息的item
        else:
            list_item = response.meta
            item = CSec21Item()
            item["parent"] = list_item["parent"]
            item['cat'] = 'detail'
            item["word"] = 'word'
            item['word_level'] = 119
            item['pos'] = 'n'
            detail_resp = response
            # 机构信息
            tr_1_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[1]/div[2]/table/tbody/tr")
            for tr_item in tr_1_list[1:]:
                # 提取内容
                words = tr_item.xpath("td")[1].xpath("text()").extract_first()
                if words is None or words.strip() == "":
                    continue
                item["word"] = words.replace("\xa0", "").replace(" ", "").replace("\r\n", " ")
                yield item
            # 会员机构高管/主要负责人/主要合伙人信息
            tr_2_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[2]/div[2]/table/tbody/tr[2]/td[2]/table/tbody/tr")
            for tr_item in tr_2_list:
                # 提取内容
                words = tr_item.xpath("td/text()").extract()
                for word in words[:-1]:
                    item["word"] = word
                    yield item
            # # 会员机构私募资产管理计划信息
            tr_3_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[3]/div[2]/table/tbody/tr/td[2]/table/tbody/tr")
            for tr_item in tr_3_list:
                # 提取内容
                words = tr_item.xpath("td/text()").extract()
                item["word"] = words[1]
                yield item


# 2.2私募基金管理人产品
class CSec22Spider(BaseSpider):
    """
    私募基金管理人产品
    https://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html
    """
    name = 'c_sec'
    payload = {}
    total_pages = None

    def start_requests(self):
        super().start_requests()
        return [scrapy.Request(method="POST",
                               url=self.start_urls[1],
                               headers={'Content-Type': 'application/json'},
                               body=json.dumps(self.payload),
                               callback=self.parse)]

    def parse(self, response, **kwargs):
        """
        解析列表页
        """
        """
        {
            "id": "351000133588",
            "fundNo": "SD3113",
            "fundName": "嘉兴全意投资合伙企业",
            "managerName": "子川天丰（天津）能源投资有限公司",
            "managerType": "自我管理",
            "workingState": "正在运作",
            "putOnRecordDate": 1369526400000,
            "lastQuarterUpdate": false,
            "isDeputeManage": "不适用",
            "url": "351000133588.html",
            "establishDate": 1395878400000,
            "managerUrl": "../manager/101000003335.html",
            "mandatorName": "",
            "managersInfo": [
                {
                    "managerId": 101000003335,
                    "managerUrl": "../manager/101000003335.html",
                    "managerName": "子川天丰（天津）能源投资有限公司"
                }
            ]
        }
        """
        # 获取总页码并设置给类变量
        if self.total_pages is None:
            self.total_pages = int(json.loads(response.text)["totalPages"])
        # 当前页码
        current_page = int(json.loads(response.text)["number"])
        res_list_data = json.loads(response.text)["content"]
        for each_data in res_list_data:
            item = CSec22Item()
            item['parent'] = each_data["fundName"]
            item['cat'] = 'list'
            item['word'] = each_data["managerName"]
            item['word_level'] = 120
            item['pos'] = 'n'
            yield item
            item['word'] = each_data["mandatorName"]
            (yield item) if (item['word'] != "") else None
            # 解析详情页(有两个)
            yield scrapy.Request(
                url="https://gs.amac.org.cn/amac-infodisc/res/pof/fund/{}.html".format(each_data["id"]),
                meta=item,
                callback=self.parse_detail1
            )
            yield scrapy.Request(
                url="https://gs.amac.org.cn/amac-infodisc/res/pof/manager/{}.html".format(each_data["managersInfo"][0]["managerId"]),
                meta=item,
                callback=self.parse_detail2
            )

        # 爬取下一页
        print("2.2的当前页码是", current_page)
        if current_page < self.total_pages:
            # if current_page < self.total_pages:
            yield scrapy.Request(
                method="POST",
                url='https://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.33221000223311026&page={}&size=20'.format(
                    current_page + 1),
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.payload),
                callback=self.parse
            )

    def parse_detail1(self, response):
        """解析基金详情"""
        detail_meta = response.meta
        item = CSec22Item()
        item["parent"] = detail_meta["parent"]
        item['cat'] = 'detail'
        item["word"] = 'word'
        item['word_level'] = 119
        item['pos'] = 'n'
        detail_resp = response
        # 私募基金公示信息
        base_info_list = detail_resp.xpath("/html/body/div[3]/div/div[2]/div[1]/div/table/tbody/tr")
        for base_item in base_info_list:
            words = base_item.xpath("td")[1].xpath("text()").extract_first()
            if words is None:
                continue
            ready_words = extract_pure_text(words)
            if ready_words == "":
                continue
            item["word"] = ready_words
            yield item
        # 信息披露情况,暂不爬取 (内容是：当月月报:	应披露0条，按时披露0条， 未披露0条；)

    def parse_detail2(self, response):
        """解析私募基金管理人详情"""
        detail_meta = response.meta
        item = CSec22Item()
        item["parent"] = detail_meta["parent"]
        item['cat'] = 'detail'
        item["word"] = 'word'
        item['word_level'] = 119
        item['pos'] = 'n'
        detail_resp = response
        # 基本信息
        base_info_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[2]/div[2]/table/tbody/tr")
        for base_item in base_info_list[1:]:
            words = base_item.xpath("td")[1].xpath("text()").extract_first()
            if words is not None:
                item["word"] = extract_pure_text(words)
                yield item
        # 会员信息
        members_info_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[3]/div[2]/table/tbody/tr")
        for member_item in members_info_list:
            td_list = member_item.xpath("td")
            for index, each_item in enumerate(td_list):
                if index % 2 != 0:
                    words = each_item.xpath("text()").extract_first()
                    if words is None:
                        continue
                    item["word"] = extract_pure_text(words)
                    yield item

        # 法律意见书信息(网页上无内容,暂不爬取)

        # 实际控制人信息
        controller_info_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[5]/div[2]/table/tbody/tr")
        for controller_item in controller_info_list:
            td_list = controller_item.xpath("td")
            for index, each_item in enumerate(td_list):
                if index % 2 != 0:
                    words = each_item.xpath("text()").extract_first()
                    item["word"] = extract_pure_text(words)
                    yield item

        # # 高管信息
        top_manager_info_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[6]/div[2]/table/tbody/tr")
        # 高管信息以333分割来提取数据(依次是：职务、是否有基金从业资格、工作履历	)
        each_manager_info_list = [top_manager_info_list[i:i + 3] for i in range(0, len(top_manager_info_list), 3)]
        # 遍历每个高管的信息之后,提取返回。
        for each_info in each_manager_info_list:
            for index, each_manager_info in enumerate(each_info):
                if index == 2:
                    # 这里是 工作履历(单独处理)
                    for sub_index, each_item in enumerate(each_manager_info.xpath("td")):
                        if sub_index % 2 != 0:
                            # 遍历获取随时间推移身份变化的信息
                            for time_info in each_item.xpath("table/tbody/tr"):
                                for each_message in time_info.xpath("td"):
                                    words = each_message.xpath("text()").extract_first()
                                    if words is None:
                                        continue
                                    item["word"] = extract_pure_text(words)
                                    yield item
                else:
                    # 其余情况是基本信息
                    for sub_index, each_item in enumerate(each_manager_info.xpath("td")):
                        if sub_index % 2 != 0:
                            words = each_item.xpath("text()").extract_first()
                            item["word"] = extract_pure_text(words)
                            yield item

        # =============
        # 关联方信息
        # =============
        related_party_info_tr_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[7]/div[2]/table/tbody/tr/td[2]/table/tbody/tr")
        for td_list in related_party_info_tr_list:
            td_info_list = td_list.xpath("td")
            for index, td_info in enumerate(td_info_list):
                if index == 2:
                    item["word"] = td_info.xpath("a/text()").extract_first()
                else:
                    item["word"] = td_info.xpath("text()").extract_first()
                yield item

        # =============
        # 出资人信息
        # =============
        investor_info_tr_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[8]/div[2]/table/tbody/tr/td[2]/table/tbody/tr")
        for td_info_list in investor_info_tr_list:
            for td_info in td_info_list.xpath("td"):
                item["word"] = td_info.xpath("text()").extract_first()
                yield item

        # =============
        # 产品信息
        # =============
        product_info_tr_list = detail_resp.xpath("/html/body/div[3]/div/div[4]/div[9]/div[2]/table/tbody/tr")
        for td_info_list in product_info_tr_list:
            for index, each_td_info in enumerate(td_info_list.xpath("td")):
                if index == 0:
                    item["word"] = each_td_info.xpath("text()").extract_first()
                    yield item
                else:
                    inner_table_fund_list = each_td_info.xpath("table/tbody/tr")
                    for each_fund_td_list in inner_table_fund_list:
                        fund_name = each_fund_td_list.xpath("td")[0].xpath("a/text()").extract_first()
                        item["word"] = fund_name
                        yield item

        # =============
        # 诚信信息基本没有,暂不爬取
        # =============
        pass


# 2.3券商集合资管
class CSec23Spider(BaseSpider):
    """
    券商集合资管
    https://gs.amac.org.cn/amac-infodisc/res/pof/securities/index.html
    """
    name = 'c_sec'
    payload = {}
    total_pages = None

    def start_requests(self):
        super().start_requests()
        return [scrapy.Request(method="POST",
                               url=self.start_urls[2],
                               headers={'Content-Type': 'application/json'},
                               body=json.dumps(self.payload),
                               callback=self.parse)]

    def parse(self, response, **kwargs):
        """
        解析列表页
        """
        # 获取总页码并设置给类变量
        if self.total_pages is None:
            self.total_pages = int(json.loads(response.text)["totalPages"])
        # 当前页码
        current_page = int(json.loads(response.text)["number"])
        res_list_data = json.loads(response.text)["content"]
        for each_data in res_list_data:
            item = CSec23Item()
            item['parent'] = each_data["cpmc"]
            item['cat'] = 'list'
            item['word'] = each_data["cpbm"]
            item['word_level'] = 120
            item['pos'] = 'n'
            yield item
            item['word'] = each_data["gljg"]
            (yield item) if (item['word'] != "") else None
            # 解析详情页
            yield scrapy.Request(
                url="https://gs.amac.org.cn/amac-infodisc/api/pof/securities/{}?rand=0.9961366627436694".format(each_data["id"]),
                meta=item,
                callback=self.parse_detail
            )

        # 爬取下一页
        print("2-3当前的页码是 ", current_page)
        if current_page < self.total_pages:
            yield scrapy.Request(
                method="POST",
                url='https://gs.amac.org.cn/amac-infodisc/api/pof/securities?rand=0.772200358104348&page={}&size=20'.format(
                    current_page + 1),
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.payload),
                callback=self.parse
            )

    def parse_detail(self, response):
        """
        券商集合资管详细信息
        """
        # print("detail_response是", response)
        detail_meta = response.meta
        item = CSec23Item()
        item["parent"] = detail_meta["parent"]
        item['cat'] = 'detail'
        item["word"] = 'word'
        item['word_level'] = 119
        item['pos'] = 'n'
        detail_resp = json.loads(response.text)
        del detail_resp["barq"]
        del detail_resp["dqr"]
        del detail_resp["slrq"]
        del detail_resp["sffj"]
        for k, v in detail_resp.items():
            item["word"] = v
            yield item


# 2.4证券公司私募产品
class CSec24Spider(BaseSpider):
    """
    证券公司私募产品
    https://gs.amac.org.cn/amac-infodisc/res/pof/subfund/index.html
    """
    name = 'c_sec'
    payload = {}
    total_pages = None

    def start_requests(self):
        super().start_requests()
        return [scrapy.Request(method="POST",
                               url=self.start_urls[3],
                               headers={'Content-Type': 'application/json'},
                               body=json.dumps(self.payload),
                               callback=self.parse)]

    def parse(self, response, **kwargs):
        """
        解析列表页
        """
        # 获取总页码并设置给类变量
        if self.total_pages is None:
            self.total_pages = int(json.loads(response.text)["totalPages"])
        # 当前页码
        current_page = int(json.loads(response.text)["number"])
        res_list_data = json.loads(response.text)["content"]
        for each_data in res_list_data:
            item = CSec24Item()
            item['parent'] = each_data["productName"]
            item['cat'] = 'list'
            item['word'] = each_data["productCode"]
            item['word_level'] = 120
            item['pos'] = 'n'
            yield item
            item['word'] = each_data["mgrName"]
            yield item
            if not (each_data["trustee"] is None or each_data["trustee"] == ""):
                item['word'] = each_data["trustee"]
                yield item

            # 解析详情页
            yield scrapy.Request(
                url="https://gs.amac.org.cn/amac-infodisc/res/pof/subfund/{}.html".format(each_data["id"]),
                meta=item,
                callback=self.parse_detail
            )

        # 爬取下一页
        print("2-4当前的页码是 ", current_page)
        if current_page < self.total_pages:
            # if current_page < self.total_pages:
            yield scrapy.Request(
                method="POST",
                url='https://gs.amac.org.cn/amac-infodisc/api/pof/subfund?rand=0.9369420809918476&page={}&size=20'.format(
                    current_page + 1),
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.payload),
                callback=self.parse
            )

    def parse_detail(self, response):
        """
        解析证券公司私募产品的详情
        """
        detail_meta = response.meta
        item = CSec24Item()
        item["parent"] = detail_meta["parent"]
        item['cat'] = 'detail'
        item["word"] = 'word'
        item['word_level'] = 119
        item['pos'] = 'n'
        detail_response = response
        detail_tr_info_list = detail_response.xpath("/html/body/div[3]/div/div[2]/div/div/table/tbody/tr")
        for detail_td_info_list in detail_tr_info_list:
            words = detail_td_info_list.xpath("td")[1].xpath("text()").extract_first()
            if not (words is None or words == ""):
                item["word"] = extract_pure_text(words)
                yield item
