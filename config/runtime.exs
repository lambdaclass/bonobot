import Config

slack_app_token =
  System.get_env("SLACK_APP_TOKEN") ||
    raise """
    environment variable SLACK_APP_TOKEN is missing.
    """

slack_bot_token =
  System.get_env("SLACK_BOT_TOKEN") ||
    raise """
    environment variable SLACK_BOT_TOKEN is missing.
    """

config :bonobot,
  slack_app_token: slack_app_token,
  slack_bot_token: slack_bot_token
