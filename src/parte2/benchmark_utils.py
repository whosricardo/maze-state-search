from statistics import mean
from time import perf_counter


DEFAULT_REPETITIONS = 5


def benchmark_call(
    function,
    repetitions=DEFAULT_REPETITIONS,
):
    times = []

    for _ in range(repetitions):
        initial_time = perf_counter()
        function()
        final_time = perf_counter()
        times.append(final_time - initial_time)

    average = mean(times) if times else 0.0

    return {
        "runs_seconds": times,
        "mean_seconds": average,
    }
