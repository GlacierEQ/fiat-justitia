! Fortran — Easy Example: Deterministic Hello
!
! What: Prints a stable greeting and exits successfully.
! Where: HPC bootstrap, numerical CI smoke, and scientific kernels.
! When: Use when the operational boundary is long-lived numerical Fortran code.
! Why: Fortran remains the performance baseline for large scientific workloads.
! How: A single program unit with no external libraries.

program easy_hello
  implicit none
  print '(A)', '{"status":"VERIFIED","language":"fortran","message":"hello-tower"}'
end program easy_hello
