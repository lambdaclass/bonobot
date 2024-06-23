defmodule Bonobot.ShareBot do
  @moduledoc """
  When mentioned, it responds with a random
  message taken from selected channels
  """

  use Bonobot.Bot

  defmodule State do
    @enforce_keys [:names, :channels]
    defstruct [:names, :channels]

    @typedoc """
    - names: the names which the bot responds to
    - channels: the channels (by id) the bot takes its responses from
    """
    @type t :: %State{names: list(String), channels: list(String)}
  end

  @impl true
  def init(%{names: names, channel_names: channels}) do
    state = %State{
      names: names,
      channels: Bonobot.API.find_channel_ids(channels)
    }

    {:ok, state}
  end

  @impl true
  def handle_event(event, state) do
    if is_relevant(event, state) do
      respond_to(event, state)
    else
      state
    end
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
