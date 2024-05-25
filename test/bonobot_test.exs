defmodule BonobotTest do
  use ExUnit.Case
  doctest Bonobot

  test "greets the world" do
    assert Bonobot.hello() == :world
  end
end
