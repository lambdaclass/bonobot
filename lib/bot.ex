defmodule Bonobot.Bot do
  use GenServer

  def start_link(init) do
    GenServer.start_link(__MODULE__, init)
  end

  @impl true
  def init(token) do
    {:ok, %{token: token}}
  end

  def react_to(bot, event) do
    GenServer.cast(bot, {:event, event})
  end

  @impl true
  def handle_cast({:event, event}, state) do
    state =
      if is_relevant(event) do
        respond_to(event, state)
      else
        state
      end

    {:noreply, state}
  end

  def is_relevant(_) do
    true
  end

  def respond_to(event, state) do
    %{
      "channel" => channel,
      "text" => text
    } = event

    Bonobot.API.post(state[:token], "chat.postMessage", channel: channel, text: text)

    state
  end
end
