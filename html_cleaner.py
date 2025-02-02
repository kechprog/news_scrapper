from html.parser import HTMLParser
from os.path import join

IGNORE_TAGS = {"script", "style"}

class HTMLElement:
    def __init__(self, tag_name, attrs=None, data=''):
        self.tag_name = tag_name
        self.attrs = attrs or {}
        self.children = []
        self.data = data

    def add_child(self, child):
        if child.tag_name in IGNORE_TAGS:
            return
        self.children.append(child)

    #TODO: add proper attrs handaling
    def __repr__(self):
        if self.children == []:
            if self.data != '':
                return f'<{self.tag_name}>\n \t{self.data}\n </{self.tag_name}>'
            else:
                return ''
        elif len(self.children) == 1:
            return self.children[0].__repr__()
        else:
            children = "\n\t".join(map(lambda x: '\n\t'.join(x.__repr__().splitlines()),
                                     self.children))
            return f"<{self.tag_name}>\n \t{children}\n </{self.tag_name}>"

class HTMLTreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.root = HTMLElement("document")  # Ensure there is always a root

    def handle_starttag(self, tag, attrs):
        element = HTMLElement(tag, attrs=dict(attrs))
        if self.stack:
            self.stack[-1].add_child(element)
        else:
            self.root.add_child(element)  # Attach top-level elements to the root
        self.stack.append(element)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1].tag_name == tag:
            self.stack.pop()

    def handle_data(self, data):
        clean_data = data.strip()
        if clean_data and self.stack:
            self.stack[-1].data = clean_data

    def build_tree(self, html):
        self.stack.clear()
        self.root = HTMLElement("document")  # Reset root for a new parse
        self.feed(html)
        return self.root
