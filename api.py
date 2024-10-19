import requests

# ENDPOINT = 'https://raccoon-moving-stud.ngrok-free.app'
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
    
    res = requests.post(f'{ENDPOINT}/exchange_reward', json=body)

    return "購買成功" if res.status_code == 200 else "點數不足"

def generate_icon(user_id, prompt):
    body = {
        'line_id': user_id,
        'prompt': prompt
    }

    res = requests.post(f'{ENDPOINT}/api/v1/icons', json=body)
    icon = res.json()

    return icon['icon'] if res.status_code == 200 else None

def send_review_result(data, result):
    body = {
        'author_id': data['author_id'],
        'pr_url': data['pr_url'],
        'reviewer_id': data['reviewer_id'],
        'result': result
    }

    res = requests.post(f'{ENDPOINT}/review', json=body)

    return "回覆成功" if res.status_code == 200 else "回覆失敗"