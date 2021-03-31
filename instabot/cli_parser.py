from optparse import OptionParser
import sys
from instabot.ParameterException import ParameterException
import yaml


class Parser:
    def __init__(self):
        self.parser = OptionParser()
        self.parser.add_option("-i", "--id", action="append", dest="post_id",
                               help="define the post id to post the comment to")
        self.parser.add_option("-t", "--tags", action="append", dest="tags",
                               help="define the username of the users to tag in the post")
        self.parser.add_option("-n", "--number-of-tags", dest="number_of_tags",
                               help="define the number of tags you want in each comment")
        self.parser.add_option("-f", "--file", dest="file", help="define the yaml file to read parameters from")
        self.parser.add_option("-u", "--username", dest="username", help="define your username")
        self.parser.add_option("-p", "--password", dest="password", help="define your password")
        self.parser.add_option("-r", "--run-until", dest="run_until", help="define the datetime to stop program "
                                                                           "execution")
        self.parser.add_option("-c", "--comments-per-day", dest="comments_per_day", help="define how many comments "
                                                                                         "per day to post")

    def parseCLI(self, arguments=None):
        if arguments is None:
            arguments = sys.argv[1:]
        (options, args) = self.parser.parse_args(arguments)
        if options.file is not None:
            with open(options.file, "r") as file:
                try:
                    return yaml.safe_load(file)
                except yaml.YAMLError as exc:
                    print(exc)
        return vars(options)


if __name__ == "__main__":
    parser = Parser()
    parser.options = parser.parseCLI(sys.argv[1:])
    print(parser.options)
    tags = parser.options.tags
    comment = ""
    if type(tags) is list:
        comment = "+".join(tags)
    elif tags is None:
        raise ParameterException("tags")
    print(comment, tags)
