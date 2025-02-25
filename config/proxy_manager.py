import json
import os
from typing import List, Dict, Tuple


class ProxyManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "proxies.json")
        self._proxies = None  # 延迟加载
        self.page_size = 100  # 每页显示数量

    @property
    def proxies(self) -> List[Dict]:
        if self._proxies is None:
            self._proxies = self.load_proxies()
        return self._proxies

    def load_proxies(self) -> List[Dict]:
        """加载代理配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_proxies(self, proxies: List[Dict]) -> bool:
        """保存代理配置"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(proxies, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def get_page(self, page: int) -> Tuple[List[Dict], int]:
        """获取指定页的代理数据和总页数"""
        start = (page - 1) * self.page_size
        end = start + self.page_size
        total_pages = (len(self.proxies) + self.page_size - 1) // self.page_size
        return self.proxies[start:end], total_pages

    def search_proxies(self, keyword: str = "", ads_id: str = "") -> List[Dict]:
        """搜索代理
        Args:
            keyword: 通用关键字搜索
            ads_id: 广告ID搜索
        """
        results = self.proxies
        if ads_id:
            results = [
                proxy
                for proxy in results
                if str(proxy.get("ads_id", "")).lower() == ads_id.lower()
            ]
        if keyword:
            results = [
                proxy for proxy in results if keyword.lower() in str(proxy).lower()
            ]
        return results


proxy_manager = ProxyManager()
