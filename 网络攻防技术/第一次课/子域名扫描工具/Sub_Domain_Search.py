# 本次实验内容主要为：收集baidu.com域名下的子域名，
# 收集方法为使用bing搜索引擎，采用爬手段，爬取搜索到的域名
# bing搜索引擎搜索子域名的语法为：domain:[域名]
import requests  # 用于请求网页
from bs4 import BeautifulSoup  # 用于处理获取的到的网页源码数据
from urllib.parse import urlparse  # 用于处理url
from fake_useragent import UserAgent  # 用于随机获取user-agent
from selenium import webdriver  # 用于模拟浏览器


# 定义一个采用bing搜索的方法
def bing_search():
    Subdomain = []  # 定义一个空列表用于存储收集到的子域名

    # 定义请求头，绕过反爬机制
    hearders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56",
        "accept": "*/*",
        "referer": "https://cn.bing.com/search?q=domain%3abaidu.com&qs=HS&pq=domain%3a&sc=10-7&cvid=B99CC286861647E79EF504A4D5B819F1&FORM=QBLH&sp=1",
        "cookie": "MUID=15F7A3347F9B66091BBBAC017EB56733",
    }

    # 定义请求url
    url = "https://cn.bing.com/search?q=domain%3aqq.com&qs=n&sp=-1&pq=domain%3abaidu.com&sc=0-16&sk=&cvid=E6DAE965B2BD4FDC8DF857015E0499C1&first=9&FORM=PQRE1"
    resp = requests.get(url, headers=hearders)  # 访问url，获取网页源码

    # 创建一个BeautifulSoup对象，第一个参数是网页源码，第二个参数是Beautiful Soup 使用的 HTML 解析器，
    soup = BeautifulSoup(resp.content, "html.parser")
    job_bt = soup.find_all("h2")  # find_all()查找源码中所有<h2>标签的内容
    for i in job_bt:
        link = i.a.get("href")  # 循环获取‘href’的内容
        # urlparse是一个解析url的工具，scheme获取url的协议名，netloc获取url的网络位置
        domain = str(urlparse(link).scheme + "://" + urlparse(link).netloc)
        if domain in Subdomain:  # 如果解析后的domain存在于Subdomain中则跳过，否则将domain存入子域名表中
            pass
        else:
            Subdomain.append(domain)
            print(domain)


def is_valid_url(url):  # 判断url是否有效
    parsed_url = urlparse(url)  # 解析url
    return parsed_url.scheme and parsed_url.netloc  # 返回url的协议和网络位置


# 百度搜索引擎搜索子域名的语法为：site:[域名]
def baidu_search():  # 百度搜索引擎搜索子域名
    Subdomain = []  # 定义一个空列表用于存储收集到的子域名

    # 随机获取一个user-agent,以模拟更真实的用户登录场景
    ua = UserAgent().random

    # 将ua转换为字符串
    str_ua = str(ua)

    # 收集网站Cookie，以便减少限制
    browser = webdriver.Chrome()  # 创建一个Chrome浏览器对象
    url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=site%3Aqq.com&fenlei=256&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_btype=t"  # 定义请求url

    browser.get(url)  # 访问url
    cookies = browser.get_cookies()  # 获取cookies
    cookie_str = ""  # 定义一个空字符串用于存储cookies
    for cookie in cookies:  # 循环获取cookies
        cookie_str += cookie["name"] + "=" + cookie["value"] + ";"  # 将cookies转换为字符串

    # 定义请求头，绕过反爬机制
    headers = {
        "User-Agent": str_ua,  # 随机获取一个user-agent
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept": "*/*",
        "Referer": "cn.bing.com",
        "Connection": "keep-alive",
        "Cookie": cookie_str,  # 采用cookie登录
    }

    # 定义请求url
    response = requests.get(url, headers=headers)
    print(response.text)
    # 创建一个BeautifulSoup对象，第一个参数是网页源码，第二个参数是Beautiful Soup 使用的 HTML 解析器，
    soup = BeautifulSoup(response.content, "html.parser")

    # find_all()查找源码中所有<h3>标签的内容
    h3_set = soup.find_all("h3")
    # title_set = soup.find_all("title")

    for i in h3_set:  # 循环获取‘href’的内容

        link = i.a.get("href")

        # 判断url是否有效
        if not is_valid_url(link):  # 如果url无效则跳过
            continue
        tmp_url = link
        # 获取最终跳转的url
        temp_response = requests.get(
            tmp_url, allow_redirects=True
        )  # allow_redirects=True允许重定向
        final_url = temp_response.url

        # 获取最终跳转的url的响应
        final_url_response = requests.get(final_url, headers=headers)

        # 获取子域名
        sub_domain = final_url.split("//")[-1].split("/")[
            0
        ]  # 以//为分隔符，获取//后面的内容，以/为分隔符，获取/前面的内容

        # 获取标题
        titl = BeautifulSoup(final_url_response.content, "html.parser")
        title = titl.find("title")
        if title:
            title_str = str(title.get_text())
        else:
            title_str = "None"
        # 获取描述
        desc = BeautifulSoup(final_url_response.content, "html.parser")
        description = desc.find("meta", attrs={"name": "description"})

        # 判断description是否为空
        if description == None:
            # 如果description为空，则考虑可能为Description的meta标签的内容
            description = desc.find("meta", attrs={"name": "Description"})
            if description == None:
                description = "None"
            else:
                description_str = str(description.get("content"))
        # 判断description的content是否为空
        elif description.get("content") == None:
            description = desc.find("meta", attrs={"name": "Description"})
            if description == None:
                description = "None"
            else:
                description_str = str(description.get("content"))
        # 如果description的content不为空，则获取description的content
        else:
            description_str = str(description.get("content"))

        # 判断子域名是否已经存在于Subdomain中，如果存在则跳过，否则将子域名存入Subdomain中
        if sub_domain in Subdomain:
            pass
        else:
            result = (
                "标题："
                + title_str
                + "\n"
                + "描述："
                + description_str
                + "\n"
                + "链接："
                + final_url
            )
            print(result)
            print("--------------------------------------------------")
            Subdomain.append(sub_domain)

        description_str = ""  # 将description_str置空
        title_str = ""  # 将title_str置空


baidu_search()
# bing_search()
