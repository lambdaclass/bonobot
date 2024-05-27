defmodule Bonobot.API do
  require Logger

  @base_url "https://slack.com/api"

  def new(token) do
    Req.new(base_url: @base_url, auth: {:bearer, token})
  end

  def get(token, endpoint, args \\ %{}) do
    Req.get(new(token),
      url: endpoint,
      params: args
    )
    |> clean()
  end

  def post(token, endpoint, args \\ %{}) do
    Req.post(new(token),
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
