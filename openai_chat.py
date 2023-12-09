from openai import AsyncOpenAI
import aiofiles
import chainlit as cl


client = AsyncOpenAI(
    api_key="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")


settings = {
    "model": "gpt-4-vision-preview",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "Tu es LegalGPT un assistant juridique viruel Algérien, un virtuose des textes juridiques en arabe et en français de 1962 à 2023"}],
    )


@cl.on_message
async def on_message(msg: cl.Message):
    if not msg.elements:
        await cl.Message(content="No file attached").send()
        return

    # Processing images exclusively
    images = [file for file in msg.elements if "image" in file.mime]

    # Accessing the bytes of a specific image
    image_bytes = images[0].content

    await cl.Message(content=f"Received {len(images)} image(s)").send()


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()

    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
