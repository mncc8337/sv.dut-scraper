import re
import requests

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&amp;", "&")
    s = s.replace("&quot;", '"')
    s = s.replace("&#39;", "'")
    return s

def get_hidden_field(html, field_name):
    pattern = r'name="' + re.escape(field_name) + r'"[^>]*value="([^"]+)"'
    m = re.search(pattern, html)
    if m:
        return m.group(1)
    return None

def extract_table_html(html, table_id):
    pattern = re.compile(
        r'(<table\b[^>]*\bid\s*=\s*["\']' + re.escape(table_id) + r'["\'][^>]*>.*?</table>)',
        re.IGNORECASE | re.DOTALL
    )
    m = pattern.search(html)
    return m.group(1) if m else None

def parse_table_rows(table_html):
    tr_pattern = re.compile(r'<tr\b[^>]*?>(.*?)</tr>', re.IGNORECASE | re.DOTALL)
    td_pattern = re.compile(r'<t[dh]\b[^>]*?>(.*?)</t[dh]>', re.IGNORECASE | re.DOTALL)

    rows = []
    for tr_match in tr_pattern.finditer(table_html):
        tr_inner = tr_match.group(1)
        cells = []
        for td_match in td_pattern.finditer(tr_inner):
            cell_html = td_match.group(1).strip()
            # Remove any inner tags (simple strip)
            cell_text = re.sub(r'<[^>]+>', '', cell_html)
            # Unescape HTML entities and normalize whitespace
            cell_text = html_unescape(cell_text)
            cell_text = re.sub(r'\s+', ' ', cell_text).strip()
            cells.append(cell_text)
        if cells:
            rows.append(cells)
    return rows

def pull_data(user, password):
    LOGIN_URL = "https://sv.dut.udn.vn/PageDangNhap.aspx"
    TARGET_URL = "https://sv.dut.udn.vn/PageLichTH.aspx"

    print("start pulling data ...")

    headers = {"User-Agent": "Mozilla/5.0", "Referer": LOGIN_URL, "Content-Type": "application/x-www-form-urlencoded",}
    cookies = {}

    # get ASP.NET_SessionId
    resp = requests.get(LOGIN_URL)
    login_html = resp.text
    cookies.update(resp.cookies.get_dict())

    request_data = {}
    request_data["_ctl0:MainContent:QLTH_btnLogin"] = "Đăng+nhập"

    # load account
    request_data["_ctl0:MainContent:DN_txtAcc"] = user
    request_data["_ctl0:MainContent:DN_txtPass"] = password
    print("account loaded")

    # get __VIEWSTATE 
    request_data["__VIEWSTATE"] = get_hidden_field(login_html, "__VIEWSTATE")
    if request_data["__VIEWSTATE"]:
        print("got VIEWSTATE")
    else:
        print("failed to get VIEWSTATE")
        exit(1)

    # get __VIEWSTATEGENERATOR
    request_data["__VIEWSTATEGENERATOR"] = get_hidden_field(login_html, "__VIEWSTATEGENERATOR")
    if request_data["__VIEWSTATEGENERATOR"]:
        print("got VIEWSTATEGENERATOR")
    else:
        print("failed to get VIEWSTATEGENERATOR")
        exit(1)

    print("attemp to login ...")
    resp = requests.post(LOGIN_URL, data=request_data, headers=headers, cookies=cookies)
    print("status:", resp.status_code)
    print("URL after POST:", resp.url)
    print("response length:", len(resp.text))

    if resp.status_code != 200:
        print("login url not exists")
        exit(1)

    if resp.url == LOGIN_URL:
        print("wrong user/password")
        exit(1)

    print("login successfully, attempt to get to schedule page ...")

    resp = requests.get(TARGET_URL, timeout=20, headers=headers, cookies=cookies)
    schedule_html = resp.text

    print("status:", resp.status_code)
    print("URL after POST:", resp.url)
    print("length of HTML:", len(schedule_html))

    if resp.status_code != 200 or resp.url != TARGET_URL:
        print("failed to reach to schedule page")
        exit(1)

    print("got into schedule page, getting the schedule ...")
    table = extract_table_html(schedule_html, "TTKB_GridInfo")
    if not table:
        print("cannot get schedule")
        exit(1)

    table_rows = parse_table_rows(table)
    table_headers = table_rows[1]
    table_headers.insert(0, "TT")
    # remove headers row
    table_rows.pop(0)
    table_rows.pop(0)
    # remove total row
    table_rows.pop(-1)

    for row in table_rows:
        tkb = row[7].split(",")
        tiet = tkb[1].split("-")
        tiet_bat_dau = int(tiet[0])
        tiet_ket_thuc = int(tiet[1])
        tuan_hoc = []
        for dur in row[8].split(";"):
            lst = dur.split("-")
            tuan_hoc.append([int(lst[0]), int(lst[1])])

        for i in range(len(row)):
            if row[i]:
                print(i, table_headers[i], ":", row[i])
        print()
