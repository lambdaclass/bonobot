import Config

slack_bot_token =
  System.get_env("SLACK_BOT_TOKEN") ||
    raise """
    environment variable SLACK_BOT_TOKEN is missing.
    """

config :bonobot,
  slack_bot_token: slack_bot_token
