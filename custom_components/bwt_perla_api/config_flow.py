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
                _LOGGER.debug("Starte Verbindungsprüfung zu BWT Perla: %s", url)

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, auth=auth, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json(content_type=None)
                            if isinstance(data, dict):
                                _LOGGER.info("Erfolgreich mit BWT Perla unter %s verbunden", clean_ip)
                                return self.async_create_entry(
                                    title=f"BWT Perla ({clean_ip})",
                                    data=user_input,
                                )
                            _LOGGER.error("BWT Perla API (%s) lieferte ungültiges Datenformat (kein JSON-Dict)", clean_ip)
                            errors["base"] = "invalid_auth"
                        elif resp.status in (401, 403):
                            _LOGGER.warning("BWT Perla API Authentifizierung fehlgeschlagen für IP %s (HTTP Status %s)", clean_ip, resp.status)
                            errors["base"] = "invalid_auth"
                        else:
                            _LOGGER.error("BWT Perla API (%s) antwortete mit unerwartetem HTTP Status %s", clean_ip, resp.status)
                            errors["base"] = "cannot_connect"
                            error_placeholders["reason"] = f"HTTP Status {resp.status}"

            except asyncio.TimeoutError:
                _LOGGER.error("Zeitüberschreitung (Timeout) beim Aufruf von http://%s:%s%s", clean_ip, DEFAULT_PORT, API_ENDPOINT)
                errors["base"] = "cannot_connect"
                error_placeholders["reason"] = "Zeitüberschreitung (Timeout)"

            except aiohttp.ClientResponseError as err:
                _LOGGER.error("HTTP-Antwortfehler bei BWT Perla (%s): Status %s - %s", clean_ip, err.status, err.message)
                errors["base"] = "cannot_connect"
                error_placeholders["reason"] = f"HTTP Fehler {err.status}"

            except aiohttp.ClientConnectorError as err:
                _LOGGER.error("Verbindungsfehler zu BWT Perla (%s:%s): %s", clean_ip, DEFAULT_PORT, err)
                errors["base"] = "cannot_connect"
                if "refused" in str(err).lower():
                    error_placeholders["reason"] = "Port 8080 abgelehnt"
                elif "cannot connect to host" in str(err).lower():
                    error_placeholders["reason"] = "IP nicht erreichbar"
                else:
                    error_placeholders["reason"] = "Netzwerkfehler"

            except Exception as err:
                _LOGGER.exception("Unerwarteter Fehler bei der BWT Perla Einrichtung (%s): %s", clean_ip, err)
                errors["base"] = "cannot_connect"
                error_placeholders["reason"] = str(err)[:40]

            # Garantierter Fallback für den Übersetzungsplatzhalter
            if "base" in errors and errors["base"] == "cannot_connect" and "reason" not in error_placeholders:
                error_placeholders["reason"] = "Unbekannter Netzwerkfehler"

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
