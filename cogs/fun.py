import io
from typing import Optional

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps
import discord
from discord.ext import commands

import aoi
from libs.minesweeper import SpoilerMinesweeper, MinesweeperError


def _font(size: int) -> PIL.ImageFont.ImageFont:
    return PIL.ImageFont.truetype(
        "assets/merged.ttf", size=size)


class Fun(commands.Cog):
    def __init__(self, bot: aoi.AoiBot):
        self.bot = bot
        self.simp_fp = open("assets/simp-template.png", "rb")
        self.simp_img = PIL.Image.open(self.simp_fp)
        self.font = _font(33)
        self.av_mask = PIL.Image.new("L", self.simp_img.size, 0)
        self.av_mask_draw = PIL.ImageDraw.Draw(self.av_mask)
        self.av_mask_draw.ellipse((430, 384, 430 + 83, 384 + 83), fill=255)

    @property
    def description(self) -> str:
        return "Fun! :D"

    @commands.command(brief="Makes a discord minesweeper game")
    async def minesweeper(self, ctx: aoi.AoiContext, height: Optional[int] = 10,
                          width: Optional[int] = 10, bombs: Optional[int] = 10, *,
                          flags=None):
        flags = await ctx.parse_flags(flags, {"raw": None, "no-spoiler": None, "interactive": None})
        fmt = "```%s```" if "raw" in flags else "%s"
        try:
            await ctx.send(fmt % SpoilerMinesweeper(height, width, bombs).discord_str("no-spoiler" not in flags))
        except MinesweeperError as e:
            await ctx.send_error(str(e))

    @commands.command(brief="Hehe simp")
    async def simp(self, ctx: aoi.AoiContext, member: discord.Member = None):
        await ctx.trigger_typing()
        member = member or ctx.author
        # bounds = (496, 145, 679, 178)
        bounds = (490, 145, 685, 178)
        target_width = bounds[2] - bounds[0]
        img_copy: PIL.Image = self.simp_img.copy().convert("RGBA")

        draw = PIL.ImageDraw.Draw(img_copy)
        # draw.rectangle(bounds, fill=(0, 200, 0))
        name_size, name_height = draw.textsize(member.name, font=self.font)
        sz = 33
        font = self.font
        while name_size > target_width and sz > 4:
            sz -= 1
            font = _font(sz)
            name_size, name_height = draw.textsize(member.name, font=font)
        draw.text((587 - name_size / 2, 162 - name_height / 2), text=member.name, font=font,
                  fill=(0, 0, 0))

        av_url = member.avatar_url_as(format="png", size=128)
        av_buf = io.BytesIO()
        await av_url.save(av_buf)
        av_buf.seek(0)
        av_img = PIL.Image.open(av_buf).convert("RGBA")
        av_img = av_img.resize((83, 83))

        av_fg_img = PIL.Image.new("RGBA", self.simp_img.size)
        av_fg_img.paste(av_img, (430, 384))
        av_fg_img.putalpha(self.av_mask)

        img_copy = PIL.Image.alpha_composite(img_copy, av_fg_img)

        buf = io.BytesIO()
        img_copy.save(buf, "png")
        await ctx.embed(image=buf)


def setup(bot: aoi.AoiBot) -> None:
    bot.add_cog(Fun(bot))
