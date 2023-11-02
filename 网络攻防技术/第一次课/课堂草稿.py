import requests

def generate_random_string():
    import string
    import random
    return ''.join(random.choice(string.ascii_lowercase) for i in range(8))


url ="http://admin.ejii3.cn/index/Index/index.html"
email ="%40"+generate_random_string()+"a.edu.cn"

# print(url)
# print(domain)
header = {
    "Accept":"application/json, text/javascript, */*; q=0.01",
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With":"XMLHttpRequest"
}
data = "name=" + generate_random_string() + email + "&pass=" + generate_random_string()
# data ="name=1%40uqzrrva.edu.cn&pass=1232123"
print(data)
response=requests.post(url=url,data=data,headers=header)
print(response.text)
