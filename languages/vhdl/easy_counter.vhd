library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity easy_counter is
  port (
    clk     : in std_logic;
    reset_n : in std_logic;
    value   : out unsigned(7 downto 0)
  );
end entity;

architecture rtl of easy_counter is
  signal state : unsigned(7 downto 0) := (others => '0');
begin
  process(clk, reset_n)
  begin
    if reset_n = '0' then
      state <= (others => '0');
    elsif rising_edge(clk) then
      state <= state + 1;
    end if;
  end process;
  value <= state;
end architecture;
