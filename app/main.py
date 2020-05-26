from aiohttp import web
import aiohttp_jinja2
import jinja2

from utils import transform, select_db, custom_encode

routes = web.RouteTableDef()                                           

@routes.view('/')
class mainView(web.View):
    async def get(self):
        response = aiohttp_jinja2.render_template(  'index.html',
                                                    self.request,
                                                    None)
        return response

    async def post(self):
        data = await self.request.post()
        if data['custom_input'] !='':
            short_link = await custom_encode(data)
        else:
            short_link = await transform(data['url_input'])
        context = {'short_link':short_link if short_link else 'This url has already taken'}
        response = aiohttp_jinja2.render_template(  'response.html',
                                                    self.request,
                                                    context)
        return response

@routes.view('/red/{link}')
class redirectView(web.View):
    async def get(self):
        short_url = 'http://short/red/'+self.request.match_info['link']
        urls = await select_db(short_url, 'short_url', '%')
        if urls:
            raise web.HTTPFound(urls[0])
        else:
            context = {'url':self.request.match_info['link']}
            response = aiohttp_jinja2.render_template(  'redirect_error.html',
                                                        self.request,
                                                        context)
            return response

if __name__ == "__main__":
    app = web.Application()
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader('templates/')
    )
    app.add_routes(routes)
    web.run_app(app)