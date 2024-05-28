defmodule Bonobot.API do
  require Logger

  @base_url "https://slack.com/api"

  def app_request() do
    token = Application.fetch_env!(:bonobot, :slack_app_token)
    Req.new(base_url: @base_url, auth: {:bearer, token})
  end

  def bot_request() do
    token = Application.fetch_env!(:bonobot, :slack_bot_token)
    Req.new(base_url: @base_url, auth: {:bearer, token})
  end

  def clean(result) do
    case result do
      {:ok, %{body: %{"ok" => true} = body}} ->
        {:ok, body}

      {_, error} ->
        Logger.error(inspect(error))
        {:error, error}
    end
  end

  def apps_connections_open() do
    Req.post(app_request(), url: "apps.connections.open") |> clean()
  end

  def chat_post_message(channel, text) do
    Req.post(bot_request(),
      url: "chat.postMessage",
      form: %{
        "channel" => channel,
        "text" => text
      }
    )
    |> clean()
  end
end
