from linebot.models import (
    CarouselTemplate,
    CarouselColumn,
    TemplateSendMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction,
    TextSendMessage,
    FlexSendMessage,
)
import json


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
            ],
        )
        for reward in rewards
    ]

    return TemplateSendMessage(
        alt_text="kdfk", template=CarouselTemplate(columns=column)
    )


def get_review_message(review):
    github_id = review["author_id"]
    summary = json.loads(review["summary"])
    template = review_template.copy()
    template["body"] = summary['flexMessage']["contents"]["body"]
    
    ## TODO: add pr_url
    
    # Format github_id
    template["header"]["contents"][0]["text"] = \
        template["header"]["contents"][0]["text"].format(github_id)
    template["header"]["contents"][1]["text"] = \
        template["header"]["contents"][1]["text"].format(github_id, github_id)

    # Format commit count
    template["header"]["contents"][3]["contents"][0]["contents"][0]["text"] = \
        template["header"]["contents"][3]["contents"][0]["contents"][0]["text"].format(review["commit_count"])

    # Format additions, deletions, total
    additions, deletions, total = review["additions"], review["deletions"], review["total"]
    template["header"]["contents"][3]["contents"][1]["contents"][0]["text"] = \
        template["header"]["contents"][3]["contents"][1]["contents"][0]["text"].format(additions)
    template["header"]["contents"][3]["contents"][1]["contents"][1]["text"] = \
        template["header"]["contents"][3]["contents"][1]["contents"][1]["text"].format(deletions)
    template["header"]["contents"][3]["contents"][1]["contents"][2]["text"] = \
        template["header"]["contents"][3]["contents"][1]["contents"][2]["text"].format(total)

    flex_message = FlexSendMessage(alt_text="Review", contents=template)

    quick_reply = TextSendMessage("Please rate your employee's work!",
        quick_reply=QuickReply(
        items=[
            QuickReplyButton(
                action={
                    "type": "message",
                    "label": f"{point}分",
                    "text": f"{point}分",
                }
            )
            for point in range(1, 6)
        ]
    ))


    return [flex_message, quick_reply]


review_template = {
    "type": "bubble",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "New PR merged for {}!",
                "weight": "bold",
                "wrap": True,
                "color": "#ffffff",
            },
            {
                "type": "text",
                "text": "Below is the summary of {}'s work, please give {} a rating to prove his contribution!",
                "wrap": True,
                "color": "#ffffff",
            },
            {"type": "separator", "margin": "10px", "color": "#000000"},
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "commits: {}",
                                "color": "#ffffff",
                                "margin": "md",
                            }
                        ],
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "additions: {}",
                                "color": "#ffffff",
                                "margin": "md",
                            },
                            {
                                "type": "text",
                                "text": "deletions: {}",
                                "color": "#ffffff",
                            },
                            {"type": "text", "text": "total: {}", "color": "#ffffff"},
                        ],
                    },
                ],
            },
        ],
        "backgroundColor": "#E03031",
    },
    "styles": {"body": {"backgroundColor": "#f5f5f2"}},
}

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
                    "data": "nothing",
                }
            ]
        )
        for reward in rewards
    ]

    return TemplateSendMessage(alt_text='yourPrizes', template=CarouselTemplate(columns=column))