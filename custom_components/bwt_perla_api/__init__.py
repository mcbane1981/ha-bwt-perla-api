from datetime import timedelta
import logging
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_IP_ADDRESS,
    CONF_LOGIN_CODE,
    CONF_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_PORT,
    API_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ip = entry.data[CONF_IP_ADDRESS]
    code = entry.data[CONF_LOGIN_CODE]
    interval = entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)

    async def async_update_data():
        url = f"http://{ip}:{DEFAULT_PORT}{API_ENDPOINT}"
        auth = aiohttp.BasicAuth("user", code)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=auth, timeout=10) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP Fehler {resp.status} beim Abruf von {url}")
                    return await resp.json(content_type=None)
        except Exception as err:
            raise UpdateFailed(f"Verbindungsfehler zur BWT Perla ({ip}): {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"BWT Perla ({ip})",
        update_method=async_update_data,
        update_interval=timedelta(seconds=interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
