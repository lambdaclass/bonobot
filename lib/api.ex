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

  def open_connection() do
    Req.post(app_request(), url: "apps.connections.open") |> clean()
  end

  def post_message(channel, text) do
    Req.post(bot_request(),
      url: "chat.postMessage",
      form: %{
        "channel" => channel,
        "text" => text
      }
    )
    |> clean()
  end

  def find_channel_ids(channel_names) do
    with {:ok, %{body: %{"channels" => channels}}} <-
           Req.get(bot_request(), url: "conversations.list") do
      channels
      |> Enum.filter(&Enum.member?(channel_names, &1["name"]))
      |> Enum.map(&Map.get(&1, "id"))
    end
  end

  def get_channel_messages(channel) do
    with {:ok, %{body: %{"messages" => messages}}} <-
           Req.post(bot_request(), url: "conversations.history", form: %{"channel" => channel}) do
      messages
      |> Enum.filter(fn message -> message["type"] == "message" && message["subtype"] == nil end)
      |> Enum.map(&Map.get(&1, "text"))
      |> MapSet.new()
    else
      _ -> MapSet.new()
    end
  end
end
