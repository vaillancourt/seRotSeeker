#! py -3
"""
This script parses a stackexchange database dump (in xml format) and outputs relevant content to help track potential
link rot.

It assumes that the data has been downloaded from https://archive.org/download/stackexchange, and exctracted to a
directory like [site].stackexchange.com (for instance, downloading the archive gamedev.stackexchange.com.7z, and
extracting it to the directory gamedev.stackexchange.com).

Usage:

py linkRotSeeker.py > list.csv

The script only works on posts, not on comments (yet?). Change the TARGET_SITE if you need to check stuff on another
site.
"""

import re

TARGET_SITE = 'gamedev'
TARGET_CONTENT = 'posts'

COMPILED_REGEX_LINK = re.compile(
    r"(https?://([-A-Za-z0-9\.]*)/\S+\.(?:zip|7z|rar|jpg|jpeg|gif|png|svg))",
    re.IGNORECASE)
COMPILED_REGEX_POST_ID = re.compile(r"<row Id=\"([0-9]+)\" PostTypeId", re.IGNORECASE)
COMPILED_REGED_POST_TYPE = re.compile(r"PostTypeId=\"([12])\"", re.IGNORECASE)

def seek_rot(a_target_site, a_target_content):
    """Main function of this little script."""

    if a_target_content != 'posts':
        print('Unknown target content: ' + a_target_content + '. Exiting.')
        exit(-1)

    lines = []
    with open(a_target_site + '.stackexchange.com/Posts.xml', mode='r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:

        link_matches = re.findall(COMPILED_REGEX_LINK, line)
        if not link_matches:
            continue

        post_type_id = re.search(COMPILED_REGED_POST_TYPE, line)
        if not post_type_id:
            # Some posts are not Question nor Answer in the SE terms (tag wikis?), in which cases we have to check the
            # next line.
            continue

        post_type_id = int(post_type_id.group(1))

        post_id = re.search(COMPILED_REGEX_POST_ID, line).group(1)
        post_url = 'https://' + TARGET_SITE + '.stackexchange.com/'
        if post_type_id == 1:
            post_url += 'q'
        elif post_type_id == 2:
            post_url += 'a'
        post_url += '/' + post_id

        for match in link_matches:

            full_url = match[0]

            domain = match[1]

            domain_parts = domain.split('.')
            domain_reversed = domain_parts[-1]
            for i in reversed(range(len(domain_parts)-1)):
                domain_reversed += '.' + domain_parts[i]

            link_type = 'package'
            if full_url.endswith(('jpg', 'jpeg', 'gif', 'png', 'svg')):
                link_type = 'image'

            print(
                post_id + '\t' +
                full_url + '\t' +
                domain + '\t' +
                domain_reversed + '\t' +
                link_type + '\t' +
                post_url)


if __name__ == '__main__':
    seek_rot(TARGET_SITE, TARGET_CONTENT)
