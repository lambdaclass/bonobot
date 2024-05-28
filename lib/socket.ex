defmodule Bonobot.Socket do
  require Logger
  use WebSockex

  def start_link(_) do
    {:ok, %{"url" => url}} = Bonobot.API.apps_connections_open()
    WebSockex.start_link(url, __MODULE__, {})
  end

  def handle_frame({:text, msg}, state) do
    case Jason.decode(msg) do
      {:ok, decoded} ->
        handle_text_frame(decoded, state)

      {:error, err} ->
        Logger.error(inspect({err, msg}))
        {:ok, state}
    end
  end

  def handle_frame(frame, state) do
    Logger.debug("Unhandled frame: #{inspect(frame)}")
    {:ok, state}
  end

  def handle_text_frame(%{"type" => "hello"} = message, state) do
    Logger.debug("Connected with Slack #{inspect(message)}")
    {:ok, state}
  end

  def handle_text_frame(
        %{"type" => "events_api", "payload" => %{"event" => event}},
        state
      ) do
    Logger.debug("Event: #{inspect(event)}")

    Bonobot.Registry.bots(Bonobot.Registry)
    |> Enum.each(fn bot -> Bonobot.Bot.react_to(bot, event) end)

    {:ok, state}
  end

  def handle_text_frame(unhandled, state) do
    Logger.debug("Unhandled payload: #{inspect(unhandled)}")
    {:ok, state}
  end
end
