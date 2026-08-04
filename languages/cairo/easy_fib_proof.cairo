// Easy Exhibit: Cairo Verifiable Fibonacci Function
func fib(n: felt) -> (res: felt) {
    if (n == 0) {
        return (res=0);
    }
    if (n == 1) {
        return (res=1);
    }
    let (a) = fib(n - 1);
    let (b) = fib(n - 2);
    return (res=a + b);
}
