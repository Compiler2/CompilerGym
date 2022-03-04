// #include <stdbool.h>
#include <time.h>
#include <math.h>
#include <stdio.h>

#define ITER 10

__attribute__((noinline))
double test_bench_func() {
  double sum = 0.0;
  for (int ic = 1; ic <= ITER; ic++) {
    sum += pow(ic, 3);
  }
  return sum;
}

__attribute__((optnone)) int main(int argc, char* argv[]) {
  double ret = test_bench_func();
  printf("*** The bench result is: %f\n", ret);
  return 0;
}
