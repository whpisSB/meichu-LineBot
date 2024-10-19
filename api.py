import requests

ENDPOINT = 'http://140.112.251.50:5000'

def get_reward_data():
    res = requests.get(f'{ENDPOINT}/api/v1/rewards')
    reward = res.json()

    return reward['rewards'] if res.status_code == 200 else None

def exchange_reward(user_id, reward_id):
    body = {
        'user_id': user_id,
        'reward_id': reward_id
    }
    
    res = requests.post(f'{ENDPOINT}/api/v1/rewards', json=body)

    return "購買成功" if res.status_code == 200 else "點數不足"

def generate_icon(user_id, prompt):
    body = {
        'user_id': user_id,
        'prompt': prompt
    }

    res = requests.post(f'{ENDPOINT}/api/v1/icons', json=body)
    icon = res.json()

    return icon['icon'] if res.status_code == 200 else None

def send_review_result(user_id, reviewer_id, result):
    body = {
        'user_id': user_id,
        'reviewer_id': reviewer_id,
        'result': result
    }

    res = requests.post(f'{ENDPOINT}/api/v1/review', json=body)

    return "回覆成功" if res.status_code == 200 else "回覆失敗"