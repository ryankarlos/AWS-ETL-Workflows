import line_profiler
import atexit
from main_twitter import handler
import click


def profiled_function():
    from secrets import get_secrets
    from tweets_api import MyStreamListener
    from tweets_api import tweepy_search_api


@click.command()
@click.argument("keyword", type=click.STRING)
@click.option(
    "--delivery",
    default="search",
    type=click.Choice(["search", "realtime"]),
    help="mode of delivery, using search api or realtime streaming api",
)
@click.option(
    "--duration",
    default=15,
    type=click.INT,
    help="How long (secs) to let stream run before disconnecting",
)
@click.option(
    "--test_import_speeds",
    default=False,
    type=click.BOOL,
    help="Uses line profiler to test speed of " "imports of custom util functions",
)
@click.option(
    "--kinesis_stream_name",
    default="",
    type=click.STRING,
    help="If kinesis stream name passed, individual records " "also put into stream",
)
def main(keyword, delivery, duration, test_import_speeds, kinesis_stream_name):
    """
    function for checking/testing tweepy streaming and search api locally before deploying as lambda image container
    For 'realtime' delivery - may need to use a trending topic as 'keyword' otherwise will have to wait a while to
    get anything. Multiple calls in short time window to streaming api may invoke 420 error.
    If test import speed option is set as True, the import stats will be reported before the script ends
    """

    if test_import_speeds:
        profile = line_profiler.LineProfiler()
        atexit.register(profile.print_stats)
        import_speeds = profile(profiled_function)
        import_speeds()

    event = {
        "keyword": keyword,
        "delivery": delivery,
        "duration": duration,
        "kinesis_stream_name": kinesis_stream_name,
    }

    context = {}
    handler(event, context)


if __name__ == "__main__":
    main()
