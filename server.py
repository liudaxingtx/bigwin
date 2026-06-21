#!/usr/bin/env python3
"""BigWin Monopoly — Multiplayer WebSocket Server"""
import asyncio, json, random, time, uuid
from websockets.asyncio.server import serve

# ─── Game Data ───────────────────────────────────────────────────
COLORS = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

SPACES = [
    {'name': '起点', 'type': 'go'},
    {'name': '地中海大道', 'type': 'property', 'price': 60, 'rent': [2, 10, 30, 90, 160, 250], 'color': '#8B4513', 'houseCost': 50},
    {'name': '机会', 'type': 'chance'},
    {'name': '波罗的海大道', 'type': 'property', 'price': 60, 'rent': [4, 20, 60, 180, 320, 450], 'color': '#8B4513', 'houseCost': 50},
    {'name': '所得税', 'type': 'tax', 'amount': 200},
    {'name': '铁路', 'type': 'railroad', 'price': 200},
    {'name': '东方大道', 'type': 'property', 'price': 100, 'rent': [6, 30, 90, 270, 400, 550], 'color': '#87CEEB', 'houseCost': 50},
    {'name': '机会', 'type': 'chance'},
    {'name': '佛蒙特大道', 'type': 'property', 'price': 100, 'rent': [6, 30, 90, 270, 400, 550], 'color': '#87CEEB', 'houseCost': 50},
    {'name': '康涅狄格大道', 'type': 'property', 'price': 120, 'rent': [8, 40, 100, 300, 450, 600], 'color': '#87CEEB', 'houseCost': 50},
    {'name': '监狱', 'type': 'jail'},
    {'name': '圣查尔斯广场', 'type': 'property', 'price': 140, 'rent': [10, 50, 150, 450, 625, 750], 'color': '#E91E63', 'houseCost': 100},
    {'name': '电力公司', 'type': 'utility', 'price': 150},
    {'name': '州立大道', 'type': 'property', 'price': 140, 'rent': [10, 50, 150, 450, 625, 750], 'color': '#E91E63', 'houseCost': 100},
    {'name': '弗吉尼亚大道', 'type': 'property', 'price': 160, 'rent': [12, 60, 180, 500, 700, 900], 'color': '#E91E63', 'houseCost': 100},
    {'name': '铁路', 'type': 'railroad', 'price': 200},
    {'name': '圣詹姆斯广场', 'type': 'property', 'price': 180, 'rent': [14, 70, 200, 550, 750, 950], 'color': '#FF9800', 'houseCost': 100},
    {'name': '命运', 'type': 'community'},
    {'name': '田纳西大道', 'type': 'property', 'price': 180, 'rent': [14, 70, 200, 550, 750, 950], 'color': '#FF9800', 'houseCost': 100},
    {'name': '纽约大道', 'type': 'property', 'price': 200, 'rent': [16, 80, 220, 600, 800, 1000], 'color': '#FF9800', 'houseCost': 100},
    {'name': '免费停车', 'type': 'free'},
    {'name': '肯塔基大道', 'type': 'property', 'price': 220, 'rent': [18, 90, 250, 700, 875, 1050], 'color': '#E53935', 'houseCost': 150},
    {'name': '机会', 'type': 'chance'},
    {'name': '印第安纳大道', 'type': 'property', 'price': 220, 'rent': [18, 90, 250, 700, 875, 1050], 'color': '#E53935', 'houseCost': 150},
    {'name': '伊利诺伊大道', 'type': 'property', 'price': 240, 'rent': [20, 100, 300, 750, 925, 1100], 'color': '#E53935', 'houseCost': 150},
    {'name': '铁路', 'type': 'railroad', 'price': 200},
    {'name': '大西洋大道', 'type': 'property', 'price': 260, 'rent': [22, 110, 330, 800, 975, 1150], 'color': '#FFEB3B', 'houseCost': 150},
    {'name': '文特诺大道', 'type': 'property', 'price': 260, 'rent': [22, 110, 330, 800, 975, 1150], 'color': '#FFEB3B', 'houseCost': 150},
    {'name': '自来水厂', 'type': 'utility', 'price': 150},
    {'name': '马文花园', 'type': 'property', 'price': 280, 'rent': [24, 120, 360, 850, 1025, 1200], 'color': '#FFEB3B', 'houseCost': 150},
    {'name': '进监狱', 'type': 'gotojail'},
    {'name': '太平洋大道', 'type': 'property', 'price': 300, 'rent': [26, 130, 390, 900, 1100, 1275], 'color': '#2E7D32', 'houseCost': 200},
    {'name': '北卡罗来纳大道', 'type': 'property', 'price': 300, 'rent': [26, 130, 390, 900, 1100, 1275], 'color': '#2E7D32', 'houseCost': 200},
    {'name': '命运', 'type': 'community'},
    {'name': '宾夕法尼亚大道', 'type': 'property', 'price': 320, 'rent': [28, 150, 450, 1000, 1200, 1400], 'color': '#2E7D32', 'houseCost': 200},
    {'name': '铁路', 'type': 'railroad', 'price': 200},
    {'name': '机会', 'type': 'chance'},
    {'name': '公园广场', 'type': 'property', 'price': 350, 'rent': [35, 175, 500, 1100, 1300, 1500], 'color': '#1A237E', 'houseCost': 200},
    {'name': '奢侈税', 'type': 'tax', 'amount': 100},
    {'name': '海滨大道', 'type': 'property', 'price': 400, 'rent': [50, 200, 600, 1400, 1700, 2000], 'color': '#1A237E', 'houseCost': 200},
]

CHANCE_CARDS = [
    {'text': '银行发放红利 $150', 'act': 'add_money', 'amount': 150},
    {'text': '前进到起点', 'act': 'move_to', 'pos': 0},
    {'text': '后退 3 格', 'act': 'move_back', 'steps': 3},
    {'text': '缴纳税款 $75', 'act': 'add_money', 'amount': -75},
    {'text': '前进到免费停车', 'act': 'move_to', 'pos': 20},
    {'text': '银行利息 $50', 'act': 'add_money', 'amount': 50},
    {'text': '前进到伊利诺伊大道', 'act': 'move_to', 'pos': 24},
    {'text': '维修费用 $100', 'act': 'add_money', 'amount': -100},
    {'text': '前进到圣查尔斯广场', 'act': 'move_to', 'pos': 11},
    {'text': '生日快乐！每人给你 $10', 'act': 'birthday'},
    {'text': '获得 $100', 'act': 'add_money', 'amount': 100},
    {'text': '进监狱！', 'act': 'goto_jail'},
    {'text': '获得 $200', 'act': 'add_money', 'amount': 200},
    {'text': '医疗费用 $50', 'act': 'add_money', 'amount': -50},
    {'text': '前进到海滨大道', 'act': 'move_to', 'pos': 39},
    {'text': '银行失误，获得 $200', 'act': 'add_money', 'amount': 200},
]

COMMUNITY_CARDS = [
    {'text': '银行错误，获得 $200', 'act': 'add_money', 'amount': 200},
    {'text': '医生费用 $50', 'act': 'add_money', 'amount': -50},
    {'text': '出售股票获得 $100', 'act': 'add_money', 'amount': 100},
    {'text': '人寿保险到期，获得 $100', 'act': 'add_money', 'amount': 100},
    {'text': '医院费用 $100', 'act': 'add_money', 'amount': -100},
    {'text': '学校费用 $50', 'act': 'add_money', 'amount': -50},
    {'text': '咨询服务费 $25', 'act': 'add_money', 'amount': 25},
    {'text': '维修评估，每栋$40/酒店$115', 'act': 'repair'},
    {'text': '选美比赛获奖 $10', 'act': 'add_money', 'amount': 10},
    {'text': '继承遗产 $100', 'act': 'add_money', 'amount': 100},
    {'text': '出售旧货 $50', 'act': 'add_money', 'amount': 50},
    {'text': '获得 $25', 'act': 'add_money', 'amount': 25},
    {'text': '进监狱！', 'act': 'goto_jail'},
    {'text': '前进到起点', 'act': 'move_to', 'pos': 0},
    {'text': '获得 $100', 'act': 'add_money', 'amount': 100},
    {'text': '生日礼物 $10', 'act': 'add_money', 'amount': 10},
]

# ─── Room & Game State ───────────────────────────────────────────
rooms = {}  # room_code → room_state

def new_room():
    """Create a new game room."""
    code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
    while code in rooms:
        code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
    rooms[code] = {
        'code': code,
        'players': [],        # list of player_info dicts
        'connections': {},    # player_id → websocket
        'state': None,        # game state (set when game starts)
        'phase': 'lobby',     # lobby | playing | gameover
        'created_at': time.time(),
    }
    return rooms[code]

def init_game(room):
    """Initialize game state for a room."""
    ps = room['players']
    n = len(ps)
    state = {
        'players': [],
        'currentPlayer': 0,
        'gamePhase': 'roll',
        'diceValues': [0, 0],
        'doublesCount': 0,
        'spaces': [{'owner': None, 'houses': 0} for _ in range(40)],
        'chanceIdx': 0, 'communityIdx': 0,
        'chanceDeck': random.sample(CHANCE_CARDS, len(CHANCE_CARDS)),
        'communityDeck': random.sample(COMMUNITY_CARDS, len(COMMUNITY_CARDS)),
        'auctionState': None,
        'log': [],
    }
    for i, p in enumerate(ps):
        state['players'].append({
            'id': i, 'name': p['name'], 'color': p['color'],
            'money': 1500, 'position': 0, 'properties': [],
            'inJail': False, 'jailTurns': 0, 'bankrupt': False,
        })
    room['state'] = state
    room['phase'] = 'playing'
    add_log(state, '欢迎来到大富翁！')

def add_log(state, msg):
    state['log'].insert(0, msg)
    if len(state['log']) > 30:
        state['log'] = state['log'][:30]

def get_state_for_player(room, player_id):
    """Return game state + player-specific info."""
    state = room['state']
    if not state:
        return {'phase': 'lobby', 'players': room['players']}
    ps = [{'id': p['id'], 'name': p['name'], 'color': p['color'],
           'money': p['money'], 'position': p['position'],
           'properties': p['properties'], 'inJail': p['inJail'],
           'jailTurns': p['jailTurns'], 'bankrupt': p['bankrupt']}
          for p in state['players']]
    return {
        'phase': 'playing',
        'roomCode': room['code'],
        'players': ps,
        'currentPlayer': state['currentPlayer'],
        'gamePhase': state['gamePhase'],
        'diceValues': state['diceValues'],
        'spaces': state['spaces'],
        'auctionState': state['auctionState'],
        'log': state['log'],
        'myId': player_id,
        'hint': compute_hint(state),
        'availableActions': compute_actions(state, player_id),
    }

def compute_hint(state):
    p = state['players'][state['currentPlayer']]
    phase = state['gamePhase']
    if phase == 'roll':
        return f"轮到 {p['name']}"
    elif phase == 'buy':
        s = SPACES[p['position']]
        return f"购买 {s['name']} (${s['price']})？"
    elif phase == 'result':
        return f"{p['name']} 回合结束"
    elif phase == 'build':
        return f"{p['name']} 可以建房"
    elif phase == 'gameover':
        alive = [pl for pl in state['players'] if not pl['bankrupt']]
        return f"{alive[0]['name']} 获胜！" if alive else ''
    return ''

def compute_actions(state, player_id):
    """Return list of actions available to this player."""
    if state['gamePhase'] == 'gameover':
        return ['restart']
    if player_id != state['currentPlayer']:
        return []
    p = state['players'][player_id]
    phase = state['gamePhase']
    actions = []
    if phase == 'roll':
        if p['inJail'] and p['jailTurns'] < 3 and p['money'] >= 50:
            actions.append('bail')
        actions.append('roll')
    elif phase == 'buy':
        s = SPACES[p['position']]
        if s.get('owner') is None and p['money'] >= s.get('price', 0):
            actions.append('buy')
        actions.append('pass')
    elif phase == 'build':
        actions.append('build')
        actions.append('pass')
    elif phase == 'result':
        actions.append('continue')
    return actions

# ─── Game Logic ──────────────────────────────────────────────────
def roll_dice(state):
    p = state['players'][state['currentPlayer']]
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    state['diceValues'] = [d1, d2]
    total = d1 + d2
    add_log(state, f"{p['name']} 掷出 {d1}+{d2}={total}")

    # Jail logic
    if p['inJail']:
        if p['jailTurns'] >= 3:
            p['money'] -= 50
            p['inJail'] = False
            p['jailTurns'] = 0
            add_log(state, f"{p['name']} 缴纳 $50 保释金（强制出狱）")
            check_bankrupt(state, p)
        elif d1 == d2:
            p['inJail'] = False
            p['jailTurns'] = 0
            add_log(state, f"{p['name']} 掷出对子，出狱！")
        else:
            p['jailTurns'] += 1
            add_log(state, f"{p['name']} 仍在狱中（第{p['jailTurns']}次）")
            state['gamePhase'] = 'result'
            return

    # Doubles tracking
    if d1 == d2:
        state['doublesCount'] += 1
        if state['doublesCount'] >= 3:
            send_to_jail(state, p)
            add_log(state, f"{p['name']} 连续三对，进监狱！")
            state['gamePhase'] = 'result'
            return
    else:
        state['doublesCount'] = 0

    # Move player
    start = p['position']
    end = (start + total) % 40
    p['position'] = end
    if start + total >= 40:
        p['money'] += 200
        add_log(state, f"{p['name']} 经过起点 +$200")

    land_on_space(state, p)

def land_on_space(state, p):
    s = SPACES[p['position']]
    t = s['type']
    if t in ('property', 'railroad', 'utility'):
        owner = state['spaces'][p['position']]['owner']
        if owner is None:
            state['gamePhase'] = 'buy'
        elif owner != p['id']:
            pay_rent(state, p, s)
            check_bankrupt(state, p)
            state['gamePhase'] = 'result'
        elif t == 'property':
            cg = [i for i, sp in enumerate(SPACES) if sp.get('color') == s.get('color') and sp.get('type') == 'property']
            owns_all = all(state['spaces'][i]['owner'] == p['id'] for i in cg)
            hs = state['spaces'][p['position']]['houses']
            min_h = min(state['spaces'][i]['houses'] for i in cg) if cg else 0
            can_build = owns_all and hs < 5 and p['money'] >= s.get('houseCost', 50) and hs <= min_h
            state['gamePhase'] = 'build' if can_build else 'result'
        else:
            state['gamePhase'] = 'result'
    elif t == 'tax':
        p['money'] -= s['amount']
        add_log(state, f"{p['name']} 缴税 ${s['amount']}")
        check_bankrupt(state, p)
        state['gamePhase'] = 'result'
    elif t == 'chance':
        draw_card(state, p, 'chance')
    elif t == 'community':
        draw_card(state, p, 'community')
    elif t == 'gotojail':
        send_to_jail(state, p)
        add_log(state, f"{p['name']} 被送进监狱！")
        state['gamePhase'] = 'result'
    else:
        state['gamePhase'] = 'result'

def pay_rent(state, p, s):
    owner_id = state['spaces'][p['position']]['owner']
    owner = state['players'][owner_id]
    if s['type'] == 'railroad':
        n = sum(1 for i, sp in enumerate(SPACES) if sp.get('type') == 'railroad' and state['spaces'][i]['owner'] == owner_id)
        rent = [25, 50, 100, 200][n - 1]
    elif s['type'] == 'utility':
        n = sum(1 for i, sp in enumerate(SPACES) if sp.get('type') == 'utility' and state['spaces'][i]['owner'] == owner_id)
        total = state['diceValues'][0] + state['diceValues'][1]
        rent = total * 10 if n == 2 else total * 4
    else:
        rent = s['rent'][min(state['spaces'][p['position']]['houses'], 5)]
    p['money'] -= rent
    owner['money'] += rent
    add_log(state, f"{p['name']} 支付 ${rent} 租金给 {owner['name']}")

def buy_property(state):
    p = state['players'][state['currentPlayer']]
    s = SPACES[p['position']]
    if state['spaces'][p['position']]['owner'] is not None or p['money'] < s['price']:
        return
    p['money'] -= s['price']
    state['spaces'][p['position']]['owner'] = p['id']
    p['properties'].append(p['position'])
    add_log(state, f"{p['name']} 购买了 {s['name']} (${s['price']})")
    state['gamePhase'] = 'result'

def pass_turn(state):
    p = state['players'][state['currentPlayer']]
    s = SPACES[p['position']]
    if s['type'] in ('property', 'railroad', 'utility') and state['spaces'][p['position']]['owner'] is None:
        start_auction(state, s)
    else:
        state['gamePhase'] = 'result'

def build_house(state):
    p = state['players'][state['currentPlayer']]
    pos = p['position']
    s = SPACES[pos]
    if s['type'] != 'property' or state['spaces'][pos]['owner'] != p['id']:
        return
    cg = [i for i, sp in enumerate(SPACES) if sp.get('color') == s.get('color') and sp.get('type') == 'property']
    if not all(state['spaces'][i]['owner'] == p['id'] for i in cg):
        return
    hs = state['spaces'][pos]['houses']
    if hs >= 5:
        return
    cost = s.get('houseCost', 50)
    if p['money'] < cost:
        return
    min_h = min(state['spaces'][i]['houses'] for i in cg)
    if hs > min_h:
        return
    p['money'] -= cost
    state['spaces'][pos]['houses'] = hs + 1
    add_log(state, f"{p['name']} 建造{'酒店' if hs + 1 == 5 else '房屋'} (${cost})")
    state['gamePhase'] = 'result'

def continue_turn(state):
    if state['gamePhase'] == 'gameover':
        return
    if state['doublesCount'] > 0 and not state['players'][state['currentPlayer']]['inJail']:
        add_log(state, f"{state['players'][state['currentPlayer']]['name']} 掷出对子，再掷一次！")
        state['gamePhase'] = 'roll'
    else:
        advance_player(state)

def advance_player(state):
    if state['gamePhase'] == 'gameover':
        return
    state['doublesCount'] = 0
    n = len(state['players'])
    for _ in range(n):
        state['currentPlayer'] = (state['currentPlayer'] + 1) % n
        if not state['players'][state['currentPlayer']]['bankrupt']:
            break
    if state['players'][state['currentPlayer']]['bankrupt']:
        return
    state['gamePhase'] = 'roll'

def pay_bail(state):
    p = state['players'][state['currentPlayer']]
    if not p['inJail'] or p['money'] < 50 or p['jailTurns'] >= 3:
        return
    p['money'] -= 50
    p['inJail'] = False
    p['jailTurns'] = 0
    add_log(state, f"{p['name']} 缴纳 $50 保释金，出狱！")
    check_bankrupt(state, p)

def send_to_jail(state, p):
    p['inJail'] = True
    p['position'] = 10
    p['jailTurns'] = 0

def check_bankrupt(state, p):
    if p['money'] < 0 and not p['bankrupt']:
        p['bankrupt'] = True
        add_log(state, f"{p['name']} 破产！💸")
        for i in range(40):
            if state['spaces'][i]['owner'] == p['id']:
                state['spaces'][i]['owner'] = None
                state['spaces'][i]['houses'] = 0
        p['properties'] = []
        alive = [pl for pl in state['players'] if not pl['bankrupt']]
        if len(alive) == 1:
            state['gamePhase'] = 'gameover'
            add_log(state, f"🏆 {alive[0]['name']} 获胜！")

def draw_card(state, p, card_type):
    deck = state['chanceDeck'] if card_type == 'chance' else state['communityDeck']
    idx = state['chanceIdx'] if card_type == 'chance' else state['communityIdx']
    card = deck[idx % len(deck)]
    if card_type == 'chance':
        state['chanceIdx'] += 1
    else:
        state['communityIdx'] += 1

    add_log(state, f"{p['name']} [{'机会' if card_type == 'chance' else '命运'}] {card['text']}")

    act = card['act']
    if act == 'add_money':
        p['money'] += card['amount']
        add_log(state, f"  {'+' if card['amount']>0 else ''}${card['amount']}")
    elif act == 'move_to':
        target = card['pos']
        start = p['position']
        if target <= start:
            p['money'] += 200
            add_log(state, f"  经过起点 +$200")
        p['position'] = target
        land_on_space(state, p)
        return
    elif act == 'move_back':
        steps = card['steps']
        p['position'] = (p['position'] - steps + 40) % 40
        land_on_space(state, p)
        return
    elif act == 'birthday':
        total = 0
        for pl in state['players']:
            if pl['id'] != p['id'] and not pl['bankrupt']:
                pl['money'] -= 10
                total += 10
        p['money'] += total
        add_log(state, f"  收到 ${total}")
    elif act == 'repair':
        cost = 0
        for i in range(40):
            if state['spaces'][i]['owner'] == p['id']:
                hs = state['spaces'][i]['houses']
                cost += hs * (115 if hs == 5 else 40)
        p['money'] -= cost
        add_log(state, f"  维修 -${cost}")
    elif act == 'goto_jail':
        send_to_jail(state, p)

    check_bankrupt(state, p)
    if state['gamePhase'] != 'gameover':
        state['gamePhase'] = 'result'

# ─── Auction ─────────────────────────────────────────────────────
def start_auction(state, space):
    alive = [i for i, pl in enumerate(state['players']) if not pl['bankrupt']]
    if len(alive) <= 1:
        state['gamePhase'] = 'result'
        return
    order = []
    idx = state['currentPlayer']
    for _ in range(len(alive)):
        while state['players'][idx]['bankrupt']:
            idx = (idx + 1) % len(state['players'])
        if idx not in order:
            order.append(idx)
        idx = (idx + 1) % len(state['players'])
    state['auctionState'] = {
        'space': {'name': space['name'], 'price': space['price'], 'pos': SPACES.index(space)},
        'currentBid': 0,
        'highestBidder': None,
        'bidderOrder': order,
        'currentBidderIdx': 0,
        'passed': [],
        'totalBidders': len(order),
    }

def place_bid(state, amount):
    a = state['auctionState']
    if not a:
        return
    bidder = state['players'][a['bidderOrder'][a['currentBidderIdx']]]
    if amount <= a['currentBid']:
        return
    # Cap: don't bid more than richest opponent + 1
    max_others = max((state['players'][i]['money'] for i in a['bidderOrder'] if i != bidder['id'] and not state['players'][i]['bankrupt']), default=0)
    if amount > max_others + 1:
        amount = max_others + 1
    if amount > bidder['money']:
        # Can't afford — auto pass
        pass_bid(state)
        return
    a['currentBid'] = amount
    a['highestBidder'] = bidder['id']
    add_log(state, f"{bidder['name']} 出价 ${amount}")
    next_bidder(state)

def pass_bid(state):
    a = state['auctionState']
    if not a:
        return
    bidder = state['players'][a['bidderOrder'][a['currentBidderIdx']]]
    a['passed'].append(bidder['id'])
    add_log(state, f"{bidder['name']} 放弃竞拍")
    next_bidder(state)

def next_bidder(state):
    a = state['auctionState']
    if not a:
        return
    n = a['totalBidders']
    for _ in range(n):
        a['currentBidderIdx'] = (a['currentBidderIdx'] + 1) % n
        nxt = a['bidderOrder'][a['currentBidderIdx']]
        if nxt not in a['passed']:
            break
    # Check if only one bidder left or all passed
    if len(a['passed']) >= n - 1 or (a['highestBidder'] is not None and all(
        state['players'][i]['money'] <= a['currentBid'] or i in a['passed']
        for i in a['bidderOrder'] if i != a['highestBidder']
    )):
        finish_auction(state)

def finish_auction(state):
    a = state['auctionState']
    if not a:
        return
    if a['highestBidder'] is not None:
        winner = state['players'][a['highestBidder']]
        pos = a['space']['pos']
        state['spaces'][pos]['owner'] = winner['id']
        winner['properties'].append(pos)
        winner['money'] -= a['currentBid']
        add_log(state, f"🏆 {winner['name']} 以 ${a['currentBid']} 赢得 {a['space']['name']}！")
    state['auctionState'] = None
    state['gamePhase'] = 'result'

# ─── WebSocket Handler ───────────────────────────────────────────
async def handler(ws):
    player_id = None
    room = None
    try:
        async for raw in ws:
            msg = json.loads(raw)
            action = msg.get('action')

            if action == 'create_room':
                room = new_room()
                await ws.send(json.dumps({'type': 'room_created', 'code': room['code']}))

            elif action == 'join_room':
                code = msg['code'].upper()
                name = msg.get('name', '玩家')
                color_idx = msg.get('colorIdx', 0)
                if code not in rooms:
                    await ws.send(json.dumps({'type': 'error', 'msg': '房间不存在'}))
                    continue
                room = rooms[code]
                if room['phase'] != 'lobby':
                    await ws.send(json.dumps({'type': 'error', 'msg': '游戏已开始'}))
                    continue
                if len(room['players']) >= 6:
                    await ws.send(json.dumps({'type': 'error', 'msg': '房间已满'}))
                    continue
                player_id = len(room['players'])
                room['players'].append({
                    'id': player_id, 'name': name,
                    'color': COLORS[color_idx % len(COLORS)],
                })
                room['connections'][player_id] = ws
                await ws.send(json.dumps({'type': 'joined', 'playerId': player_id, 'code': code}))
                # Broadcast player list to all
                await broadcast_room(room)

            elif action == 'start_game':
                if not room or room['phase'] != 'lobby':
                    continue
                if len(room['players']) < 2:
                    await ws.send(json.dumps({'type': 'error', 'msg': '至少需要2名玩家'}))
                    continue
                init_game(room)
                await broadcast_state(room)

            elif action == 'game_action':
                if not room or room['phase'] != 'playing':
                    continue
                act = msg.get('act')
                state = room['state']
                if player_id != state['currentPlayer']:
                    await ws.send(json.dumps({'type': 'error', 'msg': '不是你的回合'}))
                    continue
                if act == 'roll':
                    roll_dice(state)
                elif act == 'buy':
                    buy_property(state)
                elif act == 'pass':
                    pass_turn(state)
                elif act == 'build':
                    build_house(state)
                elif act == 'continue':
                    continue_turn(state)
                elif act == 'bail':
                    pay_bail(state)
                elif act == 'bid':
                    place_bid(state, msg.get('amount', 0))
                elif act == 'pass_bid':
                    pass_bid(state)
                await broadcast_state(room)

            elif action == 'restart':
                if room:
                    room['phase'] = 'lobby'
                    room['state'] = None
                    await broadcast_room(room)

            elif action == 'leave':
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if room and player_id is not None:
            # Remove player
            if player_id in room['connections']:
                del room['connections'][player_id]
            room['players'] = [p for p in room['players'] if p['id'] != player_id]
            if not room['players']:
                del rooms[room['code']]
            else:
                await broadcast_room(room)

async def broadcast_room(room):
    """Send lobby state to all connected players."""
    data = {
        'type': 'lobby_update',
        'code': room['code'],
        'phase': room['phase'],
        'players': room['players'],
    }
    for ws in list(room['connections'].values()):
        try:
            await ws.send(json.dumps(data))
        except:
            pass

async def broadcast_state(room):
    """Send game state to all connected players."""
    for pid, ws in list(room['connections'].items()):
        try:
            state_data = get_state_for_player(room, pid)
            state_data['type'] = 'state_update'
            await ws.send(json.dumps(state_data))
        except:
            pass

async def main():
    print("🎩 BigWin Multiplayer Server starting on ws://0.0.0.0:8765")
    async with serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
