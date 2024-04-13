"""
Part of a library/package I am currently writing to test HTTP request perfomrance using different methods.
Written 2024.
----
Module/script to set up/perform HTTP request experiment runs.

Objects, methods, and functions to enable/manage runs (sequences of 
similar API calls)—in line with parameters specified in configuration. 
Includes a class for each library used to make HTTP requests. Each of 
these classes, in turn, mimics the same standard set of possible runs 
using the respective library's functionality, as available (i.e., 
singular/batched; synchronous/asynchronous; using asyncio's "task 
group"/"as compelted"/"gather" frameworks, and with/without an eager 
task factory).
"""

# DEPENDENCIES
## Standard library
import asyncio # asynchronous I/O
import concurrent.futures # general parallelism
from contextlib import contextmanager, nullcontext # context management
from functools import wraps # higher-order function management
import os # operating system and directory manipulation
# import multiprocessing # process-based parallelism
# import threading # thread-based parallelism
from typing import Any, Awaitable, Callable, Coroutine, Generator, Optional # type-hinting # NOT SURE IF I NEED AWAITABLE OR COROUTINE
import time # function timing
import toml

## Thrid-party library
import requests # synchronous HTTP requests
# from requests.auth import HTTPBasicAuth, HTTPDigestAuth
# from requests_oauthlib import OAuth1
import httpx # general HTTP requests
import aiohttp # asynchronous HTTP requests

## Local library


# DIRECTORIES
# ROOT_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
# SRC_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
PKG_DIR = os.path.join(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(PKG_DIR, "config.toml")

# CONFIGURATION
def load_global_config() -> dict:
    """Load global configuration as dictionary.

    Returns
    -------
    dict
        Configuration dictionary.
    """
    with open(CONFIG_PATH, 'r') as f:
        return toml.load(f)
 
 
def update_global_config(config: dict) -> None:
    """
    Modify/add values in global configuration file (by rewriting on the 
    basis of local dictionary).

    Parameters
    ----------
    config : dict
        Configuration dictionary to save.

    Notes
    -----
    Changes must be assigned to relevant configuration tables and 
    keys before running. The given dictionary input will overwrite the 
    entire configuration file, so it must include unchanged values as
    well as those meant to be modified.
    """
    # Write modified config back to the file
    with open(CONFIG_PATH, 'w') as f:
        toml.dump(config, f)

# DECORATORS
# Need to review type-hinting throughout (and within these decorators, 
# wrappers, etc.) to ensure proper specifications with synchronous and 
# asynchronous options
def timer(identifier: Optional[str] = None) -> Callable | Coroutine: # double type hinting throughout outer and inner functions (also learn about generator typing and typing for wrappers within decorators)
    """Decorator factory to time functions.

    Parameters
    ----------
    identifier : str, optional
        Text to identify function in print statement with run-time.

    Returns
    -------
    callable or coroutine
        Timed function results.
    
    Notes
    -----
    Intended to be used as a decorator or a stand-alone function.
    """
    # Create a context manager to minimize redundancy
    @contextmanager
    def timing_context(message: str) -> Generator[any, any, any]:
        """Context manager to time decorated function, whether it 
        requires a synchronous or asynchronous wrapper."""
        message = f"{message} COMPLETE "
        start = time.perf_counter()
        yield
        print(f'{message:-<20}--- {time.perf_counter() - start:,.10f}')
    
    @wraps(timer)
    def decorator(func: Callable | Coroutine) -> Callable | Coroutine:
        message = identifier
        if not identifier:
            message = f"{func.__qualname__} EXECUTION"

        # Create asynchronous or synchronous wrapper to match nature of 
        # enclosed function
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any :
                with timing_context(message):
                    return await func(*args, **kwargs)
            return async_wrapper
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with timing_context(message):
                return func(*args, **kwargs)
        return sync_wrapper
    return decorator


def make_eager(func: Coroutine) -> Coroutine:
    """
    Run asynchrnonous function in eager task factory.

    Parameters
    ----------
    func : coroutine
        Coroutine to run.
    
    Notes
    -----
    Intended to be used as a decorator or a stand-alone function.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Coroutine:
        asyncio.get_event_loop().set_task_factory(asyncio.eager_task_factory)
        return await func(*args, **kwargs)
    return wrapper


@contextmanager
def eager_task_factory() -> Generator[any, any, any]:
    """Context manager to run asynchronous function in eager event loop.

    Yields
    ------
    generator
        Results of performing function in the context of an eager task
        factory.
    """
    asyncio.get_event_loop().set_task_factory(asyncio.eager_task_factory)
    yield


# CLASSES
class Run:
    """Object to handle HTTP request experiment runs.
    
    Attributes
    ----------
    volume_limit : int, optional
        Volume of requests permitted in a given period (defined by 
        rate-limit of service).
    period_limit : int, optional
        Period within which given volume of requests is permitted 
        (defined by rate-limit of service).
    """

    def __init__(self, volume_limit: Optional[int] = None, 
                period_limit: Optional[int] = None,
                concur_limit: Optional[int] = None) -> None:
        """
        Initialize HTTP client with proper authentication and 
        rate-limiting.

        Parameters
        ----------
        volume_limit : int, optional
            Volume of requests permitted in a given period (defined by 
            rate-limit of service).
        period_limit : int, optional
            Period within which given volume of requests is permitted 
            (defined by rate-limit of service).
        concur_limit : int, optional
            Maximum number of tasks to run concurrently.
        """
        self.volume_limit = volume_limit
        self.period_limit = period_limit
        self.concur_limit = concur_limit
        self.sem = asyncio.Semaphore(concur_limit) if concur_limit else None
    
    def auth(self, method: Optional[str] = Optional[str]) -> None:
        """
        Create authentication object to accompany requests.

        Parameters
        ----------
        method : {None, 'basic', 'token', 'oauth'}
            Authentication method.
        username : str, optional
            Username for basic authentication.
        password : str, optional
            Password for basic authentication.
        key : str, optional
            API key.
        token : str, optional
            API token.
        client_id: str, optional
            OAuth client id.
        client_secret : str, optional
            OAuth client secret.
        """
        raise NotImplementedError("Placeholder for future implementation.")
        
    def _limit_rate(self):
        """Enforce specified rate-limit."""
        raise NotImplementedError("Placeholder for future implementation.")


class RequestsRun(Run):
    """Object to handle HTTP requests with the "requests" package."""
    
    @timer("REQUESTS-SINGLE-SYNC")
    def get_single_sync(self, url: str) -> str:
        """
        Perform a single HTTP request, synchronously.

        Parameters
        ----------
        url : str
            Endpoint/URL to reach desired resource.

        Returns
        -------
        str
            HTTP response.
        """
        r = requests.get(url)
        return r.text

    @timer("REQUESTS-MANY-SYNC")
    def get_many_sync(self, url_list: list[str]) -> list[str]:
        """
        Perform several HTTP requests, synchronously.

        Parameters
        ----------
        url_list : list of str
            List of endpoints/URLs to reach desired resources.

        Returns
        -------
        list of str
            List of HTTP responses.
        """
        data = []
        with requests.Session() as s:
            for url in url_list:
                r = s.get(url)
                data.append(r.text)
        return data


class HttpxRun(Run):
    """Object to handle HTTP requests with the "httpx" package."""

    @timer("HTTPX-SINGLE-SYNC")
    def get_single_sync(self, url: str) -> str:
        """
        Perform a single HTTP request, synchronously.

        Parameters
        ----------
        url : str
            Endpoint/URL to reach desired resource.

        Returns
        -------
        str
            HTTP response.
        """
        r = httpx.get(url)
        return r.text

    @timer("HTTPX-MANY-SYNC")
    def get_many_sync(self, url_list: list[str]) -> list[str]:
        """
        Perform several HTTP requests, synchronously.

        Parameters
        ----------
        url_list : list of str
            List of endpoints/URLs to reach desired resources.

        Returns
        -------
        list of str
            List of HTTP responses.
        """
        data = []
        with httpx.Client(timeout = None) as client:
            for url in url_list:
                r = client.get(url)
                data.append(r.text)
        return data
    
    async def _get_single_async(self, client: httpx.AsyncClient, 
                                url: str) -> dict:
        """
        Perform a single HTTP request, asynchronously.

        Parameters
        ----------
        url : str
            Endpoint/URL to reach desired resource.

        Returns
        -------
        str
            HTTP response.
        """
        r = await client.get(url)
        return r.text

    @timer("HTTPX-MANY-ASYNC - AS COMPLETED")
    async def get_many_async_as_completed(self, url_list: list[str],
                                          eager: bool = False) -> list[str]:
        """
        Perform several HTTP requests, asynchronously.

        Parameters
        ----------
        url_list : list of str
            List of endpoints/URLs to reach desired resources.

        Returns
        -------
        list of str
            List of HTTP responses.
        """
        data = []
        with eager_task_factory() if eager else nullcontext():
            async with httpx.AsyncClient(timeout = None) as client:
                awaitables = [self._get_single_async(client, url) for url in url_list]
                for coro in asyncio.as_completed(awaitables):
                    data.append(await coro)
            return data

    @timer("HTTPX-MANY-ASYNC - GATHER")
    async def get_many_async_gather(self, url_list: list[str], 
                                    eager: bool = False) -> list[str]:
        """
        Perform several HTTP requests, asynchronously.

        Parameters
        ----------
        url_list : list of str
            List of endpoints/URLs to reach desired resources.

        Returns
        -------
        list of str
            List of HTTP responses.
        """
        with eager_task_factory() if eager else nullcontext():
            async with httpx.AsyncClient(timeout = None) as client:
                awaitables = [self._get_single_async(client, url) for url in url_list]
                return await asyncio.gather(*awaitables)

    @timer("HTTPX-MANY-ASYNC - TASK GROUP")
    async def get_many_async_taskgroup(self, url_list: list[str],
                                       eager: bool = False) -> list[str]:
        """
        Perform several HTTP requests, asynchronously.

        Parameters
        ----------
        url_list : list of str
            List of endpoints/URLs to reach desired resources.

        Returns
        -------
        list of str
            List of HTTP responses.
        """
        results = []
        with eager_task_factory() if eager else nullcontext():
            async with httpx.AsyncClient(timeout = None) as client:
                async with asyncio.TaskGroup() as tg:
                    for url in url_list:
                        results.append(
                            tg.create_task(self._get_single_async(client, url))
                        )
            return [result.result() for result in results]


class AiohttpRun(Run):
    """Object to handle HTTP requests with the "aiohttp" package."""

    async def _get_single_async(self, session: aiohttp.ClientSession, 
                                url: str) -> str:
        """
        Perform single HTTP request, asynchronously.

        Parameters
        ----------
        url : str
            Endpoint/URL to reach desired resource.

        Returns
        -------
        str
            HTTP response.
        """
        async with session.get(url) as response:
            return await response.text()

    @timer("AIOHTTP-MANY-ASYNC - AS COMPLETED")
    async def get_many_async_as_completed(self, url_list: list[str], 
                                          eager: bool = False) -> list[str]:
        """
        Perform several HTTP requests, asynchronously.

        Parameters
        ----------
        url : str
            Endpoint/URL to reach desired resource.

        Returns
        -------
        str
            HTTP response.
        """
        data = []
        with eager_task_factory() if eager else nullcontext():
            async with aiohttp.ClientSession() as session:
                awaitables = [self._get_single_async(session, url) for url in url_list]
                for coro in asyncio.as_completed(awaitables):
                    data.append(await coro)
            return data

    @timer("AIOHTTP-MANY-ASYNC - GATHER")
    async def get_many_async_gather(self, url_list: list[str],
                                    eager: bool = False) -> list[str]:
        """
        Perform several HTTP requests, asynchronously.

        Parameters
        ----------
        url_list : list of str
            List of endpoints/URLs to reach desired resources.

        Returns
        -------
        list of str
            List of HTTP responses.
        """
        with eager_task_factory() if eager else nullcontext():
            async with aiohttp.ClientSession() as session:
                awaitables = [self._get_single_async(session, url) for url in url_list]
                return await asyncio.gather(*awaitables)
 
    @timer("AIOHTTP-MANY-ASYNC - TASK GROUP")
    async def get_many_async_taskgroup(self, url_list: list[str], 
                                       eager: bool = False) -> list[str]:
        """
        Perform several HTTP requests, asynchronously.

        Parameters
        ----------
        url_list : list of str
            List of endpoints/URLs to reach desired resources.
        eager : bool, default=True
            Whether to make asynchronous task factory eager.

        Returns
        -------
        list of str
            List of HTTP responses.
        """
        results = []
        with eager_task_factory() if eager else nullcontext():
            async with aiohttp.ClientSession() as session:
                async with asyncio.TaskGroup() as tg:
                    for url in url_list:
                        results.append(
                            tg.create_task(self._get_single_async(session, url))
                        ) # can also create task at the level of the response retrieval or at both levels
                        # review convention for continuation indent above
            return [result.result() for result in results]


# FUNCTIONS
def main() -> None:
    """"""
    # CONFIGURATION
    config = load_global_config()

    # configure HTTP request packages
    USE_REQUESTS = config['package']['use_requests']
    USE_HTTPX = config['package']['use_httpx']
    USE_AIOHTTP = config['package']['use_aiohttp']

    # configure synchronicity
    RUN_SYNC = config['synchronicity']['run_sync']
    RUN_ASYNC = config['synchronicity']['run_async']

    # configure task factory
    TASK_FACTORY = config['asynchronous']['task_factory']

    # configure task execution
    TASK_EXECUTION = config['asynchronous']['task_execution']

    # configure experiment repetition
    RUN_FREQ = 1000

    # TEST_URL = "https://httpstat.us/200"
    TEST_URL = "https://fakerapi.it/api/v1/books?_quantity=1"

    # ITERATE THROUGH RUNS

    buffer = time.sleep(60) # cool-off to prevent rate-limits from executing runs one after the other

    runs = []
    if USE_REQUESTS:
        runs.append(RequestsRun())
    if USE_HTTPX:
        runs.append(HttpxRun())
    if USE_AIOHTTP:
        runs.append(AiohttpRun())

    for run in runs:
        if RUN_SYNC and any("_sync" in func_name for func_name in dir(run)):
            run.get_single_sync(TEST_URL)
            buffer
            run.get_many_sync([TEST_URL] * RUN_FREQ)           
        
        if RUN_ASYNC and any("async" in func_name for func_name in dir(run)):
            for factory, use in TASK_FACTORY.items():
                eager = False
                if factory == "eager" and use:
                    eager = True
                print(f"{factory} {use!s:-<60}")
                buffer
                if TASK_EXECUTION['as_completed']:
                    asyncio.run(
                        run.get_many_async_as_completed([TEST_URL] * RUN_FREQ, eager)
                    )
                buffer
                if TASK_EXECUTION['gather']:
                    asyncio.run(
                        run.get_many_async_gather([TEST_URL] * RUN_FREQ, eager)
                    )
                buffer
                if TASK_EXECUTION['task_group']:
                    asyncio.run(
                        run.get_many_async_taskgroup([TEST_URL] * RUN_FREQ, eager)
                    )

# RUN
if __name__ == "__main__":
    main()
