from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional

import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase
from plugins.autolittersister.mediaserver import Emby, Plex, Jellyfin
from plugins.autolittersister.scraper import JavLibrary
from plugins.autolittersister.site import Torrent, FSM, MTeam, sort_torrents, filter_torrents


class AutoLitterSister(_PluginBase):
    plugin_name = "小姐姐自己动"
    # 插件描述
    plugin_desc = ""
    # 插件图标
    plugin_icon = "Melody_A.png"
    # 插件版本
    plugin_version = "0.0.11"
    # 插件作者
    plugin_author = "envyafish"
    # 作者主页
    author_url = "https://github.com/envyafish"
    # 插件配置项ID前缀
    plugin_config_prefix = "autolittersister_"
    # 加载顺序
    plugin_order = 0
    # 可使用的用户级别
    auth_level = 2

    _enabled: bool = False,
    _notify: bool = True,
    _mteam_api_key: str = ""
    _fsm_api_key: str = ""
    _fsm_passkey: str = ""
    _emby_server: str = ""
    _emby_api_key: str = ""
    _jellyfin_server: str = ""
    _jellyfin_api_key: str = ""
    _jellyfin_user: str = ""
    _plex_server: str = ""
    _plex_token: str = ""
    _brush: bool = False
    _only_chinese: bool = False
    _only_uc: bool = False
    _min_mb: int = None
    _max_mb: int = None
    _top: int = 1
    _once: bool = False
    _cron: str = "0 20 * * *"

    _scheduler: Optional[BackgroundScheduler] = None
    _config = {}

    def init_plugin(self, config: dict = None):
        self._config = config
        self._enabled = config.get("enabled", False)
        self._notify = config.get("notify", False)
        self._mteam_api_key = config.get("mteam_api_key", "")
        self._fsm_api_key = config.get("fsm_api_key", "")
        self._fsm_passkey = config.get("fsm_passkey", "")
        self._emby_server = config.get("emby_server", "")
        self._emby_api_key = config.get("emby_api_key", "")
        self._jellyfin_server = config.get("jellyfin_server", "")
        self._jellyfin_api_key = config.get("jellyfin_api_key", "")
        self._jellyfin_user = config.get("jellyfin_user", "")
        self._plex_server = config.get("plex_server", "")
        self._plex_token = config.get("plex_token", "")
        self._brush = config.get("brush", False)
        self._only_chinese = config.get("only_chinese", False)
        self._only_uc = config.get("only_uc", False)
        self._min_mb = config.get("min_mb")
        self._max_mb = config.get("max_mb")
        self._top = config.get("top", 1)
        self._once = config.get("once", False)
        self._cron = config.get("cron", "")
        if self._enabled and self._once:
            if self._once:
                self._config["once"] = False
                self.update_config(self._config)
                self._scheduler = BackgroundScheduler(timezone=settings.TZ)
                logger.info("3秒后立即来一下")
                self.main()
                # self._scheduler.add_job(func=self.main, trigger='date',
                #                         run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                #                         name="小姐姐自己动")
                # if self._scheduler.get_jobs():
                #     self._scheduler.print_jobs()
                #     self._scheduler.start()

    pass

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify',
                                            'label': '发送通知',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'once',
                                            'label': '来一下',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'cron',
                                            'label': '定时执行,cron表达式',
                                        }
                                    }
                                ]
                            },

                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'brush',
                                            'label': '洗版',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'only_chinese',
                                            'label': '仅中文',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'only_uc',
                                            'label': '仅步兵',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'top',
                                            'label': '榜单选择',
                                            'items': [
                                                {"title": "TOP20", "value": 1},
                                                {"title": "TOP40", "value": 2},
                                                {"title": "TOP60", "value": 3},
                                                {"title": "TOP80", "value": 4},
                                                {"title": "TOP100", "value": 5}
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '1.无论是否开启洗版，都会进行中文和步兵排序,优选种子\n'
                                                    '2.关闭洗版，将会强制过滤中文和步兵(若<仅中文>或者<仅步兵>开启)'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'min_mb',
                                            'label': '最小大小(MB)',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'max_mb',
                                            'label': '最大大小(MB)',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'mteam_api_key',
                                            'label': '馒头APIKEY',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'fsm_api_key',
                                            'label': '飞天拉面神教APIKEY',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'fsm_passkey',
                                            'label': '飞天拉面神教passkey',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'emby_server',
                                            'label': 'Emby地址',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'emby_api_key',
                                            'label': 'Emby APIKEY',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'plex_server',
                                            'label': 'Plex地址',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'plex_token',
                                            'label': 'Plex token',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'jellyfin_server',
                                            'label': 'Jellyfin地址',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'jellyfin_api_key',
                                            'label': 'Jellyfin APIKEY',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'jellyfin_user',
                                            'label': 'Jellyfin 用户',
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "notify": False,
            "mteam_api_key": "",
            "fsm_api_key": "",
            "fsm_passkey": "",
            "emby_server": "",
            "emby_api_key": "",
            "jellyfin_server": "",
            "jellyfin_api_key": "",
            "jellyfin_user": "",
            "plex_server": "",
            "plex_token": "",
            "brush": False,
            "only_chinese": False,
            "only_uc": False,
            "min_mb": None,
            "max_mb": None,
            "top": 1,
            "once": False,
            "cron": "0 20 * * *"
        }

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        pass

    def main(self):
        library = JavLibrary()
        emby = Emby(self._emby_api_key, self._emby_server)
        plex = Plex(self._plex_server, self._plex_token)
        jellyfin = Jellyfin(self._jellyfin_server, self._jellyfin_api_key, self._jellyfin_user)
        fsm = FSM(self._fsm_api_key, self._fsm_passkey)
        mteam = MTeam(self._mteam_api_key)
        codes = library.crawling_top20(self._top)
        exist_codes = []
        for code in codes:
            if emby.is_valid():
                movie = emby.search(code)
                if movie:
                    exist_codes.append(code)
                    continue
            if plex.is_valid():
                movie = plex.search(code)
                if movie:
                    exist_codes.append(code)
                    continue
            if jellyfin.is_valid():
                movie = jellyfin.search(code)
                if movie:
                    exist_codes.append(code)
                    continue
        un_exist_codes = list(set(codes) - set(exist_codes))
        logger.info(f"未找到的番号:{un_exist_codes}")
        for code in un_exist_codes:
            logger.info(f"开始搜索番号:{code}")
            torrents: List[Torrent] = []
            if fsm.is_valid(): torrents.extend(fsm.search(code))
            if mteam.is_valid(): torrents.extend(mteam.search(code))
            logger.info(f"搜索结果:{len(torrents)}条")
            for torrent in torrents:
                logger.info(
                    f"站点:{torrent.site}|标题:{torrent.title}|大小：{torrent.size_mb}MB|做种数：{torrent.seeders}")
            torrents = filter_torrents(torrents, max_size=8000, min_size=3000, only_chinese=False, only_uc=False)
            logger.info(f"过滤后结果:{len(torrents)}条")
            for torrent in torrents:
                logger.info(
                    f"站点:{torrent.site}|标题:{torrent.title}|大小：{torrent.size_mb}MB|做种数：{torrent.seeders}")
            torrents = sort_torrents(torrents)
            logger.info(f"排序后结果:{len(torrents)}条")
            for torrent in torrents:
                logger.info(
                    f"站点:{torrent.site}|标题:{torrent.title}|大小：{torrent.size_mb}MB|做种数：{torrent.seeders}")
            if torrents:
                torrent = torrents[0]
                download_url = mteam.get_torrent_download_url(
                    torrent.id) if torrent.site == mteam.site_name else fsm.get_torrent_download_url(torrent.id)
                if download_url:
                    logger.info(
                        f"命中种子ID:{torrent.id}|站点:{torrent.site}|标题:{torrent.title}|大小：{torrent.size_mb}MB|做种数：{torrent.seeders}")
                    logger.info(f"下载链接:{download_url}")
