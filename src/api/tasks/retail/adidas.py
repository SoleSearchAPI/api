import json
import logging
import re
from datetime import datetime
from pathlib import Path

import requests

from core.models.shoes import Adidas as AdidasShoe
from ingest.models.json import Ingest


class AdidasIngest(Ingest):
    def __init__(self):
        super().__init__(
            brand="Adidas", download_url="https://www.adidas.com/us/release-dates"
        )

    def download(self) -> None:
        r = requests.get(
            url=self.download_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Cookie": "geo_ip=100.34.208.118; geo_country=US; onesite_country=US; akacd_Phased_www_adidas_com_Generic=3879262350~rv=12~id=6b039c5cdafbe0d8f327190cfbef53ad; adidas_country=us; gl-feat-enable=CHECKOUT_PAGES_ENABLED; badab=true; akacd_phased_PDP=3879262350~rv=26~id=72124c30227ac1464f4164d1c5c26bd2; notice_preferences=2; x-original-host=adidas.co.uk; x-site-locale=en_GB; mt.v=0.211842328.1701809553231; wishlist=%5B%5D; AMCVS_7ADA401053CCF9130A490D4C%40AdobeOrg=1; ab_qm=b; ab_inp=a; s_cc=true; QSI_SI_1HBh4b3ZpUvgHMV_intercept=true; x-commerce-next-id=11101d76-0b32-434c-8ac9-2c5fc104dccf; persistentBasketCount=0; userBasketCount=0; notice_preferences=2; pagecontext_cookies=; pagecontext_secure_cookies=; s_sess=%5B%5BB%5D%5D; newsletterShownOnVisit=true; geo_state=PA; geo_coordinates=lat=40.1156, long=-74.8582; checkedIfOnlineRecentlyViewed=true; UserSignUpAndSave=4; s_pers=%20s_vnum%3D1704085200938%2526vn%253D1%7C1704085200938%3B%20s_invisit%3Dtrue%7C1701812642822%3B; AMCV_7ADA401053CCF9130A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C19697%7CMCMID%7C31097539932472422145926103310509822013%7CMCAID%7CNONE%7CMCOPTOUT-1701818042s%7CNONE; utag_main=v_id:018c3bc101450013d6f9829feaac04075001906d008c0$_sn:1$_se:16%3Bexp-session$_ss:0%3Bexp-session$_st:1701812641852%3Bexp-session$ses_id:1701809553736%3Bexp-session$_pn:5%3Bexp-session$_vpn:5%3Bexp-session$_prevpage:RELEASE%20CALENDAR%7CRELEASE-CALENDAR%3Bexp-1701814442768$ttdsyncran:1%3Bexp-session$dcsyncran:1%3Bexp-session$dc_visit:1$dc_event:5%3Bexp-session$ab_dc:TEST%3Bexp-1706994841983; bm_sz=4DEB611AEDD479D1EEFFB452313C8BDE~YAAQSiTDF3bvHyGMAQAAyCN8PRZBKVXaGX+qMTwWWcrFxU3M3BxoGG2vkWHrxe2RsL+yrUXK6Bz6ZW2qCxQ3kNpfYsYEsRvad0w5gi8N+EPS+D/3WKW1TRlVm0QBnKOtnK6AbE3oQhiMBh7lxfsUBCUSd5rqtV+QXklSam+CohWELJWelFKi/OEZ++WszYq2CebURLT8l75W8kpI16GEcLtrlAY34C2VyktM4ZxTofwT1ZNrfkUP6XaodjYLFp4soBbZXycF/Y7JeMUqrxe7an6BfgQgdMy//2XIanTuhikpWX6+Oh1THf+f7I0lFEBwMR+FUEzKz9On1fyFKmk2FIREzYWNgueEm6Uy6VG4SUqSy8ZXJ+y2soENYcpsUtVXQq8KsqRwwr6Ux+AcR1YLs2/Yl91a9T44Zk8ffcvlOlSuVf5ITt60W6iOiCF6~3355702~3294263; _abck=EBFA1A89F552EC3779E06BEAAD348FD7~-1~YAAQSiTDF2jwHyGMAQAADSl8PQsB6xCt0mEVHp2Mdor9S6Jy22cuq6Q/BL/8eiyHjA7stokpqjKAT1kcZgqjmSZ0aZ8LdhHpbWAUcj1Geq9XzLCihJvMq7yiyA+k6rF0ew0TdN7MkHlhxSWk6MLE5VeBeRazCOYthqtJnDnRjEk66/puN/fTlUFmclblgRjhICXOBMpJRkpDtAJI1UQK+tsvppt1iXborhU3/D78EvxlPnWGnCJbst1dp7jUuu8+tVC0G0k9pb7+HpnJL2bgKemQEDUBXEUD4pX1rbxNUIJefvHC6vAdH/N3hvp67+L/IO4Bu2szy9wAtnaiDnWpM7tVzMVmXUVM5iUH4TsONN12xkgVTAi/H09DEtM0RAzY4Bp/xXIOUoNXefnJGLNYmm131pgAzfI75sae/6nU08PhB6Zbr2qqu3EkiQu39tlfwc0Znw/m+IGUZw==~-1~-1~1701842138; sbsd=sfIonmPL8eEMWK7/7M0O0LF7jmW7kCLc01sYxwJ7aDBJpov6EbF3IfsRQOXGSEFs49+6rGXGA1bq8FE/QKJqn7YBMDWTBOpK4loOkwTdAso/1o7PYO/Oowe9sSSa20WwYBzlUIMWg6duy9hNITY+AmA==; ak_bmsc=4A68BEF64B798971B5792E66D28095D7~000000000000000000000000000000~YAAQSiTDFyHzHyGMAQAAbjR8PRYY+x4wsrapXloYPlmUCWvbZNBD5e0/NINjpnkflWMqP/av2vW3F37EWp6B1ZqMymcGcEg08z524EIljO/RDcuxbwNFZ9bdTxcr5eoFuePj07IStDc+Zq/GR9qKaMkhSxN9V4swRGq0TIc8MH4d/huA1ep0a+lhirWayNByPMfUo0EqBccCZ2tsLVexL6GFVzaiPqQmOGNokYbuer+DzUIz6yJRBMK2R/SO43aC7LuLltBySTQYW0Sc9VNmg6Pz+X/+2a7aWjt46moYK8utFu5CpTz2QKt7I5q9qlrrQx1FOAnD1VH7qCPsumV683y96YjR1uTIKaFS2o1hLXPiY0ktjQTlHHEmdYeJc/bwibom54Uypr5P",
                "Accept ": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Cache-Control": "max-age=0",
            },
        )
        if r.status_code == 200:
            with open(file=self.paths["html"], mode="w", encoding="utf-8") as html_file:
                html_file.write(r.text)
        else:
            raise ConnectionError(
                f"Failed to retrieve {self.download_url}, status code {r.status_code}"
            )

    def extractor(self, input):
        pattern = re.compile(
            r"<script>\s*window.DATA_STORE\s*=\s*JSON.parse\s*\(\s*[\'\"](.*?)[\'\"]\s*\)\s*;\s*</script>",
            re.DOTALL,
        )
        react_data = pattern.search(input).group(1)
        return react_data

    def ingest(self):
        pass
