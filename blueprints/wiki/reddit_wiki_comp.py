__author__ = 'HansiHE'

import markdown

LINK_PATTERN = r'a'

class LinkChanger(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        print 'wat'
        return 'wat'

class RedditExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['link_changer'] = LinkChanger(LINK_PATTERN)

def makeExtension(configs=None):
    return RedditExtension(configs=configs)