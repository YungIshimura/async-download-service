import argparse
import asyncio
import time


async def create_archive_process(directory):
    process = await asyncio.create_subprocess_exec(
        'zip', '-r9', '-', '.',
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=directory,
        env={'PYTHONUNBUFFERED': '1'}
    )
    
    return process


async def check_timeout(namespace, start_time, logger):
    if time.time() - start_time > namespace.timeout:
        if namespace.logging:
            logger.error('Download was interrupted')
        raise asyncio.CancelledError


def create_argparse_namespace():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        default=10,
        help='Таймаут для обрыва соединения'
    )
    parser.add_argument(
        '-l',
        '--logging',
        action='store_true',
        help='Включить логирование'
    )
    parser.add_argument(
        '-p',
        '--path',
        type=str,
        default='test_photos',
        help='Путь до папки с фото'
    )

    namespace = parser.parse_args()

    return namespace
