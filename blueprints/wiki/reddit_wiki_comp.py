__author__ = 'HansiHE'

import markdown

LINK_PATTERN = r'a'


class LinkChanger(markdown.inlinepatterns.Pattern):
    def handle_match(self, m):
        print 'wat'
        return 'wat'


class RedditExtension(markdown.Extension):
    def extend_markdown(self, md, md_globals):
        md.inlinePatterns['link_changer'] = LinkChanger(LINK_PATTERN)


def make_extension(configs=None):
    return RedditExtension(configs=configs)