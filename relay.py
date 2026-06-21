#!/usr/bin/env python3
"""BigWin Relay — 纯消息中转，不跑任何游戏逻辑"""
import asyncio, json
from websockets.asyncio.server import serve

rooms = {}  # room_code → {host: ws, guests: {id: ws}, next_id: int}

async def handler(ws):
    room = None
    my_id = None
    is_host = False
    
    try:
        async for raw in ws:
            msg = json.loads(raw)
            action = msg.get('action')
            
            if action == 'create_room':
                import random, string
                code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
                while code in rooms:
                    code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
                rooms[code] = {'host': ws, 'guests': {}, 'next_id': 1}
                room = rooms[code]
                is_host = True
                my_id = 0
                await ws.send(json.dumps({'type': 'room_created', 'code': code, 'id': 0}))
            
            elif action == 'join_room':
                code = msg['code'].upper()
                if code not in rooms:
                    await ws.send(json.dumps({'type': 'error', 'msg': '房间不存在'}))
                    continue
                room = rooms[code]
                my_id = room['next_id']
                room['next_id'] += 1
                room['guests'][my_id] = ws
                # Tell guest they joined
                await ws.send(json.dumps({'type': 'joined', 'code': code, 'id': my_id}))
                # Tell host about new guest
                try:
                    await room['host'].send(json.dumps({'type': 'guest_joined', 'id': my_id, 'name': msg.get('name', '玩家')}))
                except:
                    pass
            
            elif action == 'broadcast':
                # Host broadcasting state to all guests
                if not is_host or not room:
                    continue
                data = json.dumps(msg.get('data', {}))
                for gid, gws in list(room['guests'].items()):
                    try:
                        await gws.send(data)
                    except:
                        del room['guests'][gid]
            
            elif action == 'to_host':
                # Guest sending action to host
                if is_host or not room:
                    continue
                try:
                    await room['host'].send(json.dumps({
                        'type': 'guest_action',
                        'from': my_id,
                        'action': msg.get('gameAction', {}),
                    }))
                except:
                    pass
            
            elif action == 'player_list':
                # Host asking for relay to send player list to guests (used for lobby)
                if not is_host or not room:
                    continue
                for gid, gws in list(room['guests'].items()):
                    try:
                        await gws.send(json.dumps(msg.get('data', {})))
                    except:
                        del room['guests'][gid]
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if room:
            if is_host:
                # Host left — notify all guests and clean up room
                for gid, gws in list(room['guests'].items()):
                    try:
                        await gws.send(json.dumps({'type': 'host_left'}))
                    except:
                        pass
                # Find and delete the room
                for code, r in list(rooms.items()):
                    if r is room:
                        del rooms[code]
                        break
            elif my_id is not None:
                # Guest left — notify host
                if my_id in room['guests']:
                    del room['guests'][my_id]
                try:
                    await room['host'].send(json.dumps({'type': 'guest_left', 'id': my_id}))
                except:
                    pass

async def main():
    print("🔁 BigWin Relay — ws://0.0.0.0:8765")
    async with serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
