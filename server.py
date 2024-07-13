import os
import time

import aiofiles
from aiohttp import web
from aiologger import Logger

from utils import (check_timeout, create_archive_process,
                   create_argparse_namespace)


async def archive(request):
    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'attachment; filename="images.zip"'
    await response.prepare(request)

    archive_hash = request.match_info.get('archive_hash')
    directory = os.path.join(namespace.path, archive_hash)

    archive_process = await create_archive_process(directory)
    await archive_process.communicate()

    zip_path = os.path.join(os.getcwd(), 'images.zip')

    try:
        start_time = time.time()
        with open(zip_path, 'rb') as file:
            while chunk := file.read(8192):
                await check_timeout(namespace, start_time, archive_process, logger)
                await response.write(chunk)

                if namespace.logging:
                    logger.info('Sending archive chunk ...')
        await response.write_eof()
    except TimeoutError:
        if namespace.logging:
            logger.error('Download was interrupted')
    finally:
        os.remove(zip_path)

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    namespace = create_argparse_namespace()
    logger = Logger.with_default_handlers(name='write_chunk_logger')
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
