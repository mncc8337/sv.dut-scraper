import re

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
