from typing import List

import requests

from app.log import logger


class Torrent:
    id: int = 0
    site: str = ""
    code: str = ""
    size_mb: float = 0
    seeders: int = 0
    title: str = ""
    chinese: bool = False
    uc: bool = False

    cn_keywords: List[str] = ['中字', '中文字幕', '色花堂', '字幕']
    uc_keywords: List[str] = ['UC', '无码', '步兵']

    def __init__(self, id, site, code, size_mb, seeders, title):
        self.id = id
        self.site = site
        self.code = code
        self.size_mb = size_mb
        self.seeders = seeders
        self.title = title
        self.chinese = self.has_chinese(title)
        self.uc = self.has_uc(title)

    def has_chinese(self, title: str):
        has_chinese = False
        for keyword in self.cn_keywords:
            if title.find(keyword) > -1:
                has_chinese = True
                break
        return has_chinese

    def has_uc(self, title: str):
        uc = False
        for keyword in self.uc_keywords:
            if title.find(keyword) > -1:
                uc = True
                break
        return uc


def sort_torrents(torrents: List[Torrent]):
    upload_sort_list = sorted(torrents, key=lambda torrent: torrent.seeders, reverse=True)
    cn_sort_list = sorted(upload_sort_list, key=lambda torrent: torrent.chinese, reverse=True)
    uc_sort_list = sorted(cn_sort_list, key=lambda torrent: torrent.uc, reverse=True)
    return uc_sort_list


def filter_torrents(torrents: List[Torrent], max_size, min_size, only_chinese=False, only_uc=False):
    filter_list = []
    for torrent in torrents:
        size_mb = torrent.size_mb
        if not size_mb:
            continue
        if max_size:
            if size_mb > max_size:
                continue
        if min_size:
            if size_mb < min_size:
                continue
        if only_chinese:
            if not torrent.chinese:
                continue
        if only_uc:
            if not torrent.uc:
                continue
        filter_list.append(torrent)
    return filter_list


class FSM:
    site_name: str = "飞天拉面神教"
    # 站点域名
    site_domain: str = "https://api.fsm.name"
    # 站点API密钥
    site_api_key: str = ""
    # 站点passkey
    site_passkey: str = ""

    def __init__(self, api_key, passkey):
        self.site_api_key = api_key
        self.site_passkey = passkey
        pass

    def search(self, keyword) -> List[Torrent]:
        search_url = f"{self.site_domain}/Torrents/listTorrents?keyword={keyword}&page=1&type=AV&systematics=0&tags=[]"
        headers = {
            'APITOKEN': self.site_api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"飞天拉面神教请求失败:{response.status_code}")
            return []
        data = response.json()
        fsm_torrents = data['data']['list']
        torrents = []
        for fsm_torrent in fsm_torrents:
            torrents.append(self.convert_torrent(keyword, fsm_torrent))
        return torrents

    def get_torrent_download_url(self, tid):
        download_url = f"{self.site_domain}/Torrents/download?tid={tid}&passkey={self.site_passkey}&source=direct"
        return download_url

    def convert_torrent(self, code, fsm_torrent):
        torrent = Torrent(
            id=fsm_torrent['tid'],
            site=self.site_name,
            code=code,
            size_mb=int(fsm_torrent['fileRawSize']) / 1024 / 1024,
            seeders=int(fsm_torrent['peers']['upload']),
            title=fsm_torrent['title']
        )
        return torrent

    def is_valid(self):
        return self.site_api_key and self.site_passkey


class MTeam:
    site_name: str = "馒头"
    # 站点域名
    site_domain: str = "https://kp.m-team.cc"
    # 站点API密钥
    site_api_key: str = ""

    def __init__(self, api_key):
        self.site_api_key = api_key
        pass

    def search(self, keyword) -> List[Torrent]:
        reqPayload = {
            "mode": "adult",
            "categories": ["410", "429"],
            "visible": 1,
            "keyword": keyword,
            "pageNumber": 1,
            "pageSize": 100
        }
        headers = {
            'x-api-key': self.site_api_key,
        }
        response = requests.post(f"{self.site_domain}/api/torrent/search", json=reqPayload, headers=headers)
        if response.status_code != 200:
            logger.error(f"馒头请求失败:{response.status_code}")
            return []
        data = response.json()
        if int(data['code']) == 1:
            logger.error(f"馒头搜索报错:{data['message']}")
            return []
        if int(data['code']) == 0:
            mteam_torrents = data['data']['data']
            torrents = []
            for mteam_torrent in mteam_torrents:
                torrents.append(self.convert_torrent(keyword, mteam_torrent))
            return torrents
        return []

    def get_torrent_download_url(self, id):
        reqPayload = {
            "id": id
        }
        headers = {
            'x-api-key': self.site_api_key,
        }
        response = requests.post(f"{self.site_domain}/api/torrent/genDlToken", data=reqPayload, headers=headers)
        data = response.json()
        if data['code'] == 1:
            logger.error(f"馒头获取下载链接报错:{data['message']}")
            return None
        logger.info(f"馒头获取下载链接结果:{data}")
        return data['data']

    def convert_torrent(self, code, mteam_torrent):
        torrent = Torrent(
            id=mteam_torrent['id'],
            site=self.site_name,
            code=code,
            size_mb=int(mteam_torrent['size']) / 1024 / 1024,
            seeders=int(mteam_torrent['status']['seeders']),
            title=f"{mteam_torrent['name']} {mteam_torrent['smallDescr']}"
        )
        return torrent

    def is_valid(self):
        return self.site_api_key
