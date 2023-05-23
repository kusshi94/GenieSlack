import slack_sdk
import slack_sdk.errors


def reply_to_message(
    client: slack_sdk.web.client.WebClient, 
    channel_id: str, 
    message_ts: str, 
    message_content: str
):
    """メッセージのスレッドで返信する

    Args:
        client (slack_sdk.web.client.WebClient): slack_sdkのclient
        channel_id (str): _description_
        message_ts (str): _description_
        message_content (str): _description_
    """
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            thread_ts=message_ts,
            text=message_content,
        )

        print(result)
    except slack_sdk.errors.SlackApiError as e:
        print(f"Error: {e}")
