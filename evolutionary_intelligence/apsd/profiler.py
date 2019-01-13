import cProfile


def do_profile(func):
    """
    profiling tool for python
    (https://zapier.com/engineering/profiling-python-boss/)

    we can put this annotation above to function:
        @profiler.do_profile
    """

    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func