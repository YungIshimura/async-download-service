from aiohttp import web
import aiofiles
import asyncio
import os
from aiologger import Logger
import time
import argparse


async def archive(request):
    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'attachment; filename="images.zip"'
    await response.prepare(request)

    archive_hash = request.match_info.get('archive_hash')
    directory = os.path.join(namespace.path, archive_hash)
    
    proc = await asyncio.create_subprocess_exec(
        'zip', '-r9', 'images.zip', directory,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=os.getcwd()
    )
    await proc.communicate()


    zip_path = os.path.join(os.getcwd(), 'images.zip')

    try:
        start_time = time.time()
        with open(zip_path, 'rb') as file:
            while chunk := file.read(8192):
                if time.time() - start_time > namespace.timeout:
                    await proc.kill()
                    if namespace.logging:
                        logger.error('Download was interrupted')
                    raise asyncio.CancelledError
                await response.write(chunk)
                if namespace.logging:
                    logger.info('Sending archive chunk ...')
        await response.write_eof()
    except TimeoutError:
        logger.error('Download was interrupted')
    finally:
        os.remove(zip_path)

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        default=10
    )
    parser.add_argument(
        '-l',
        '--logging',
        type=bool,
        default=False
    )
    parser.add_argument(
        '-p',
        '--path',
        type=str,
        default='test_photos/'
    )
    namespace = parser.parse_args()
    logger = Logger.with_default_handlers(name='write_chunk_logger')
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
