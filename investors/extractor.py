from bs4 import BeautifulSoup
import requests
import re
from config import HEADERS


def extract_from_shizune(url):
    """
    Extract investors directly from HTML tables on Shizune.
    NO LLM. Preserve all table columns and description fields.
    """

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')

        investors = []

        # =========================
        # 1. TABLE EXTRACTION
        # =========================
        tables = soup.select('table')

        def normalize_key(text):
            key = text.strip().lower()
            key = re.sub(r'[^a-z0-9]+', '_', key)
            return key.strip('_')

        def get_cell_text(cell):
            link = cell.find('a', href=True)
            if link:
                return link.get_text(' ', strip=True) or link['href']
            return cell.get_text(' ', strip=True)

        for table in tables:
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [normalize_key(th.get_text(' ', strip=True)) for th in header_row.find_all(['th', 'td'])]

            rows = table.select('tr')[1:] if headers else table.select('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 2:
                    continue

                row_data = {}
                for idx, col in enumerate(cols):
                    key = headers[idx] if idx < len(headers) and headers[idx] else f'column_{idx+1}'
                    # preserve line breaks so we can extract name + type under the same cell
                    raw = col.get_text('\n', strip=True)
                    # prefer link href for website-like cells
                    link = col.find('a', href=True)
                    if link and (key == 'website' or link.get('href', '').startswith('http')):
                        val = link.get('href')
                    else:
                        val = raw.replace('\n', ' | ')

                    row_data[key] = val

                    # if investor cell contains a second line with type, capture it
                    if key in ('name', 'investor', 'company'):
                        parts = raw.splitlines()
                        if len(parts) > 1:
                            row_data['type_from_name_cell'] = parts[1].strip()

                name = row_data.get('name') or row_data.get('investor') or row_data.get('company')
                if not name or len(name) < 2:
                    continue

                # Map Shizune columns to requested JSON fields
                # Geography -> country, Focus -> included in description
                country = row_data.get('geography') or row_data.get('country') or ''
                relevant = row_data.get('relevant_deals') or row_data.get('relevant') or row_data.get('deals') or ''
                focus = row_data.get('focus') or ''

                description = relevant
                if focus:
                    description = (description + ' | Focus: ' + focus) if description else ('Focus: ' + focus)

                typ = row_data.get('type') or row_data.get('category') or row_data.get('type_from_name_cell') or 'Unknown'

                investor = {
                    'name': name,
                    'type': typ,
                    'country': country,
                    'website': row_data.get('website', ''),
                    'description': description
                }

                # keep any extra table columns
                for key, value in row_data.items():
                    if key not in investor and value:
                        investor[key] = value

                investors.append(investor)

        # =========================
        # CLEAN DUPLICATES
        # =========================
        seen = set()
        cleaned = []

        for inv in investors:
            name = inv['name'].lower().strip()
            if name and name not in seen:
                seen.add(name)
                cleaned.append(inv)

        return cleaned

    except Exception as e:
        print('Extractor error:', e)
        return []
