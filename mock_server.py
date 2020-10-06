import asyncio, json, datetime, time, threading
import websockets

async def run(websocket, path):
    greeting = f"Hello to the mock server!"
    await websocket.send(greeting)

    auth_msg = await websocket.recv()
    on_auth_message(auth_msg)
    await websocket.send("authenticated by the server")

    async def generate_signals():
        while True:
            await websocket.send(generate_a_signal())
            time.sleep(1)

    '''
    signal_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(signal_loop)
    signal_loop.run_until_complete(generate_signals())
    '''

    #th = threading.Thread(target=generate_signals)
    #th.start()

    #'''
    msg = await websocket.recv()
    on_subs_message(msg)

    while True:
        await websocket.send(generate_a_signal())
        time.sleep(1)
    #'''

    '''
    while True:
        msg = await websocket.recv()
        on_subs_message(msg)
    #'''

def on_auth_message(msg_strs):
    if not msg_strs:
        print('the auth message is not valid')
    print('on_auth_message', msg_strs)

def on_subs_message(msg_strs):
    if not msg_strs:
        print('the subs message is not valid')
    print('on_subs_message', msg_strs)

def generate_a_signal():
    signal = {
        "ev": "A"
    }
    epoch_s = datetime.datetime.now().timestamp()
    epoch_s_int = int(epoch_s)
    syms = ['AABA', 'AAPL', 'ABIO']
    signal['sym'] = syms[epoch_s_int % 3]
    signal['c'] = 100 + (int(epoch_s * 100) % 20)
    signal['v'] = 1
    signal['s'] = int(epoch_s_int)

    print('about to generate A signal', signal)
    return json.dumps([signal])

def on_message(msg_strs):
    if not msg_strs:
        print('the message is not valid')

    msg_js = json.loads(msg_strs)
    print('on_message', msg_js)

if __name__ == '__main__':
    start_server = websockets.serve(run, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
