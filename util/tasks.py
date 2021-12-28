import asyncio
import concurrent.futures
import functools
from util import logger as log


# async def run_blocking_code(client, funcs, *args, **kwargs) -> list:
#     """Run blocking code safely in a new thread.
#
#     DO NOT pass in an asynchronous function. If an asynchronous function has blocking code, the event loop will
#     also block. There were several attempts made to make it compatible with asynchronous functions, but it was a
#     headache to work with.
#
#     :param client: Asynchronous client containing the asynchronous loop.
#     :param funcs: The blocking function that needs to be called.
#         May also pass in a list of functions
#         with the 0th index as the callable function,
#         the 1st index as the args for that function,
#         and the 2nd index as the kwargs for that function.
#     :param args: The args to pass into the blocking function.
#     :param kwargs: The keyword args to pass into the blocking function.
#     :returns: List of results in no particular order. Make sure the output can be managed with no specific order.
#     """
#     loop = asyncio.get_running_loop()
#     try:
#         with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
#             results = []  # a list of results
#             if not isinstance(funcs, list):
#                 funcs = [[funcs, args, kwargs]]
#
#             for func in funcs:
#                 callable_function = func[0]
#                 func_args = func[1]
#                 func_kwargs = func[2]
#                 if callable(callable_function):
#                     results.append(await loop.run_in_executor(pool, functools.partial(callable_function,
#                                                                                       *func_args, **func_kwargs)))
#
#             log.info(f'Custom Thread Pool -> {func}', method=run_blocking_code)
#
#             return results
#
#     except AttributeError as e:
#         log.info(f"{e} (AttributeError)", method=run_blocking_code, event_loop=client.loop)
#     except Exception as e:
#         log.info(f"{e} (Exception)", method=run_blocking_code, event_loop=client.loop)
#     return []
#
#

