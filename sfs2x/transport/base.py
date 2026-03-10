from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Protocol
import hashlib

from sfs2x.core import Buffer, SFSObject, SFSArray
from sfs2x.protocol import Message, decode, encode, Room, SysAction, ControllerID

class Transport(ABC):
    """Abstract base class for transports."""

    _closed: bool
    _compress_threshold: int | None = None
    _encryption_key: bytes | None = None

    def __init__(self) -> None:
        self._closed = True

    async def open(self) -> "Transport":
        await self._open()
        self._closed = False
        return self

    async def send(self, msg: Message) -> None:
        if self._closed:
            err_msg = "Connection closed by remote host"
            raise ConnectionError(err_msg)
        await self._send_raw(
            encode(msg, compress_threshold=self._compress_threshold, encryption_key=self._encryption_key))

    async def recv(self) -> Message:
        if self._closed:
            msg = "Connection closed by remote host"
            raise ConnectionError(msg)
        raw = await self._recv_raw()
        return decode(Buffer(raw), encryption_key=self._encryption_key)

    async def close(self) -> None:
        if not self._closed:
            await self._close_impl()
            self._closed = True

    async def listen(self) -> AsyncIterator[Message]:
        while not self._closed:
            try:
                msg = await self.recv()
                handled = await self._handle_system(msg)
                if not handled:
                    yield msg
                yield msg
            except (ConnectionError, RuntimeError):
                break
    async def _handle_system(self, message: Message) -> bool:
        payload = message.payload
        if message.action == SysAction.HANDSHAKE:
            token = hashlib.md5(self.host().encode()).hexdigest()
    
            session_info = SFSObject()
            session_info.put_int("ct", 1000000)
            session_info.put_int("ms", 8000000)
            session_info.put_utf_string("tk", token)
    
            await self.send(Message(
                controller=ControllerID.SYSTEM,
                action=SysAction.HANDSHAKE,
                payload=session_info
            ))
    
            return True
        elif message.action == SysAction.LOGIN:
            login = SFSObject()
            login.put_short("rs", 0)
            login.put_utf_string("zn", self.zone_name)
            login.put_utf_string("un", payload.get("un"))
            login.put_short("pi", 0)

            NewRoom = Room(room_id=0, name="Limbo", room_type="default", is_hidden=False, 
                    is_password_protected=True, is_game=False, min_players=0, max_players=self.max_players)

            RoomArrays = SFSArray()
            RoomArrays.add_sfs_array(NewRoom.to_sfs_array())

            login.put_sfs_array("rl", RoomArrays)

            await self.send(Message(
                controller=ControllerID.SYSTEM,
                action=SysAction.LOGIN,
                payload=login
            ))
    
        return False

    async def __aenter__(self) -> "Transport":
        """Async enter."""
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """Async exit."""
        await self.close()

    @abstractmethod
    async def _open(self) -> None:
        ...

    @abstractmethod
    async def _send_raw(self, raw: bytes) -> None:
        ...

    @abstractmethod
    async def _recv_raw(self) -> bytes:
        ...

    @abstractmethod
    async def _close_impl(self) -> None:
        ...

    @abstractmethod
    def host(self) -> str:
        ...

    @abstractmethod
    def port(self) -> int:
        ...


class Acceptor(Protocol):
    """Async listener for server."""

    async def __aiter__(self) -> AsyncIterator[Transport]: ...  # noqa: D105
