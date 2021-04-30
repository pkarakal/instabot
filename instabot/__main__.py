import instabot.cli_parser as cli_parser
from instabot.instagram import Instagram
from instabot.logger import default_logger, stopLogging
from datetime import datetime
import sys

if __name__ == "__main__":
    parser = cli_parser.Parser()
    cli = parser.parseCLI(sys.argv[1:])
    if cli.get('username') is not None and cli.get('password') is not None:
        termination = cli.get('run_until')
        termination_date = datetime.fromisoformat(termination)
        comments_per_day = cli.get('comments_per_day') or 500
        insta = Instagram(cli.get('tags'), cli.get('emojis'), cli.get('number_of_tags'), cli.get('number_of_emojis'),
                          logger=default_logger)
        (session, cookies) = insta.login(cli.get('username'), cli.get('password'))
        insta.post_comment(post_id=cli.get('post_id')[0], token=session.get('csrf_token'),
                           comment=" ".join(insta.randomizeTags(
                               int(cli.get('number_of_tags')) if cli.get('number_of_tags') is not None else None)),
                           run_until=termination_date, comments_per_day=comments_per_day)
        stopLogging()
