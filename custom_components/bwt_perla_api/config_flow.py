import asyncio
import logging
import voluptuous as vol
import aiohttp
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

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

class BWTPerlaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        error_placeholders = {}

        if user_input is not None:
            raw_ip = user_input[CONF_IP_ADDRESS].strip()
            clean_ip = (
                raw_ip.replace("http://", "")
                .replace("https://", "")
                .split(":")[0]
                .split("/")[0]
            )
            code = user_input[CONF_LOGIN_CODE].strip()
            user_input[CONF_IP_ADDRESS] = clean_ip

            try:
                auth = aiohttp.BasicAuth("user", code)
                url = f"http://{clean_ip}:{DEFAULT_PORT}{API_ENDPOINT}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, auth=auth, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if isinstance(data, dict):
                                return self.async_create_entry(
                                    title=f"BWT Perla ({clean_ip})",
                                    data=user_input,
                                )
                            errors["base"] = "invalid_auth"
                        elif resp.status in (401, 403):
                            errors["base"] = "invalid_auth"
                        else:
                            errors["base"] = "cannot_connect"
                            error_placeholders["reason"] = f"HTTP Status {resp.status}"

            except asyncio.TimeoutError:
                errors["base"] = "cannot_connect"
                error_placeholders["reason"] = "Zeitüberschreitung (Timeout)"

            except aiohttp.ClientResponseError as err:
                errors["base"] = "cannot_connect"
                error_placeholders["reason"] = f"HTTP Fehler {err.status}"

            except aiohttp.ClientConnectorError as err:
                errors["base"] = "cannot_connect"
                # Unterteilung in Verbindungsabbruch vs. falscher Host
                if "refused" in str(err).lower():
                    error_placeholders["reason"] = "Port 8080 abgelehnt"
                elif "cannot connect to host" in str(err).lower():
                    error_placeholders["reason"] = "IP nicht erreichbar"
                else:
                    error_placeholders["reason"] = "Netzwerkfehler"

            except Exception as err:
                _LOGGER.exception("Unerwarteter Fehler bei BWT Perla Anbindung: %s", err)
                errors["base"] = "cannot_connect"
                # Kurze Fehlerzusammenfassung für unvorhergesehene Ausnahmen
                error_placeholders["reason"] = str(err)[:40]

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_LOGIN_CODE): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): cv.positive_int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders=error_placeholders,
        )
