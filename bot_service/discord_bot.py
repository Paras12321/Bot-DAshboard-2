import discord
import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)


class DiscordBotHandler:
    def __init__(self):
        
        self._clients: dict[str, discord.Client] = {}

    async def _get_client(self, token: str) -> discord.Client:
        if token in self._clients:
            client = self._clients[token]
            if not client.is_closed():
                return client

        intents = discord.Intents.default()

        intents.message_content = True
        intents.members = True
        client = discord.Client(intents=intents)

        ready = asyncio.get_event_loop().create_future()

        @client.event
        async def on_ready():
            if not ready.done():
                ready.set_result(True)
                
        @client.event
        async def on_message(message):

            if message.author.bot:
                return

            try:

                import bot_service.db_access as db_access
            
                rules = db_access.get_auto_replies()

                for rule in rules:

                    if not rule["is_active"]:
                        continue

                    trigger = rule["trigger_keyword"].lower()

                    content = message.content.lower()

                    matched = False

                    if rule["match_type"] == "exact":
                        matched = content == trigger

                    elif rule["match_type"] == "contains":
                        matched = trigger in content

                    if matched:

                        await message.channel.send(
                            rule["response_text"]
                        )

            except Exception:
                logger.exception("Auto reply error")
        @client.event
        async def on_member_join(member):

            try:

                import bot_service.db_access as db_access

                rules = db_access.get_welcome_messages()

                for rule in rules:

                    if not rule["is_active"]:
                        continue

                    channel = member.guild.get_channel(
                    int(rule["channel_id"])
                    )

                    if not channel:
                        continue

                    msg = rule["message_template"].replace(
                        "{user}",
                        member.name
                    )

                    await channel.send(msg)

            except Exception as e:
                logger.exception("Welcome message error")
       
        asyncio.create_task(client.start(token))

        try:
            await asyncio.wait_for(asyncio.shield(ready), timeout=30.0)
        except asyncio.TimeoutError:
            await client.close()
            raise RuntimeError("Discord client timed out during login")

        self._clients[token] = client
        return client

    async def send_message(self,token: str,channel_id: int,message: str,) -> dict:
        try:
            client = await self._get_client(token)

            channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)
            await channel.send(message)

            logger.info("Message sent to Discord channel #%s", channel.name)
            return {"status": "success", "detail": f"Message sent to channel {channel_id}"}

        except discord.LoginFailure:
            logger.error("Invalid Discord bot token")
            return {"status": "failed", "detail": "Invalid bot token"}
        except discord.NotFound:
            logger.error("Discord channel %s not found", channel_id)
            return {"status": "failed", "detail": f"Channel {channel_id} not found"}
        except discord.Forbidden:
            logger.error("Bot lacks permission to send to channel %s", channel_id)
            return {"status": "failed", "detail": "Bot lacks permission to send messages"}
        except Exception as e:
            logger.exception("Unexpected error sending Discord message")
            return {"status": "failed", "detail": str(e)}

    async def validate_token(self, token: str) -> bool:
        url = "https://discord.com/api/v10/users/@me"
        headers = {"Authorization": f"Bot {token}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    return resp.status == 200
        except Exception:
            logger.exception("Error validating Discord token")
            return False

    async def close_all(self):
        for client in self._clients.values():
            if not client.is_closed():
                await client.close()
        self._clients.clear()

discord_handler = DiscordBotHandler()