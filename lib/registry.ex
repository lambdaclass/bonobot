defmodule Bonobot.Registry do
  use Supervisor

  def start_link(_) do
    Supervisor.start_link(__MODULE__, nil, name: __MODULE__)
  end

  @impl true
  def init(_) do
    children = [
      Supervisor.child_spec(Bonobot.Bot, id: :bot1),
      Supervisor.child_spec(Bonobot.Bot, id: :bot2)
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end

  def bots(registry) do
    Supervisor.which_children(registry) |> Enum.map(&elem(&1, 1)) |> Enum.filter(&is_pid/1)
  end
end
