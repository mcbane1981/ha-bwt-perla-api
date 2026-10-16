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

class BWTPerlaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            ip = user_input[CONF_IP_ADDRESS]
            code = user_input[CONF_LOGIN_CODE]

            try:
                auth = aiohttp.BasicAuth("user", code)
                url = f"http://{ip}:{DEFAULT_PORT}{API_ENDPOINT}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, auth=auth, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if isinstance(data, dict):
                                return self.async_create_entry(
                                    title=f"BWT Perla ({ip})",
                                    data=user_input,
                                )
                            errors["base"] = "invalid_auth"
                        elif resp.status in (401, 403):
                            errors["base"] = "invalid_auth"
                        else:
                            errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_LOGIN_CODE): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): cv.positive_int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
