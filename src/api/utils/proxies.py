from fp.fp import FreeProxy

fosyclub_proxies = "https://fosy.club/api/free/list?type=http"
free_cz = "http://free-proxy.cz/en/proxylist/country/all/https/ping/level1"
proxy_daily = "https://proxy-daily.com/"
mega_proxy = "https://www.megaproxylist.net/"
prxoydocker = "https://www.proxydocker.com/en/proxylist/type/https"
proxyscraper = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&amp;anonymity=elite&amp;timeout=15000&amp;proxy_format=ipport&amp;format=json"
proxy_list = "https://www.proxy-list.download/HTTPS"


def get_proxies():
    return FreeProxy(timeout=1, https=True, elite=True).get()
