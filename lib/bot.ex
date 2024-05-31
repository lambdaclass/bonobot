defmodule Bonobot.Bot do
  use GenServer

  defmodule State do
    @enforce_keys [:names, :channels]
    defstruct [:names, :channels]
  end

  def start_link(state) do
    GenServer.start_link(__MODULE__, state)
  end

  @impl true
  def init(%{names: names, channel_names: channels}) do
    state = %State{
      names: names,
      channels: Bonobot.API.find_channel_ids(channels)
    }

    {:ok, state}
  end

  def react_to(bot, event) do
    GenServer.cast(bot, {:event, event})
  end

  @impl true
  def handle_cast({:event, event}, state) do
    state =
      if is_relevant(event, state) do
        respond_to(event, state)
      else
        state
      end

    {:noreply, state}
  end

  defp is_relevant(event, state) do
    with text when not is_nil(text) <- event["text"] do
      String.contains?(text, state.names)
    else
      _ -> false
    end
  end

  defp respond_to(event, state) do
    %{
      "channel" => channel
    } = event

    response = Enum.random(possible_responses(state))
    Bonobot.API.post_message(channel, response)

    state
  end

  defp possible_responses(state) do
    state.channels
    |> Enum.map(&Bonobot.API.get_channel_messages/1)
    |> Enum.reduce(&MapSet.union/2)
  end
end
