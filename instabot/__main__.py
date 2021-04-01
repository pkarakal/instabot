import instabot.cli_parser as cli_parser
from instabot.instagram import Instagram
from datetime import datetime
import sys

if __name__ == "__main__":
    parser = cli_parser.Parser()
    cli = parser.parseCLI(sys.argv[1:])
    if cli.get('username') is not None and cli.get('password') is not None:
        termination = cli.get('run_until')
        termination_date = datetime.fromisoformat(termination)
        comments_per_day = cli.get('comments-per-day') or 500
        insta = Instagram(cli.get('tags'))
        (session, cookies) = insta.login(cli.get('username'), cli.get('password'))
        insta.post_comment(post_id=cli.get('post-id')[0], token=session.get('csrf_token'),
                           comment=" ".join(insta.randomizeTags(
                               int(cli.get('number_of_tags')) if cli.get('number_of_tags') is not None else None)),
                           run_until=termination_date, comments_per_day=comments_per_day)
