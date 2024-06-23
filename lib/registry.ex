defmodule Bonobot.Registry do
  @moduledoc """
  Supervises the different bots in the application

  On startup, it spawns and supervises all the `Bonobot.Bot`s defined
  in the `Bonobot.Registry.init` function.

  The process is globally accessed by its module name.
  """

  use Supervisor

  def start_link(_) do
    Supervisor.start_link(__MODULE__, [], name: __MODULE__)
  end

  @impl true
  def init(_) do
    children = [
      {Bonobot.ShareBot, %{names: ["bot"], channel_names: ["random"]}}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end

  @doc """
  Returns the list of active bots (by their pids)
  """
  def bots(registry) do
    Supervisor.which_children(registry) |> Enum.map(&elem(&1, 1)) |> Enum.filter(&is_pid/1)
  end
end
