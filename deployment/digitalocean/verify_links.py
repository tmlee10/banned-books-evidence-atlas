"""Verify the prebuilt site's local links without modifying the research content."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def verify(root):
    root = root.resolve()
    pages = {}
    for page in root.rglob('*.html'):
        parsed = Links()
        parsed.feed(page.read_text())
        pages[page.resolve()] = parsed
    checked = 0
    for page, parsed in pages.items():
        for link in parsed.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = ((root if url.path.startswith('/') else page.parent) / unquote(url.path).lstrip('/')).resolve() if url.path else page
            if target.is_dir():
                target /= 'index.html'
            if not target.is_relative_to(root) or not target.is_file():
                raise RuntimeError(f'Broken local link in {page.name}: {link}')
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                raise RuntimeError(f'Broken local anchor in {page.name}: {link}')
            checked += 1
    print(f'PASS: {len(pages)} HTML pages and {checked} local links/anchors.')


if __name__ == '__main__':
    import sys
    verify(Path(sys.argv[1]))
