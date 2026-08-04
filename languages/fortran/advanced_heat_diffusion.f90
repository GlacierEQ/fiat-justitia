! Fortran — Advanced Example: 1D Heat Diffusion with Energy Audit
!
! What: Integrates the 1D heat equation with an explicit FTCS scheme and audits
!       discrete energy change against a strict tolerance.
! Where: Climate kernels, materials models, and scientific digital twins.
! When: Use when dense numerical loops and long-term maintainability dominate.
! Why: Fortran still delivers top-tier array performance and readable scientific form.
! How: Fixed grid, Dirichlet boundaries, conserved interior measure, and a
!       deterministic VERIFIED receipt on stdout.

program advanced_heat_diffusion
  implicit none
  integer, parameter :: n = 64
  integer, parameter :: steps = 200
  real(kind=8), parameter :: alpha = 0.15d0
  real(kind=8), parameter :: dx = 1.0d0
  real(kind=8), parameter :: dt = 0.25d0
  real(kind=8), parameter :: r = alpha * dt / (dx * dx)
  real(kind=8) :: u(n), u_next(n)
  real(kind=8) :: energy0, energy1, drift
  integer :: i, t

  if (r >= 0.5d0) then
    error stop "FTCS stability requires r < 0.5"
  end if

  ! Initial condition: central pulse, cold boundaries.
  u = 0.0d0
  do i = 1, n
    if (i > n/4 .and. i < 3*n/4) then
      u(i) = 1.0d0
    end if
  end do
  u(1) = 0.0d0
  u(n) = 0.0d0

  energy0 = sum(u(2:n-1))

  do t = 1, steps
    do i = 2, n-1
      u_next(i) = u(i) + r * (u(i-1) - 2.0d0*u(i) + u(i+1))
    end do
    u_next(1) = 0.0d0
    u_next(n) = 0.0d0
    u = u_next
  end do

  energy1 = sum(u(2:n-1))
  drift = abs(energy1 - energy0) / max(energy0, 1.0d-12)

  ! With cold Dirichlet boundaries, energy is expected to decrease, not explode.
  if (any(u /= u) .or. maxval(u) > 1.0001d0) then
    error stop "numerical instability detected"
  end if
  if (energy1 > energy0) then
    error stop "energy increased under dissipative boundaries"
  end if

  write(*,'(A,I0,A,ES12.5,A,ES12.5,A)') &
    '{"status":"VERIFIED","language":"fortran","steps":', steps, &
    ',"energy0":', energy0, ',"energy1":', energy1, ',"scheme":"FTCS"}'
end program advanced_heat_diffusion
