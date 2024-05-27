defmodule Bonobot.Bot do
  use GenServer

  def start_link(init) do
    GenServer.start_link(__MODULE__, init)
  end

  @impl true
  def init(init) do
    {:ok, init}
  end

  def react_to(bot, event) do
    GenServer.cast(bot, {:event, event})
  end

  @impl true
  def handle_cast({:event, event}, state) do
    IO.puts("#{inspect(self())}: #{inspect(event)}'")
    {:noreply, state}
  end
end
