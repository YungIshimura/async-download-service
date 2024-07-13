import argparse
import asyncio
import os
import time


async def create_archive_process(directory):
    process = await asyncio.create_subprocess_exec(
        'zip', '-r9', 'images.zip', directory,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    return process


async def check_timeout(namespace, start_time, archive_process, logger):
    if time.time() - start_time > namespace.timeout:
        await archive_process.kill()
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
        default='test_photos/',
        help='Путь до папки с фото'
    )

    namespace = parser.parse_args()

    return namespace