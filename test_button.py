import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# First, get the CSRF token
response = opener.open('http://127.0.0.1:8000/login/')
csrf_token = None
for cookie in cj:
    if cookie.name == 'csrftoken':
        csrf_token = cookie.value

# Now, login
data = urllib.parse.urlencode({
    'username': 'admin',
    'password': 'admin123',
    'csrfmiddlewaretoken': csrf_token
}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/login/', data=data)
req.add_header('Referer', 'http://127.0.0.1:8000/login/')
opener.open(req)

# Now, go to requests page
req = urllib.request.Request('http://127.0.0.1:8000/requests/')
response = opener.open(req)
html = response.read().decode('utf-8')

if 'User Database' in html:
    print('User Database button found!')
else:
    print('User Database button NOT found!')
    
with open('debug_html.html', 'w', encoding='utf-8') as f:
    f.write(html)
