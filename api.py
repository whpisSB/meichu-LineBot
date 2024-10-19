import requests

ENDPOINT = 'http://140.112.251.50:5000'

def get_user_points(user_id):
    res = requests.get(f'{ENDPOINT}/user_points', json={'line_id': user_id})
    points = res.json()
    return points if res.status_code == 200 else None

def get_user_reward(user_id):
    res = requests.get(f'{ENDPOINT}/user_rewards', json={'line_id': user_id})
    rewards = res.json()
    return rewards if res.status_code == 200 else None

def get_reward_data():
    res = requests.get(f'{ENDPOINT}/reward')
    reward = res.json()
    print("====\n",reward)
    return reward if res.status_code == 200 else None

def exchange_reward(user_id, reward_id):
    body = {
        'line_id': user_id,
        'reward_id': reward_id
    }
    
    res = requests.post(f'{ENDPOINT}/api/v1/rewards', json=body)

    return "購買成功" if res.status_code == 200 else "點數不足"

def generate_icon(user_id, prompt):
    body = {
        'line_id': user_id,
        'prompt': prompt
    }

    res = requests.post(f'{ENDPOINT}/api/v1/icons', json=body)
    icon = res.json()

    return icon['icon'] if res.status_code == 200 else None

def send_review_result(user_id, reviewer_id, result):
    body = {
        'line_id': user_id,
        'reviewer_id': reviewer_id,
        'result': result
    }

    res = requests.post(f'{ENDPOINT}/api/v1/review', json=body)

    return "回覆成功" if res.status_code == 200 else "回覆失敗"