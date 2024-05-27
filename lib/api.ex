defmodule Bonobot.API do
  require Logger

  @base_url "https://slack.com/api"

  def new() do
    token = Application.fetch_env!(:bonobot, :slack_bot_token)
    Req.new(base_url: @base_url, auth: {:bearer, token})
  end

  def get(endpoint, args \\ %{}) do
    Req.get(new(),
      url: endpoint,
      params: args
    )
    |> clean()
  end

  def post(endpoint, args \\ %{}) do
    Req.post(new(),
      url: endpoint,
      form: args
    )
    |> clean()
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
end
