"""
中国证券投资基金的爬虫相关配置
"""
c_sec_default = {
    'allowed_domains': ['gs.amac.org.cn'],
    'start_urls': [
        # 2.1基金协会会员单位
        'https://gs.amac.org.cn/amac-infodisc/api/pof/pofMember?rand=0.033337234974890606&page=0&size=1',
        # 2.2私募基金管理人产品
        'https://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.33221000223311026&page=625&size=20',
        # 2.3券商集合资管
        'https://gs.amac.org.cn/amac-infodisc/api/pof/securities?rand=0.772200358104348&page=0&size=20',
        # 2.4证券公司私募产品
        'https://gs.amac.org.cn/amac-infodisc/api/pof/subfund?rand=0.9369420809918476&page=0&size=20',
        # 2.5私募基金管理人
        # 'https://gs.amac.org.cn/amac-infodisc/api/pof/manager?rand=0.6918348942272805&page=0&size=10',
    ],
}
