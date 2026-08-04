-- VHDL — Advanced Example: Triple-Modular-Redundancy Voter
--
-- What: Majority-votes three redundant data lanes, reports per-lane disagreement,
--       and asserts when all three lanes diverge.
-- Where: Aerospace, defense, safety-critical FPGA/ASIC control paths.
-- When: Use when single-event upsets or lane faults must be tolerated in hardware.
-- Why: VHDL's strong typing and concurrent signal model make reviewable TMR explicit.
-- How: Bitwise majority logic, mismatch vector, and severity-graded assertions.

library ieee;
use ieee.std_logic_1164.all;

entity fault_tolerant_voter is
  generic (
    WIDTH : positive := 32
  );
  port (
    clk      : in  std_logic;
    rst      : in  std_logic;
    lane_a   : in  std_logic_vector(WIDTH-1 downto 0);
    lane_b   : in  std_logic_vector(WIDTH-1 downto 0);
    lane_c   : in  std_logic_vector(WIDTH-1 downto 0);
    voted    : out std_logic_vector(WIDTH-1 downto 0);
    mismatch : out std_logic_vector(2 downto 0);  -- bit0=A, bit1=B, bit2=C disagree with majority
    valid    : out std_logic
  );
end entity fault_tolerant_voter;

architecture rtl of fault_tolerant_voter is
  signal majority : std_logic_vector(WIDTH-1 downto 0);
  signal mm_a     : std_logic;
  signal mm_b     : std_logic;
  signal mm_c     : std_logic;
  signal all_diverge : std_logic;
begin
  -- Combinational majority vote per bit.
  majority <= (lane_a and lane_b) or (lane_a and lane_c) or (lane_b and lane_c);

  mm_a <= '0' when lane_a = majority else '1';
  mm_b <= '0' when lane_b = majority else '1';
  mm_c <= '0' when lane_c = majority else '1';

  all_diverge <= '1' when (lane_a /= lane_b and lane_a /= lane_c and lane_b /= lane_c) else '0';

  sequential : process(clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        voted    <= (others => '0');
        mismatch <= (others => '0');
        valid    <= '0';
      else
        voted    <= majority;
        mismatch <= mm_c & mm_b & mm_a;
        valid    <= not all_diverge;
      end if;
    end if;
  end process sequential;

  -- Design-time / simulation assertions (not synthesizable side effects).
  check_width : process
  begin
    assert WIDTH >= 1
      report "WIDTH must be positive"
      severity failure;
    wait;
  end process check_width;

  check_divergence : process(lane_a, lane_b, lane_c)
  begin
    assert all_diverge = '0'
      report "TMR total disagreement: all three lanes diverge"
      severity warning;
  end process check_divergence;
end architecture rtl;
