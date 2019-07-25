import requests

from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class DetectorAssetConstant:
    def __init__(self):
        self.page_asset = {
            'vtv.vn': {
                'article_links': [
                    'http://vtv.vn/the-thao/vdv-viet-nam-gap-su-co-dang-tiec-trong-tran-chung-ket-pencak-silat-20170829130631776.htm',
                    'http://vtv.vn/truyen-hinh/dan-btv-noi-tieng-no-nuc-doi-anh-dai-dien-mung-sinh-nhat-vtv-tuoi-47-20170830093555214.htm',
                    'http://vtv.vn/truyen-hinh/park-min-young-bat-tay-voi-bo-doi-running-man-trong-show-truyen-hinh-moi-cua-netflix-20170829153537885.htm'
                ],
                'non_article_links': [
                    'http://vtv.vn/the-thao/bong-da-quoc-te.htm',
                    'http://vtv.vn/giao-duc.htm',
                    'http://vtv.vn/goc-khan-gia.htm'
                ],
                'css_selectors': [
                    {
                        'is_article': '#admWrapsite .noidung h1.title_detail',
                        'title': '#admWrapsite .noidung h1.title_detail',
                        'description': '#admWrapsite .noidung h2.sapo',
                        'main_content': '#admWrapsite .noidung div.ta-justify',
                        'published_at': '#admWrapsite .noidung .time',
                        'junk_data': ['.VCSortableInPreviewMode']
                    }
                ]
            },
            'tuoitre.vn': {
                'article_links': [
                    'http://tuoitre.vn/thu-the-nha-bao-pho-tong-bien-tap-bao-thanh-nien-1230895.htm',
                    'http://tuoitre.vn/mac-du-luan-ngoi-nha-bi-thu-ba-ria-tiep-tuc-duoc-thi-cong-1378483.htm',
                    'http://tuoitre.vn/tai-nan-lien-hoan-duong-noi-cac-kcn-binh-duong-roi-loan-1377919.htm'
                ],
                'non_article_links': [
                    'http://tuoitre.vn/phap-luat.htm', 'http://tuoitre.vn/nhip-song-tre.htm',
                    'http://tuoitre.vn/giai-tri.htm'
                ],
                'css_selectors': [
                    {
                        'is_article': '#admWrapsite .left-side .title-2',
                        'title': '#admWrapsite .left-side .title-2',
                        'description': '#admWrapsite .left-side .txt-head',
                        'main_content': '#admWrapsite .left-side .fck',
                        'published_at': '#admWrapsite .left-side .date',
                        'junk_data': []
                    }
                ]
            },
            'kenh14.vn': {
                'article_links': [
                    'http://kenh14.vn/6-phim-han-hiem-hoi-so-huu-dan-sao-nu-dep-den-lang-nguoi-20170824225216064.chn',
                    'http://kenh14.vn/chang-bao-gio-khoa-truong-nhung-khoi-tai-san-kech-xu-cua-hat-ung-hoang-phuc-cung-khong-phai-dang-vua-dau-2017082315312997.chn',
                    'http://kenh14.vn/khi-sep-em-nhiem-ngon-tinh-20170829101032906.chn',
                    'http://kenh14.vn/sau-7-nam-shin-se-kyung-da-chiu-len-tieng-ve-cai-ket-cua-high-kick-2-20170829090547547.chn'
                ],
                'non_article_links': [
                    'http://kenh14.vn/tram-yeu.chn', 'http://kenh14.vn/the-gioi.chn', 'http://kenh14.vn/thiet-hai-do-bao-harvey.html'
                ],
                'css_selectors': [
                    {
                        'is_article': '.adm-mainsection .kbw-content .kbwc-title',
                        'title': '.adm-mainsection .kbw-content .kbwc-title',
                        'description': '.kbw-content .klw-new-content .knc-sapo',
                        'main_content': '.kbw-content .klw-new-content .knc-content',
                        'published_at': '.kbw-content .kbwcm-time',
                        'junk_data': ['.knc-rate-link']
                    }
                ]
            },
            'www.vietnamplus.vn': {
                'article_links': [
                    'http://www.vietnamplus.vn/thu-tuong-lao-gui-dien-tham-hoi-tinh-hinh-mua-lu-tai-viet-nam/460653.vnp',
                    'http://www.vietnamplus.vn/thuong-257-ty-dong-cho-85-cong-trinh-toan-hoc-nam-2016/460741.vnp',
                ],
                'non_article_links': [
                    'http://www.vietnamplus.vn/chinhtri.vnp', 'http://www.vietnamplus.vn/xahoi.vnp',
                    'http://www.vietnamplus.vn/timkiem/Sai-gon.vnp', 'http://www.vietnamplus.vn/chude/viet-namcampuchia/218.vnp'
                ],
                'css_selectors': [
                    {
                        'is_article': 'header.article-header > .cms-title',
                        'title': 'header.article-header > .cms-title',
                        'description': '',
                        'main_content': 'article div.article-body',
                        'published_at': 'header.article-header time',
                        'junk_data': []
                    }
                ]
            },
            'baodongthap.vn': {
                'article_links': [
                    'http://baodongthap.vn/newsdetails/1D3FE18E535/Hai_bi_cao_gay_tai_nan_giao_thong_bi_phat_tu.aspx',
                    'http://baodongthap.vn/newsdetails/1D3FE18E539/Bo_truong_Phung_Xuan_Nha_Quyet_quy_hoach_lai_cac_truong_Su_pham.aspx',
                ],
                'non_article_links': [
                    'http://baodongthap.vn/newslist/4AE0F99B8/Phap_luat.aspx',
                    'http://baodongthap.vn/newslist/4AE0F99BE/Giao_duc.aspx',
                    'http://baodongthap.vn/ketquatimkiem.aspx?keyword=Sai%20gon'
                ],
                'css_selectors': [
                    {
                        'is_article': '.home-col-left .pageListLeft .view-page-Tit',
                        'title': '.home-col-left .pageListLeft .view-page-Tit',
                        'description': '',
                        'main_content': '.home-col-left .pageListLeft',
                        'published_at': '.pageListLeft .date span',
                        'junk_data': ['#brMenu', '.view-page-Tit', 'div', 'script']
                    }
                ]
            },
            'giaoduc.net.vn': {
                'article_links': [
                    'http://giaoduc.net.vn/Quoc-te/Kim-Jongun-da-lat-bai-ngua-lua-chon-nao-cho-Donald-Trump-post178888.gd',
                    'http://giaoduc.net.vn/Van-hoa/Ong-cap-phep-hat-Quoc-ca-ve-Van-phong-Bo-post177014.gd',
                    'http://giaoduc.net.vn/Xa-hoi/Ha-Noi-da-cat-giam-39-truong-phong-143-pho-phong-trong-6-thang-dau-nam-post178988.gd'
                ],
                'non_article_links': [
                    'http://giaoduc.net.vn/Quoc-te/16.gd', 'http://giaoduc.net.vn/Van-hoa/20.gd',
                    'http://giaoduc.net.vn/tim-kiem/Sai-gon.gd', 'http://giaoduc.net.vn/tag/nguy%E1%BB%85n-%C4%91%C4%83ng-ch%C6%B0%C6%A1ng.gd'
                ],
                'css_selectors': [
                    {
                        'is_article': 'h1.title.cms-title',
                        'title': 'h1.title.cms-title',
                        'description': '.summary.cms-desc',
                        'main_content': 'div.body.cms-body',
                        'published_at': 'time.cms-date',
                        'junk_data': ['.notebox.cms-relate.nleft']
                    }
                ]
            },
            'phanbonhalan.com': {
                'article_links': [
                    'http://phanbonhalan.com/vi/tin-noi-bo/ton-vinh---phan-bon-ha-lan---san-pham-chat-luong-cho-mua-boi-thu--2017-526',
                    'http://phanbonhalan.com/vi/tin-noi-bo/chu-tich-hoi-ndvn--uy-vien-trung-uong-dang---lai-xuan-mon-tham-quan-nha-may-phan-bon-ha-lan-528',
                    'http://phanbonhalan.com/vi/ky-thuat-bon-phan/phan-bon-la-thuc-an-cua-cay-trong-130'
                ],
                'non_article_links': [
                    'http://phanbonhalan.com/vi/truyen-thong/tuyen-dung-145',
                    'http://phanbonhalan.com/vi/truyen-thong/thu-vien-152',
                    'http://phanbonhalan.com/vi/truyen-thong/lien-he-221'
                ],
                'css_selectors': [
                    {
                        'is_article': '#divTechWrapper .article-content .title-heading',
                        'title': '#divTechWrapper .article-content .title-heading',
                        'description': '#divTechWrapper .article-content .box-des-detail',
                        'main_content': '#divTechWrapper .article-content div:nth-of-type(2)',
                        'published_at': '',
                        'junk_data': []
                    }
                ]
            },
            'phanbonbamien.com': {
                'article_links': [
                    'http://phanbonbamien.com/nhung-ky-thuat-bon-phan-cho-lua-dat-nang-suat-cao.html',
                    'http://phanbonbamien.com/nhung-dich-benh-hai-can-chu-y-trong-tuan-tu-8-145.html',
                    'http://phanbonbamien.com/san-xuat-tieu-huu-co.html'
                ],
                'non_article_links': [
                    'http://phanbonbamien.com/kho-hang',
                    'http://phanbonbamien.com/hoa-chat-phan-bon',
                    'http://phanbonbamien.com/tin-tuc', 'http://phanbonbamien.com/lien-he'
                ],
                'css_selectors': [
                    {
                        'is_article': '#main .main-content #content .entry-title',
                        'title': '#main .main-content #content .entry-title',
                        'description': '',
                        'main_content': '#main .main-content #content .entry-content',
                        'published_at': '',
                        'junk_data': []
                    }
                ]
            },
            'nongviet.com.vn': {
                'article_links': [
                    'http://nongviet.com.vn/san-pham/phan-hon-hop-npk/npk-18-8-18.html',
                    'http://nongviet.com.vn/san-pham/phan-trung-vi-luong/phan-trung-vi-luong-tosy.html',
                    'http://nongviet.com.vn/san-pham/phan-hon-hop-npk/npk-18-8-18.html'
                ],
                'non_article_links': [
                    'http://nongviet.com.vn/san-pham/phan-trung-vi-luong.html',
                    'http://nongviet.com.vn/tu-van.html',
                    'http://nongviet.com.vn/khuyen-mai.html', 'http://nongviet.com.vn/lien-he.html'
                ],
                'css_selectors': [
                    {
                        'is_article': '#body .product-detail-tab-content',
                        'title': '#body .product-detail-title',
                        'description': '',
                        'main_content': '#body .product-detail-tab-content',
                        'published_at': '',
                        'junk_data': []
                    }
                ]
            },
            'quangnong.vn': {
                'article_links': [
                    'http://quangnong.vn/trong-dua-kim-hoang-hau-lai-8-trieu-dsao-1-2-2029338.html',
                    'http://quangnong.vn/tron-nang-nong-dan-ra-dong-lam-viec-tu-nua-dem-1-2-2029035.html',
                    'http://quangnong.vn/dau-dau-mua-duoc-gia-1-2-2028459.html',
                    'http://quangnong.vn/trong-chanh-khong-hat-sieu-loi-nhuan-1-2-2028167.html'
                ],
                'non_article_links': [
                    'http://quangnong.vn/bo-sp-nileda-2-1-70019242.html',
                    'http://quangnong.vn/san-pham-cho-caosu-2-1-639819.html',
                    'http://quangnong.vn/tim_kiem/sp'
                ],
                'css_selectors': [
                    {
                        'is_article': '.benphai_2 .contentdetail.relative h1',
                        'title': '.benphai_2 .contentdetail.relative h1',
                        'description': '',
                        'main_content': '.benphai_2 .contentdetail.relative ._mota',
                        'published_at': '.benphai_2 .contentdetail.relative .chu_date',
                        'junk_data': []
                    }
                ]
            },
            'phanbondientrang.vn': {
                'article_links': [
                    'http://phanbondientrang.vn/san-pham/pg041-trichomix-azo-rau-mau-50kg-395.html',
                    'http://phanbondientrang.vn/san-pham/pg019-trichomixdt-lua-35kg-388.html',
                    'http://phanbondientrang.vn/tin-tuc/nghien-cuu-giai-phap-xu-ly-rom-nham-cai-thien-moi-truong-dat-trong-lua-o-dong-bang-song-cuu-long-93.html',
                    'http://phanbondientrang.vn/tin-tuc/tuyen-dung-nhan-vien-kcs-91.html',
                    'http://phanbondientrang.vn/tin-tuc/bai-bao-04-huong-moi-phong-tri-benh-dom-trang-dom-nau-cay-thanh-long-87.html',
                    'http://phanbondientrang.vn/cong-nghe/nam-gay-benh-tren-cay-ho-tieu-391.html'
                ],
                'non_article_links': [
                    'http://phanbondientrang.vn/hoi-dap.html', 'http://phanbondientrang.vn/cong-nghe.html',
                    'http://phanbondientrang.vn/ky-thuat/69/ky-thuat-canh-tac/'
                ],
                'css_selectors': [
                    {
                        'is_article': '.content_main .ten_sp_detail',
                        'title': '.content_main .ten_sp_detail',
                        'description': '',
                        'main_content': '#container .content',
                        'published_at': '',
                        'junk_data': []
                    },
                    {
                        'is_article': '#main .title_main1',
                        'title': '#main .title_main1',
                        'description': '',
                        'main_content': '#main .content_main',
                        'published_at': '',
                        'junk_data': []
                    }
                ]
            },
            'phanbonminhphat.vn': {
                'article_links': [
                    'http://phanbonminhphat.vn/tin-tuc-nguoi-trong-ca-phe-duoc-dam-bao-muc-lai-tren-35-5.html',
                    'http://phanbonminhphat.vn/tin-tuc-trao-hoc-bong-tai-tra-vinh-24.html',
                    'http://phanbonminhphat.vn/tin-tuc-bon-phan-cho-lua-1.html',
                    'http://phanbonminhphat.vn/tin-tuc-trao-hoc-bong-tai-tra-vinh-24.html'
                ],
                'non_article_links': [
                    'http://phanbonminhphat.vn/tin/4/ban-tin-minh-phat/',
                    'http://phanbonminhphat.vn/tin/2/nhip-cau-nha-nong/',
                    'http://phanbonminhphat.vn/tin/3/chinh-sach-xa-hoi/'
                ],
                'css_selectors': [
                    {
                        'is_article': '#listtin > h1',
                        'title': '#listtin > h1',
                        'description': '',
                        'main_content': '#listtin',
                        'published_at': '#listtin .time',
                        'junk_data': ['li', 'h1', '.time']
                    }
                ]
            },
            'phanbonnamviet.vn': {
                'article_links': [
                    'http://phanbonnamviet.vn/k%E1%BB%B9-thu%E1%BA%ADt-n%C3%B4ng-nghi%E1%BB%87p/item/1870-k%E1%BB%B9-thu%E1%BA%ADt-tr%E1%BB%93ng-c%C3%A2y-%C3%B3c-ch%C3%B3-gi%C3%A0u-dinh-d%C6%B0%E1%BB%A1ng-mang-l%E1%BA%A1i-gi%C3%A1-tr%E1%BB%8B-kinh-t%E1%BA%BF-cao.html',
                    'http://phanbonnamviet.vn/k%E1%BB%B9-thu%E1%BA%ADt-n%C3%B4ng-nghi%E1%BB%87p/item/1851-k%E1%BB%B9-thu%E1%BA%ADt-tr%E1%BB%93ng-v%C3%A0-ch%C4%83m-s%C3%B3c-cho-c%C3%A2y-b%E1%BA%A7u-nhi%E1%BB%81u-qu%E1%BA%A3.html',
                    'http://phanbonnamviet.vn/tin-t%E1%BB%A9c/item/1867-th%E1%BB%A9-tr%C6%B0%E1%BB%9Fng-l%C3%AA-qu%E1%BB%91c-doanh-%E1%BB%A9ng-d%E1%BB%A5ng-c%C3%B4ng-ngh%E1%BB%87-l%C3%A0-kh%C3%A2u-then-ch%E1%BB%91t-t%E1%BA%A1o-s%E1%BB%B1-%C4%91%E1%BB%99t-ph%C3%A1-trong-t%C3%A1i-c%C6%A1-c%E1%BA%A5u-ng%C3%A0nh-n%C3%B4ng-nghi%E1%BB%87p.html',
                ],
                'non_article_links': [
                    'http://phanbonnamviet.vn/tin-t%E1%BB%A9c/tin-th%E1%BB%8B-tr%C6%B0%E1%BB%9Dng.html',
                    'http://phanbonnamviet.vn/s%E1%BA%A3n-ph%E1%BA%A9m/ph%C3%A2n-b%C3%B3n-l%C3%A1.html',
                    'http://phanbonnamviet.vn/s%E1%BA%A3n-ph%E1%BA%A9m/ph%C3%A2n-h%E1%BB%AFu-c%C6%A1-nam-vi%E1%BB%87t.html'
                ],
                'css_selectors': [
                    {
                        'is_article': '#rt-main #k2Container .itemHeader',
                        'title': '#rt-main #k2Container .itemHeader',
                        'description': '',
                        'main_content': '#rt-main #k2Container .itemBody',
                        'published_at': '',
                        'junk_data': []
                    }
                ]
            },
            'ngoisao.net': {
                'article_links': [
                    'http://ngoisao.net/tin-tuc/hau-truong/showbiz-viet/dan-nghe-si-noi-tieng-lam-phu-dau-phu-re-cho-le-vu-quy-cua-le-phuong-3624212.html',
                    'http://ngoisao.net/tin-tuc/thoi-trang/nha-phuong-thanh-lich-voi-vay-cong-so-3634633.html',
                    'http://ngoisao.net/tin-tuc/gia-dinh/me-hai-con-viet-nhat-ky-chua-kip-an-ngon-da-di-de-mo-3634255.html',
                ],
                'non_article_links': [
                    'http://ngoisao.net/tin-tuc/thoi-cuoc', 'http://ngoisao.net/tin-tuc/thoi-trang',
                    'http://ngoisao.net/tin-tuc/ben-le'
                ],
                'css_selectors': [
                    {
                        'is_article': '#page_container div.detailCT > h1',
                        'title': '#page_container div.detailCT > h1',
                        'description': '',
                        'main_content': '#page_container div.detailCT div.fck_detail',
                        'published_at': '#page_container div.detailCT div.author_mail span',
                        'junk_data': []
                    }
                ]

            },
            'baocongthuong.com.vn': {
                'article_links': [
                    'http://baocongthuong.com.vn/nang-tam-gia-tri-nong-san.html',
                    'http://baocongthuong.com.vn/tech-expo-2017-ket-noi-37-nha-tuyen-dung-voi-hon-1500-ung-vien.html',
                    'http://baocongthuong.com.vn/neu-co-hoi-khong-go-cua.html'
                ],
                'non_article_links': [
                    'http://baocongthuong.com.vn/thuong-mai',
                    'http://baocongthuong.com.vn/thoi-su',
                    'http://baocongthuong.com.vn/thuong-hieu'
                ],
                'css_selectors': [
                    {
                        'is_article': '#content header > h1',
                        'title': '#content header > h1',
                        'description': '#content header div.summary p',
                        'main_content': '#content article',
                        'published_at': '#content header time',
                        'junk_data': []
                    }
                ]

            },
            'vietnamnet.vn': {
                'article_links': [
                    'http://vietnamnet.vn/vn/the-thao/tin-chuyen-nhuong/tin-chuyen-nhuong-31-8-mourinho-2-tay-2-dien-thoai-man-city-ky-sanchez-396142.html',
                    'http://vietnamnet.vn/vn/giai-tri/the-gioi-sao/ve-dep-khong-tuoi-cua-dien-vien-hien-mai-tuoi-50-394948.html',
                    'http://vietnamnet.vn/vn/giao-duc/nguoi-thay/niem-tin-cua-giao-vien-la-dieu-quan-trong-de-doi-moi-giao-duc-thanh-cong-396019.html'
                ],
                'non_article_links': [
                    'http://vietnamnet.vn/vn/suc-khoe/',
                    'http://vietnamnet.vn/vn/doi-song/',
                    'http://vietnamnet.vn/vn/giao-duc/'
                ],
                'css_selectors': [
                    {
                        'is_article': 'body .Main-Container div div .ArticleDetail h1',
                        'title': 'body .Main-Container div div .ArticleDetail h1',
                        'description': '',
                        'main_content': '#ArticleContent',
                        'published_at': 'body .Main-Container .Main-Body div div .ArticleDetail .ArticleDateTime span',
                        'junk_data': ['.box-taitro']
                    }
                ]

            },
            'thanhnien.vn': {
                'article_links': [
                    'http://thanhnien.vn/gioi-tre/cu-nhan-chay-xe-om-870684.html',
                    'http://thanhnien.vn/giao-duc/de-nhu-san-xuat-luan-van-sau-dai-hoc-870960.html',
                    'http://thethao.thanhnien.vn/bong-da-quoc-te/chamberlain-chap-nhan-luong-thap-roi-arsenal-sang-liverpool-77747.html'
                ],
                'non_article_links': [
                    'http://thanhnien.vn/doi-song/', 'http://thanhnien.vn/kinh-doanh/'
                ],
                'css_selectors': [
                    {
                        'is_article': '.main-article header h1',
                        'title': '.main-article header h1',
                        'description': '.main-article .content .cms-desc',
                        'main_content': '.main-article .content #main_detail',
                        'published_at': '.main-article header .meta time',
                        'junk_data': ['#relatednews', '.story']
                    }
                ]

            },
            'baodatviet.vn': {
                'article_links': [
                    'http://baodatviet.vn/bat-dong-san/khong-gian-song/chuyen-gia-phong-thuy-soi-dai-gia-rao-ban-nha-55-ty-3342160/',
                    'http://baodatviet.vn/the-thao/ben-le-tran-dau/vff-niu-giu-huu-thang-de-giu-ghe-cua-minh-3342052/',
                    'http://baodatviet.vn/kinh-te/tai-chinh/pvn-xin-pha-san-nha-may-dung-quat-vi-sao-cham-tre-3342101/'
                ],
                'non_article_links': [
                    'http://baodatviet.vn/chinh-tri-xa-hoi/', 'http://baodatviet.vn/kinh-te/',
                    'http://baodatviet.vn/dien-dan-tri-thuc/'
                ],
                'css_selectors': [
                    {
                        'is_article': '#detail > h1',
                        'title': '#detail > h1',
                        'description': '#left_col .lead',
                        'main_content': '#divContent',
                        'published_at': '#mid_col .time',
                        'junk_data': []
                    }
                ]

            },
            'news.zing.vn': {
                'article_links': [
                    'http://news.zing.vn/khu-biet-thu-hang-sang-ben-bo-bien-ho-tram-gia-gan-8-ty-post775771.html',
                    'http://news.zing.vn/doi-hinh-ngoi-sao-cho-muon-mua-giai-201718-post775914.html',
                    'http://news.zing.vn/cao-thu-man-bac-trung-quoc-quan-he-vung-trom-voi-nhieu-gai-tre-post775303.html'
                ],
                'non_article_links': [
                    'http://news.zing.vn/giai-tri.html', 'http://news.zing.vn/cong-nghe.html',
                    'http://news.zing.vn/phap-luat.html'
                ],
                'css_selectors': [
                    {
                        'is_article': 'article section.main header h1',
                        'title': 'article section.main header h1',
                        'description': 'article section.main .the-article-summary',
                        'main_content': 'article section.main .the-article-body',
                        'published_at': 'article section.main header .the-article-publish',
                        'junk_data': []
                    }
                ]

            },
            'dantri.com.vn': {
                'article_links': [
                    'http://dantri.com.vn/giao-duc-khuyen-hoc/vu-lo-ap-tien-si-thac-si-bo-giao-duc-yeu-cau-thuc-hien-dung-ket-luan-thanh-tra-20170901071840553.htm',
                    'http://dantri.com.vn/the-thao/psg-chinh-thuc-no-sieu-bom-tan-mbappe-20170901083511228.htm',
                    'http://dantri.com.vn/nhip-song-tre/nu-sinh-16-tuoi-cao-1m71-hoc-gioi-tieng-anh-va-tieng-phap-20170831231824557.htm'
                ],
                'non_article_links': [
                    'http://dantri.com.vn/the-thao.htm',
                    'http://dantri.com.vn/the-gioi.htm',
                    'http://dantri.com.vn/giao-duc-khuyen-hoc.htm'
                ],
                'css_selectors': [
                    {
                        'is_article': '.container #ctl00_IDContent_ctl00_divContent h1',
                        'title': '.container #ctl00_IDContent_ctl00_divContent h1',
                        'description': '',
                        'main_content': '#divNewsContent',
                        'published_at': '.container #ctl00_IDContent_ctl00_divContent .tt-capitalize',
                        'junk_data': ['.news-tag']
                    }
                ]
            },
            'cafebiz.vn': {
                'article_links': [
                    'http://cafebiz.vn/7-loai-ban-be-nen-tu-mat-cang-som-cang-tot-loai-thu-5-ai-cung-co-20170831142952026.chn',
                    'http://cafebiz.vn/thu-truong-bo-tai-chinh-tang-vat-khong-tac-dong-nhieu-den-nguoi-ngheo-20170830191431928.chn',
                    'http://cafebiz.vn/1-can-benh-va-2-nguoi-ban-bat-cu-nguoi-viet-tre-nao-cung-can-loai-bo-neu-muon-thanh-cong-dat-duoc-muc-tieu-cuoc-doi-20170830163433741.chn'
                ],
                'non_article_links': [
                    'http://cafebiz.vn/thoi-su.chn',
                    'http://cafebiz.vn/vi-mo.chn',
                    'http://cafebiz.vn/cau-chuyen-kinh-doanh.chn'
                ],
                'css_selectors': [
                    {
                        'is_article': '#mainDetail h1',
                        'title': '#mainDetail h1',
                        'description': '#mainDetail h2',
                        'main_content': '#mainDetail .detail-content',
                        'published_at': '.right .date_time',
                        'junk_data': []
                    }
                ]

            },
            'www.tienphong.vn': {
                'article_links': [
                    'http://www.tienphong.vn/gioi-tre/nhan-sac-cac-hot-girl-ha-noi-doi-dau-ngay-ay-bay-gio-1183836.tpo',
                    'http://www.tienphong.vn/phap-luat/cong-an-vao-cuoc-vu-dinh-tac-hoanh-hanh-o-cao-toc-ha-noi-bac-giang-1184396.tpo',
                    'http://www.tienphong.vn/phap-luat/thanh-nien-duoi-chem-me-trong-con-ngao-da-1118960.tpo',
                    'http://www.tienphong.vn/gioi-tre/5-y-tuong-khoi-nghiep-xuat-sac-nhat-khu-vuc-phia-bac-1113403.tpo'
                ],
                'non_article_links': [
                    'http://www.tienphong.vn/the-gioi/', 'http://www.tienphong.vn/gioi-tre/',
                    'http://www.tienphong.vn/search/ZGFzZA==/dasd.tpo', 'http://www.tienphong.vn/tag/dinh-tac'
                ],
                'css_selectors': [
                    {
                        'is_article': '#article-meta h1',
                        'title': '#article-meta h1',
                        'description': '#article-content-left .article-sapo',
                        'main_content': '#article-content-left .article-col-b',
                        'published_at': '#article-meta time',
                        'junk_data': ['.article-relate-b', '.article-hot-video']
                    }
                ]

            },
            'vnexpress.net': {
                'article_links': [
                    'https://vnexpress.net/tin-tuc/cuoi/chang-trai-lam-gi-de-thoat-khoi-nguy-hiem-3611267.html',
                    'https://vnexpress.net/tin-tuc/oto-xe-may/nissan-x-trail-giam-gia-thang-9-canh-tranh-honda-cr-v-3636496.html',
                    'https://vnexpress.net/tin-tuc/phap-luat/phu-lai-tau-se2-vks-truy-to-oan-day-toi-vao-tot-cung-dau-kho-3638065.html'
                    'https://vnexpress.net/tin-tuc/thoi-su/tru-so-cong-ty-nha-nuoc-tai-quan-1-bi-cuong-che-3638051.html'
                ],
                'non_article_links': [
                    'https://vnexpress.net/thao-do-chung-cu-co-giang/tag-909981-1.html',
                    'https://vnexpress.net/cuong-che-cong-ty-nha-nuoc/tag-928426-1.html',
                    'https://vnexpress.net/tin-tuc/thoi-su', 'https://vnexpress.net/tin-tuc/goc-nhin'
                ],
                'css_selectors': [
                    {
                        'is_article': '.container .title_news_detail',
                        'title': '.container h1.title_news_detail',
                        'description': '.container .description',
                        'main_content': '.container article.content_detail',
                        'published_at': '.container .time',
                        'junk_data': []
                    }
                ]

            },
        }


class Detector:
    __detector_asset_constant = DetectorAssetConstant()

    def __init__(self):
        pass

    def get_html(self, url: str):
        response = requests.get(url)
        content = response.content
        return content

    def __get_domain_name(self, url: str) -> str:
        components = urlparse(url)
        return components.netloc

    def is_article(self, url: str, html: str):
        if self.get_available_article_css_selector(url, html) is None:
            return False
        return True

    def get_title(self, html: str, d_css_selector: dict) -> str:
        if d_css_selector['title'] != '':
            result = self.__get_by_selector(html, d_css_selector['title'])
            return result[0].getText()
        return ''

    def get_description(self, html: str, d_css_selector: dict) -> str:
        if d_css_selector['description'] != '':
            result = self.__get_by_selector(html, d_css_selector['description'])
            return result[0].getText()
        return ''

    def get_published_at(self, html: str, d_css_selector: dict):
        if d_css_selector['published_at'] != '':
            result = self.__get_by_selector(html, d_css_selector['published_at'])
            return result[0].getText()
        return ''

    def get_main_content(self, html: str, d_css_selector: dict):
        return self.__get_content_without_junk(html, d_css_selector['main_content'], d_css_selector['junk_data'])

    def get_available_article_css_selector(self, url: str, html: str):
        source_name = self.__get_domain_name(url)
        if source_name in self.__detector_asset_constant.page_asset:
            page_asset = self.__detector_asset_constant.page_asset[source_name]
            l_css_selector = page_asset['css_selectors']

            for d_css_selector in l_css_selector:
                if self.__is_valid_css_selector(html, d_css_selector):
                    return d_css_selector

        return None

    # TODO move to magic-splash
    def validate_source(self, source: str):
        if source in self.__detector_asset_constant.page_asset:
            page_asset = self.__detector_asset_constant.page_asset[source]
            l_css_selector = page_asset['css_selectors']
            l_non_article_link = page_asset['non_article_links']
            l_article_link = page_asset['article_links']

            # Validate article links
            for article_link in l_article_link:
                if not self.__validate_css_selector(article_link, l_css_selector):
                    raise Exception('Wrong selectors on url: {}'.format(article_link))

            # Validate non article links
            for non_article_link in l_non_article_link:
                if self.__validate_css_selector(non_article_link, l_css_selector):
                    raise Exception('Wrong selectors on url: {}'.format(non_article_link))

    def __is_valid_css_selector(self, html: str, d_css_selector: dict):
        for key in d_css_selector.keys():
            if d_css_selector[key] == '' or key == 'junk_data':
                continue

            result = self.__get_by_selector(html, d_css_selector[key])
            if len(result) < 1:
                return False

            result_content = result[0]
            if result_content == '':
                return False

        return True

    def __validate_css_selector(self, link: str, l_css_selector: List[dict]):
        html_content = self.get_html(link)
        for d_css_selector in l_css_selector:
            if self.__is_valid_css_selector(html_content, d_css_selector):
                return True
        return False

    def __get_content_without_junk(self, html_content: str, main_content_pattern: str, l_junk_data_pattern: List[str]):
        main_content = self.__get_by_selector(html_content, main_content_pattern)[0]
        for jun_data_pattern in l_junk_data_pattern:
            l_junk_data = main_content.select(jun_data_pattern)

            for junk in l_junk_data:
                junk.extract()
        return str(main_content)

    def __get_by_selector(self, html: str, selector_pattern: str):
        soup = BeautifulSoup(html, 'html.parser')
        result = soup.select(selector_pattern)

        return result

