import typing
from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import BorshPubkey
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey

from ..program_id import PROGRAM_ID


class UserStatsJSON(typing.TypedDict):
    owner: str
    asset: str
    level: int
    created_at: int
    last_active: int
    total_games: int
    total_moon: int
    total_doom: int
    total_correct_moon: int
    total_correct_doom: int
    total_prediction_funds: int
    total_winnings: int
    bump: int


@dataclass
class UserStats:
    discriminator: typing.ClassVar = b"\xb0\xdf\x88\x1bzO \xe3"
    layout: typing.ClassVar = borsh.CStruct(
        "owner" / BorshPubkey,
        "asset" / BorshPubkey,
        "level" / borsh.U8,
        "created_at" / borsh.U64,
        "last_active" / borsh.U64,
        "total_games" / borsh.U64,
        "total_moon" / borsh.U64,
        "total_doom" / borsh.U64,
        "total_correct_moon" / borsh.U64,
        "total_correct_doom" / borsh.U64,
        "total_prediction_funds" / borsh.U64,
        "total_winnings" / borsh.U64,
        "bump" / borsh.U8,
    )
    owner: Pubkey
    asset: Pubkey
    level: int
    created_at: int
    last_active: int
    total_games: int
    total_moon: int
    total_doom: int
    total_correct_moon: int
    total_correct_doom: int
    total_prediction_funds: int
    total_winnings: int
    bump: int

    @classmethod
    async def fetch(
            cls,
            conn: AsyncClient,
            address: Pubkey,
            commitment: typing.Optional[Commitment] = None,
            program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["UserStats"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
            cls,
            conn: AsyncClient,
            addresses: list[Pubkey],
            commitment: typing.Optional[Commitment] = None,
            program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["UserStats"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["UserStats"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "UserStats":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = UserStats.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            owner=dec.owner,
            asset=dec.asset,
            level=dec.level,
            created_at=dec.created_at,
            last_active=dec.last_active,
            total_games=dec.total_games,
            total_moon=dec.total_moon,
            total_doom=dec.total_doom,
            total_correct_moon=dec.total_correct_moon,
            total_correct_doom=dec.total_correct_doom,
            total_prediction_funds=dec.total_prediction_funds,
            total_winnings=dec.total_winnings,
            bump=dec.bump,
        )

    def to_json(self) -> UserStatsJSON:
        return {
            "owner": str(self.owner),
            "asset": str(self.asset),
            "level": self.level,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "total_games": self.total_games,
            "total_moon": self.total_moon,
            "total_doom": self.total_doom,
            "total_correct_moon": self.total_correct_moon,
            "total_correct_doom": self.total_correct_doom,
            "total_prediction_funds": self.total_prediction_funds,
            "total_winnings": self.total_winnings,
            "bump": self.bump,
        }

    @classmethod
    def from_json(cls, obj: UserStatsJSON) -> "UserStats":
        return cls(
            owner=Pubkey.from_string(obj["owner"]),
            asset=Pubkey.from_string(obj["asset"]),
            level=obj["level"],
            created_at=obj["created_at"],
            last_active=obj["last_active"],
            total_games=obj["total_games"],
            total_moon=obj["total_moon"],
            total_doom=obj["total_doom"],
            total_correct_moon=obj["total_correct_moon"],
            total_correct_doom=obj["total_correct_doom"],
            total_prediction_funds=obj["total_prediction_funds"],
            total_winnings=obj["total_winnings"],
            bump=obj["bump"],
        )
