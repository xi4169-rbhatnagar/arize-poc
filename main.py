from dotenv import load_dotenv

load_dotenv('envs/deepseek.env')

from servers.arize_server import app

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=7000)
