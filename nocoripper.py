import pycurl
import json
import configparser
from io import BytesIO
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import parse_qs

url = {"user": "https://api.noco.tv:443/1.1/users/init",
       "search": "https://api.noco.tv:443/1.1/shows?partner_key=NOL&subscribed=false&page={}&elements_per_page=40",
       "media": "https://api.noco.tv:443/1.1/shows/{}/medias",
       "qualities": "https://api.noco.tv:443/1.1/shows/{}/qualities",
       "video": "https://api.noco.tv:443/1.1/shows/{}/video/{}/fr"
       }

try:
    config = configparser.RawConfigParser()
    config.read("config.cfg")

    username = config.get("Logs", "Username")
    password = config.get("Logs", "Password")
except Exception as ex:
    print("Fichier de configuration invalide.")


def get_url():
    c = pycurl.Curl()
    post_data = {"login" : 1,
                 "username" : username,
                 "password" : password}
    postfields = urlencode(post_data)
    buffer = BytesIO()
    dessert = BytesIO()

    c.setopt(pycurl.URL, "https://api.noco.tv/1.1/OAuth2/authorize.php?response_type=token&state=xyz&redirect_uri=https%3A%2F%2Fapi.noco.tv%2Fo2c.html&realm=5ae5f7fbe420f7f104084a3bfc3b6271&client_id=DocumentationAPI&scope=noco_account")
    c.setopt(pycurl.HTTPHEADER, ['Origin: https://api.noco.tv',
                                 'Upgrade-Insecure-Requests: 1',
                                 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
                                 'Content - Type: application / x - www - form - urlencoded',
                                 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                 'Referer: https://api.noco.tv/1.1/OAuth2/authorize.php?response_type=token&state=xyz&redirect_uri=https%3A%2F%2Fapi.noco.tv%2Fo2c.html&realm=5ae5f7fbe420f7f104084a3bfc3b6271&client_id=DocumentationAPI&scope=noco_account',
                                 'Accept-Encoding: gzip, deflate, br',
                                 'Accept-Language: fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4'])
    c.setopt(pycurl.POSTFIELDS, postfields)
    c.setopt(pycurl.WRITEHEADER, buffer)
    c.setopt(pycurl.WRITEDATA, dessert)

    c.perform()

    if c.getinfo(pycurl.RESPONSE_CODE) == 302:
        body = buffer.getvalue().decode('iso-8859-1')
        redirection_url = [line.split(":", 1)[1].replace('#', '?') for line in body.split('\n') if line.startswith("Location")]
        c.close()
        return redirection_url[0]
    else:
        c.close()
        raise Exception("Erreur : Logs incorrects")


def get_token(url=get_url()):
    parsed = urlparse(url)

    return parse_qs(parsed.query)['access_token'][0]


def make_request(token, url):
    buffer = BytesIO()

    connect = pycurl.Curl()
    connect.setopt(pycurl.URL, url)
    connect.setopt(pycurl.HTTPHEADER, ['Host: api.noco.tv',
                                       'Connection: keep-alive',
                                       'Accept: application/json',
                                       'Authorization: Bearer {}'.format(token),
                                       'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gec'
                                       'ko) Chrome/52.0.2743.116 Safari/537.36',
                                       'Referer: https://api.noco.tv/1.1/documentation/',
                                       'Accept-Encoding: gzip, deflate, sdch, br',
                                       'Accept-Language: fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4'
                                       ])
    connect.setopt(pycurl.WRITEDATA, buffer)
    connect.perform()
    resp_code = connect.getinfo(pycurl.RESPONSE_CODE)
    connect.close()

    if resp_code != 200:
        raise ValueError(resp_code)

    body = buffer.getvalue().decode('iso-8859-1')
    return json.loads(body)

if __name__ == '__main__':
    token = get_token()
    result = make_request(token, url["user"])

    print("L'utilisateur connecté est {}. Bonjour !".format(result["user"]["username"]))
