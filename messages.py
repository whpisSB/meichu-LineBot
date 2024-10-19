from linebot.models import CarouselTemplate, CarouselColumn, TemplateSendMessage, Action

def get_reward_message(rewards):
    column = [
        CarouselColumn(
            thumbnail_image_url=reward["thumbnail_image"],
            title=reward["title"],
            text=reward["description"],
            actions=[
                {
                    "type": "postback",
                    "label": f"台積點 * {reward['points']}",
                    "data": reward['id'],
                }
            ]
        )
        for reward in rewards
    ]

    return TemplateSendMessage(alt_text='kdfk', template=CarouselTemplate(columns=column))