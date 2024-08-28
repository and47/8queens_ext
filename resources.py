from functools import wraps
from typing import Callable


class MySet:
    """Customized set to store (or count unique) solutions and computational dead-ends (DP), with hashing to save RAM
    and optimizations, e.g. adding (duplicate) variations of a passed solution. Based on built-in."""
    __slots__ = ('data', 'optimizations', 'hash')  # use slots for minimal if any extra performance (3-5%?)

    def __init__(self, optimizations):
        self.data = set()
        self.optimizations = optimizations
        self.hash = False

    def add(self, value):
        if not value:
            return
        if self.hash:
            if (the_value := hash(value)) in self.data:
                return
        elif (the_value := value) in self.data:
            return
        self.data.add(the_value)
        for transformed_solution in self.optimizations(solution=value):
            self.data.add(hash(transformed_solution) if self.hash else transformed_solution)

    def __contains__(self, value):
        return hash(value) in self.data if self.hash else value in self.data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)


def cache_nosolutions_inputs(cache: set = set(), values: set = {frozenset()}, inputs: tuple[int] = [0],
                             cached_return=frozenset()) -> Callable:
    """
    custom cache decorator, only memoizes when no solutions found. capture remaining coords and items leading to dead
      end. optionally hashes to reduce cache's memory use.
      also, it ignores given positional args, e.g. which carries "current solution" or optional ones.
    :param cache: object implementing  __contains__ (incl. e.g. input args processing, hashing) and add (incl. e.g.
     combos of `values`), e.g. bitset, bloom filter, or Python Set
    :param values: set of resulting values (returned by decorated function), for which inputs should be cached
    :param inputs: list of index or indices of input arguments that should be cached
    :param cached_return: value to return for cached input, usually part of `values`

    """

    def decorator(func: Callable):
        @wraps(func)  # to keep metadata for user's or IDE introspection
        def wrapper(*args, **kwargs):

            _args = (*args, *kwargs.values())

            inp_k = frozenset(_args[inputs[0]]) if len(inputs) == 1 else \
                        tuple(x for i, x in enumerate(_args) if i in inputs)
            if inp_k in cache:
                wrapper.cache_hits += 1
                return cached_return

            result = func(*args, **kwargs)  # call the expensive function for new inputs (coords filled with vnts)

            if not result or result in values:
                cache.add(inp_k)  # all inputs variants (or only original) cached (possibly in hashed or reduced form)

            return result

        wrapper.cache_hits = 0  # counter to track use of cache for debugging or later proper logging.
        return wrapper if cache is not None else func
    return decorator
