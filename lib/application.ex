defmodule Bonobot do
  use Application

  def start(_type, _args) do
    slack_bot_token = Application.fetch_env!(:bonobot, :slack_bot_token)

    children = [
      {Bonobot.Socket, slack_bot_token}
    ]

    Supervisor.start_link(children, strategy: :one_for_one)
  end
end
