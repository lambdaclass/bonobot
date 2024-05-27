defmodule Bonobot.Registry do
  use Supervisor

  def start_link(token) do
    Supervisor.start_link(__MODULE__, token, name: __MODULE__)
  end

  @impl true
  def init(token) do
    children = [
      {Bonobot.Bot, token}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end

  def bots(registry) do
    Supervisor.which_children(registry) |> Enum.map(&elem(&1, 1)) |> Enum.filter(&is_pid/1)
  end
end
