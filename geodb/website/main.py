import uvicorn
import geodb.website
port = 8000

app = geodb.website.Application()

uvicorn.run(app, host='0.0.0.0', port=port)
