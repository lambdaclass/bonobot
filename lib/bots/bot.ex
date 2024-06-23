defmodule Bonobot.Bot do
  @moduledoc """
  A GenServer that controls a specific slack bot user

  The main way to interact with the bot is through `react_to`.
  """

  defmacro __using__(_) do
    quote do
      use GenServer
      @behaviour Bonobot.Bot

      def start_link(opts) do
        GenServer.start_link(__MODULE__, opts)
      end

      def handle_cast({:event, event}, state) do
        state = handle_event(event, state)

        {:noreply, state}
      end
    end
  end

  @doc """
  Sends an `:event` to the bot
  """
  def react_to(bot, event) do
    GenServer.cast(bot, {:event, event})
  end

  @doc """
  Reacts to an `:event` cast

  The bot should decide if it's a relevant event and responds appropiately.
  """
  @callback handle_event(event :: any, state :: any) :: any
end
