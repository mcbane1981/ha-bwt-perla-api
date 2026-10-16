from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

# BWT Fehler-ID Übersetzung (gemäß BWT-Dokumentation Kapitel 4)
ERROR_MAPPING = {
    "1": "Motor / Ventil 1 Fehler",
    "2": "Motor / Ventil 2 Fehler",
    "3": "Verschneidemotor Fehler",
    "5": "Regeneriermittel demnächst leer (<= 20 %)",
    "8": "Überstrom Motor / Ventil 1",
    "9": "Überstrom Motor / Ventil 2",
    "10": "Überstrom Motor / Ventil 3",
    "12": "Überstrom Magnetventil",
    "13": "AQA Stop Volume überschritten",
    "14": "AQA Stop Bodensensor ausgelöst",
    "15": "AQA Watch Schleichwasser erkannt",
    "16": "Leitungsdruck abgesunken",
    "21": "Kolben 1 / 2 Position undefiniert",
    "22": "Fehler interne Elektronik",
    "25": "Regeneriermittelvolumen nicht erreicht",
    "26": "AQA Guard Funk-Bodensensor ausgelöst",
    "27": "Regeneriermittel leer (0 %)",
    "32": "Routinemäßige Wartung fällig",
    "33": "Inspektion fällig",
    "34": "Expertwartung fällig",
    "35": "Mineralstoffbehälter demnächst leer",
    "36": "Mineralstoffbehälter leer",
    "43": "Ventil Überstrom",
    "44": "Ventil Überstrom",
    "45": "Ventil Dosierpumpe Überstrom",
    "46": "Fehler Ventilkugelhahn",
    "54": "Wasserzähler zählt nicht",
    "55": "Regenerationsablauf gestört",
    "56": "Fehler Initialisierung PCB 1.0",
    "57": "Fehler Initialisierung PCB 1.1",
    "58": "Motor 1 verfahren",
    "59": "Motor 2 verfahren",
    "61": "Leitfähigkeit zu hoch",
    "62": "Leitfähigkeit Grenze 1",
    "63": "Leitfähigkeit Grenze 2",
    "64": "Leitfähigkeit Grenze Wasser",
    "65": "Keine Sole verfügbar / Keine Funktion",
    "66": "Keine Verbindung zum Temperatursensor",
    "67": "Temperatur zu hoch",
    "68": "Kugelhahn reagiert nicht",
    "74": "Filter wechseln/spülen",
    "75": "Sole nicht gesättigt",
    "88": "Dosierpumpe gestört",
}

SHORT_ERROR_MAPPING = {
    "1": "Ventil 1",
    "2": "Ventil 2",
    "3": "Verschneidemotor",
    "5": "Salz <= 20%",
    "8": "Überstrom V1",
    "9": "Überstrom V2",
    "10": "Überstrom V3",
    "12": "Überstrom MV",
    "13": "AQA Volume",
    "14": "Bodensensor",
    "15": "Schleichwasser",
    "16": "Druckabfall",
    "21": "Kolbenposition",
    "22": "Elektronik",
    "25": "Sole-Volumen",
    "26": "AQA Guard Funk",
    "27": "Salz 0%",
    "32": "Wartung fällig",
    "33": "Inspektion",
    "34": "Expertwartung",
    "35": "Dosierung fast leer",
    "36": "Dosierung leer",
    "43": "Überstrom MV",
    "44": "Überstrom MV",
    "45": "Überstrom Pumpe",
    "46": "Kugelhahn",
    "54": "Zähler blockiert",
    "55": "Regen. gestört",
    "56": "PCB 1.0 Fehler",
    "57": "PCB 1.1 Fehler",
    "58": "Motor 1 Pos.",
    "59": "Motor 2 Pos.",
    "61": "Leitfähigkeit hoch",
    "62": "Leitfähigkeit G1",
    "63": "Leitfähigkeit G2",
    "64": "Leitfähigkeit Wasser",
    "65": "Keine Sole",
    "66": "Temp.-Sensor",
    "67": "Temp. zu hoch",
    "68": "Kugelhahn",
    "74": "Filter spülen",
    "75": "Sole ungesättigt",
    "88": "Pumpe gestört",
}

def parse_error_ids_to_text(raw_ids):
    if not raw_ids or str(raw_ids).strip() in ("", "0", "None", "null"):
        return "Keine Störung"
    ids = [i.strip() for i in str(raw_ids).split(",") if i.strip()]
    translated = [ERROR_MAPPING.get(i, f"Unbekannter Fehler (ID {i})") for i in ids]
    return "; ".join(translated) if translated else "Keine Störung"

def parse_error_ids_to_short_text(raw_ids):
    if not raw_ids or str(raw_ids).strip() in ("", "0", "None", "null"):
        return "OK"
    ids = [i.strip() for i in str(raw_ids).split(",") if i.strip()]
    translated = [SHORT_ERROR_MAPPING.get(i, f"Fehler {i}") for i in ids]
    if not translated:
        return "OK"
    if len(translated) == 1:
        return translated[0]
    return f"{translated[0]} (+{len(translated) - 1})"


SENSOR_TYPES = [
    # Status & Diagnose
    {
        "key": "ActiveErrorIDs",
        "name": "Fehlermeldung",
        "icon": "mdi:alert-circle",
        "value_fn": parse_error_ids_to_text,
    },
    {
        "key": "ActiveErrorIDs",
        "name": "Fehler Kurztext",
        "unique_suffix": "_short",
        "icon": "mdi:alert-circle-check-outline",
        "value_fn": parse_error_ids_to_short_text,
    },
    {
        "key": "ActiveErrorIDs",
        "name": "Aktive Fehler-IDs",
        "unique_suffix": "_raw",
        "icon": "mdi:alert-circle-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "value_fn": lambda v: v if v and str(v).strip() != "" else "Keine",
    },
    {
        "key": "ShowError",
        "name": "Status",
        "icon": "mdi:water-boiler",
        "value_fn": lambda v: {0: "Betriebsbereit (OK)", 1: "Warnung", 2: "Fehler"}.get(v, f"Unbekannt ({v})"),
    },
    {
        "key": "OutOfService",
        "name": "Außer Betrieb",
        "icon": "mdi:power-plug-off",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "value_fn": lambda v: "Ja" if v == 1 else "Nein",
    },
    {
        "key": "HolidayModeStartTime",
        "name": "Urlaubsmodus Status",
        "icon": "mdi:airplane",
        "value_fn": lambda v: "Deaktiviert" if v in (0, -1) else ("Aktiviert" if v == 1 else f"Start bei Unix {v}"),
    },
    {
        "key": "FirmwareVersion",
        "name": "Firmware Version",
        "icon": "mdi:information-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },

    # Salz & Regeneriermittel
    {
        "key": "RegenerativLevel",
        "name": "Salz Füllstand",
        "unit": "%",
        "icon": "mdi:salt-container",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "RegenerativRemainingDays",
        "name": "Salz Verbleibende Tage",
        "unit": "Tage",
        "icon": "mdi:calendar-clock",
    },
    {
        "key": "RegenerativSinceSetup_g",
        "name": "Salzverbrauch seit Inbetriebnahme",
        "unit": "g",
        "icon": "mdi:weight-gram",
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },

    # Durchfluss & Kapazität
    {
        "key": "CurrentFlowrate_l_h",
        "name": "Aktueller Durchfluss",
        "unit": "L/h",
        "icon": "mdi:water-pump",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "CapacityColumn1_ml_dH",
        "name": "Restkapazität Säule 1",
        "unit": "ml*°dH",
        "icon": "mdi:gauge",
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "key": "CapacityColumn2_ml_dH",
        "name": "Restkapazität Säule 2",
        "unit": "ml*°dH",
        "icon": "mdi:gauge",
        "state_class": SensorStateClass.MEASUREMENT,
    },

    # Wasserverbrauch
    {
        "key": "WaterTreatedCurrentDay_l",
        "name": "Aufbereitetes Wasser Heute",
        "unit": "L",
        "icon": "mdi:water",
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "key": "WaterTreatedCurrentMonth_l",
        "name": "Aufbereitetes Wasser Monat",
        "unit": "L",
        "icon": "mdi:water-calendar",
        "device_class": SensorDeviceClass.WATER,
    },
    {
        "key": "WaterTreatedCurrentYear_l",
        "name": "Aufbereitetes Wasser Jahr",
        "unit": "L",
        "icon": "mdi:water-sync",
        "device_class": SensorDeviceClass.WATER,
    },
    {
        "key": "WaterSinceSetup_l",
        "name": "Ausgangswasser seit Inbetriebnahme",
        "unit": "L",
        "icon": "mdi:counter",
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "key": "BlendedWaterSinceSetup_l",
        "name": "Verschneitwasser seit Inbetriebnahme",
        "unit": "L",
        "icon": "mdi:water-plus",
        "device_class": SensorDeviceClass.WATER,
    },
    {
        "key": "DosingSinceSetup_ml",
        "name": "Dosiermittel seit Inbetriebnahme",
        "unit": "ml",
        "icon": "mdi:cup-water",
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },

    # Eingangswasserhärte
    {
        "key": "HardnessIN_dH",
        "name": "Eingangshärte °dH",
        "unit": "°dH",
        "icon": "mdi:water-hardness",
    },
    {
        "key": "HardnessIN_fH",
        "name": "Eingangshärte °fH",
        "unit": "°fH",
        "icon": "mdi:water-hardness",
    },
    {
        "key": "HardnessIN_CaCO3",
        "name": "Eingangshärte ppm CaCO3",
        "unit": "ppm",
        "icon": "mdi:water-hardness",
    },
    {
        "key": "HardnessIN_mmol_l",
        "name": "Eingangshärte mmol/L",
        "unit": "mmol/L",
        "icon": "mdi:water-hardness",
    },

    # Ausgangswasserhärte
    {
        "key": "HardnessOUT_dH",
        "name": "Ausgangshärte °dH",
        "unit": "°dH",
        "icon": "mdi:water-hardness-line",
    },
    {
        "key": "HardnessOUT_fH",
        "name": "Ausgangshärte °fH",
        "unit": "°fH",
        "icon": "mdi:water-hardness-line",
    },
    {
        "key": "HardnessOUT_CaCO3",
        "name": "Ausgangshärte ppm CaCO3",
        "unit": "ppm",
        "icon": "mdi:water-hardness-line",
    },
    {
        "key": "HardnessOUT_mmol_l",
        "name": "Ausgangshärte mmol/L",
        "unit": "mmol/L",
        "icon": "mdi:water-hardness-line",
    },

    # Regeneration & Zähler
    {
        "key": "RegenerationCountSinceSetup",
        "name": "Regenerationen Gesamt",
        "icon": "mdi:refresh",
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "key": "RegenerationCounterColumn1",
        "name": "Regenerationen Säule 1",
        "icon": "mdi:refresh",
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "key": "RegenerationCounterColumn2",
        "name": "Regenerationen Säule 2",
        "icon": "mdi:refresh",
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "key": "LastRegenerationColumn1",
        "name": "Letzte Regeneration Säule 1",
        "icon": "mdi:clock-check-outline",
    },
    {
        "key": "LastRegenerationColumn2",
        "name": "Letzte Regeneration Säule 2",
        "icon": "mdi:clock-check-outline",
    },

    # Wartung
    {
        "key": "LastServiceCustomer",
        "name": "Letzte Routinewartung",
        "icon": "mdi:account-wrench-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
    {
        "key": "LastServiceTechnican",
        "name": "Letzte Expertwartung",
        "icon": "mdi:wrench-outline",
        "entity_category": EntityCategory.DIAGNOSTIC,
    },
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        BWTPerlaSensor(coordinator, entry, sensor_def)
        for sensor_def in SENSOR_TYPES
    ]
    async_add_entities(entities)

class BWTPerlaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, sensor_def):
        super().__init__(coordinator)
        self._key = sensor_def["key"]
        self._value_fn = sensor_def.get("value_fn")
        suffix = sensor_def.get("unique_suffix", "")
        
        self._attr_name = f"BWT Perla {sensor_def['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{self._key}{suffix}"
        self._attr_native_unit_of_measurement = sensor_def.get("unit")
        self._attr_icon = sensor_def.get("icon")
        self._attr_device_class = sensor_def.get("device_class")
        self._attr_state_class = sensor_def.get("state_class")
        self._attr_entity_category = sensor_def.get("entity_category")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get(self._key)
        if self._value_fn:
            return self._value_fn(val)
        return val

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "BWT Perla Wasserenthärtung",
            "manufacturer": "BWT",
            "model": "Perla / Rondomat Duo",
            "sw_version": str(self.coordinator.data.get("FirmwareVersion")) if self.coordinator.data else None,
        }
