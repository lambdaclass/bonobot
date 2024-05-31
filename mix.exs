defmodule Bonobot.MixProject do
  use Mix.Project

  def project do
    [
      app: :bonobot,
      version: "0.1.0",
      elixir: "~> 1.16",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      mod: {Bonobot, []},
      extra_applications: [:logger]
    ]
  end

  defp deps do
    [
      {:websockex, "~> 0.4.3"},
      {:req, "~> 0.4.14"}
    ]
  end
end
