import instabot.cli_parser as cli_parser
from instabot.instagram import Instagram
import sys

if __name__ == "__main__":
    parser = cli_parser.Parser()
    cli = parser.parseCLI(sys.argv[1:])
    if cli.get('username') is not None and cli.get('password') is not None:
        insta = Instagram(cli.get('tags'))
        (session, cookies) = insta.login(cli.get('username'), cli.get('password'))
        insta.post_comment(post_id=cli.get('post-id')[0], token=session.get('csrf_token'),
                           comment=" ".join(insta.randomizeTags(
                               int(cli.get('number-of-tags')) if cli.get('number-of-tags') is not None else cli.get(
                                   'number_of_tags'))))
