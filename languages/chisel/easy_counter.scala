package tower

import chisel3._

class EasyCounter(width: Int = 8) extends Module {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val value = Output(UInt(width.W))
  })
  val counter = RegInit(0.U(width.W))
  when(io.enable) { counter := counter + 1.U }
  io.value := counter
}

object EasyCounter extends App {
  emitVerilog(new EasyCounter())
