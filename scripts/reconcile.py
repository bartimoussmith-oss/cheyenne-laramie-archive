import hashlib, json, re, sys
from pathlib import Path
import openpyxl

PATTERN = re.compile(r"cheyenne|laramie county|pine bluffs|\balbin\b|\bburns\b|ranchettes|south greeley|fox farm", re.I)
EXCLUDED = {'Dakotas Official URLs', 'Nebraska Official URLs', 'Colorado Official URLs'}
EXCLUDED_LABELS = {'Dewey County Commissioners', 'Cheyenne County', 'Sidney'}

def reconcile(path):
    path = Path(path)
    book = openpyxl.load_workbook(path, read_only=False, data_only=False)
    rows, excluded = [], []
    for sheet in book:
        for cells in sheet:
            values = [str(c.value) for c in cells if c.value is not None]
            if not any(PATTERN.search(v) for v in values):
                continue
            label = values[0] if values else ''
            item = {'sheet': sheet.title, 'row': cells[0].row, 'label': label, 'endpoints': []}
            for cell in cells:
                if cell.data_type != 'f' and isinstance(cell.value, str):
                    for url in re.findall(r'https?://[^\s<>"\[\]]+', cell.value):
                        item['endpoints'].append({'cell': cell.coordinate, 'url': url.rstrip(".,);'"), 'kind': 'literal'})
                if cell.hyperlink and cell.hyperlink.target:
                    item['endpoints'].append({'cell': cell.coordinate, 'url': cell.hyperlink.target, 'kind': 'hyperlink'})
            if sheet.title in EXCLUDED or label in EXCLUDED_LABELS:
                excluded.append(item)
            else:
                rows.append(item)
    book.close()
    return {'schema': 'workbook-reconciliation-v1', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'sheets': len(book.sheetnames), 'candidate_rows': rows, 'excluded_name_collisions': excluded, 'approval_status': 'candidates_only_not_authorized_for_crawl', 'formulas_executed': False}

if __name__ == '__main__':
    Path(sys.argv[2]).write_text(json.dumps(reconcile(sys.argv[1]), ensure_ascii=False, indent=2), encoding='utf-8')
