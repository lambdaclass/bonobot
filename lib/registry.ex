defmodule Bonobot.Registry do
  use Supervisor

  def start_link(_) do
    Supervisor.start_link(__MODULE__, [], name: __MODULE__)
  end

  @impl true
  def init(_) do
    children = [
      {Bonobot.Bot, %{names: ["bot"], channel_names: ["random"]}}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end

  def bots(registry) do
    Supervisor.which_children(registry) |> Enum.map(&elem(&1, 1)) |> Enum.filter(&is_pid/1)
  end
end
