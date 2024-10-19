from linebot.models import CarouselTemplate, CarouselColumn, TemplateSendMessage, QuickReply, QuickReplyButton, MessageAction

def get_reward_message(rewards):
    column = [
        CarouselColumn(
            thumbnail_image_url=reward["thumbnail_image"],
            title=reward["title"],
            text=reward["description"],
            actions=[
                {
                    "type": "postback",
                    "label": f"{reward['points']} 台積點",
                    "data": f"price {reward['reward_id']}",
                }
            ]
        )
        for reward in rewards
    ]

    return TemplateSendMessage(alt_text='kdfk', template=CarouselTemplate(columns=column))

def get_review_message(review):
    summary = review["summary"]
    

    
    quick_reply = QuickReply(
        items=[
            QuickReplyButton(
                action={
                    "type": "postback",
                    "label": f"{point}分",
                    "data": point,
                }
            )
            for point in range(1, 6)
        ]
    )

def get_user_reward_message(rewards):
    column = [
        CarouselColumn(
            thumbnail_image_url=reward["thumbnail_image"],
            title=reward["title"],
            text=reward["description"],
            actions=[
                {
                    "type": "postback",
                    "label": "查看",
                    "data": f"reward {reward['reward_id']}",
                }
            ]
        )
        for reward in rewards
    ]

    return TemplateSendMessage(alt_text='yourPrizes', template=CarouselTemplate(columns=column))