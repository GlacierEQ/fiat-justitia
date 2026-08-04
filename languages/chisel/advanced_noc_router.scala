package tower

import chisel3._
import chisel3.util._

/** Chisel — Advanced Example: Parameterized Credit-Aware NoC Router
  *
  * What: Routes flits from N input ports to N output ports using destination
  *       fields, round-robin arbitration, and explicit ready/valid flow control.
  * Where: RISC-V SoCs, reusable interconnect generators, accelerator meshes.
  * When: Use when hardware structure should be generated from parameters, not copied RTL.
  * Why: Chisel makes port counts, widths, and arbitration policy programmable.
  * How: Parameter checks, Decoupled flits, RRArbiter per output, and destination decode.
  */
class Flit(val width: Int, val destinationWidth: Int) extends Bundle {
  val destination = UInt(destinationWidth.W)
  val payload     = UInt(width.W)
  val last        = Bool()
}

class AdvancedNoCRouter(
    width: Int = 64,
    ports: Int = 4
) extends Module {
  require(width >= 8, s"payload width must be >= 8, got $width")
  require(ports >= 2, s"router needs >= 2 ports, got $ports")
  require(ports <= 16, s"router ports capped at 16 for this exhibit, got $ports")

  private val destinationWidth = log2Ceil(ports)

  val io = IO(new Bundle {
    val in  = Flipped(Vec(ports, Decoupled(new Flit(width, destinationWidth))))
    val out = Vec(ports, Decoupled(new Flit(width, destinationWidth)))
    val activeCount = Output(UInt(log2Ceil(ports + 1).W))
  })

  val arbiters = Seq.fill(ports) {
    Module(new RRArbiter(new Flit(width, destinationWidth), ports))
  }

  // Per-output arbitration: only inputs targeting this output compete.
  for (outPort <- 0 until ports) {
    for (inPort <- 0 until ports) {
      val selected =
        io.in(inPort).valid &&
          (io.in(inPort).bits.destination === outPort.U(destinationWidth.W))
      arbiters(outPort).io.in(inPort).valid := selected
      arbiters(outPort).io.in(inPort).bits  := io.in(inPort).bits
    }
    io.out(outPort) <> arbiters(outPort).io.out
  }

  // Input ready is true when the destination output's arbiter grants ready.
  for (inPort <- 0 until ports) {
    val readyBits = Wire(Vec(ports, Bool()))
    for (outPort <- 0 until ports) {
      readyBits(outPort) :=
        arbiters(outPort).io.in(inPort).ready &&
          (io.in(inPort).bits.destination === outPort.U(destinationWidth.W))
    }
    io.in(inPort).ready := readyBits.asUInt.orR
  }

  // Observability: how many inputs currently hold valid flits.
  io.activeCount := PopCount(VecInit(io.in.map(_.valid)).asUInt)

  // Simulation-only sanity: destination must be in range when valid.
  for (inPort <- 0 until ports) {
    when(io.in(inPort).valid) {
      assert(
        io.in(inPort).bits.destination < ports.U,
        cf"input $inPort destination out of range"
      )
    }
  }
}

object AdvancedNoCRouter extends App {
  emitVerilog(new AdvancedNoCRouter(width = 64, ports = 4))
}
